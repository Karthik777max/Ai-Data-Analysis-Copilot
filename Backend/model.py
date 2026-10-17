"""Gemini Interactions API integration with the project's local MCP server."""

import asyncio
import json
import os
import sys
from pathlib import Path

from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_INSTRUCTIONS = (
    "You are a helpful general-purpose assistant for this analytics workspace. "
    "Answer general questions, frequently asked questions, and questions about "
    "using the app directly from your knowledge. Use the PostgreSQL tools only "
    "when the user asks about their data or a database fact. For database "
    "questions, inspect the available tables and columns before querying. Explain "
    "results clearly, say when you are unsure, and never claim a query succeeded "
    "if a tool returned an error. The database tools are read-only."
)
MAX_TOOL_ROUNDS = 6
DATABASE_TOOL_NAMES = {
    "list_database_tables",
    "describe_database_table",
    "run_read_only_query",
}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER_PATH = PROJECT_ROOT / "mcp_server" / "server.py"


def _setting(name, default=None):
    """Read a setting from the environment, falling back to Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name, default)
    except (ImportError, FileNotFoundError):
        return default


def _gemini_api_key():
    """Prefer the key just configured in Streamlit secrets over a stale env key."""
    try:
        import streamlit as st

        secret_key = st.secrets.get("GEMINI_API_KEY")
        if secret_key:
            return secret_key
    except (ImportError, FileNotFoundError):
        pass
    return os.getenv("GEMINI_API_KEY")


def _tool_definitions(mcp_tools):
    """Convert the PostgreSQL tools advertised by MCP to Gemini function declarations."""
    definitions = []
    for tool in mcp_tools:
        if tool.name not in DATABASE_TOOL_NAMES:
            continue
        definitions.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description or tool.name,
            "parameters": tool.inputSchema or {"type": "object", "properties": {}},
        })
    return definitions


def _tool_output(result):
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return json.dumps(structured, default=str)
    blocks = []
    for block in getattr(result, "content", []):
        block_text = getattr(block, "text", None)
        blocks.append(block_text if block_text is not None else str(block))
    return "\n".join(blocks) or "Tool completed without a result."


async def _ask_with_mcp(client, question, instructions, model):
    database_url = _setting("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Add it to the environment or "
            ".streamlit/secrets.toml."
        )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_PATH)],
        env={**os.environ, "DATABASE_URL": database_url},
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed_tools = await session.list_tools()
            tools = _tool_definitions(listed_tools.tools)
            if not tools:
                raise RuntimeError("The MCP server did not provide PostgreSQL tools.")

            # Keep the interaction stateless so Gemini does not retain this
            # database conversation as a stored Interaction resource.
            history = [{
                "type": "user_input",
                "content": [{"type": "text", "text": question}],
            }]

            for round_number in range(MAX_TOOL_ROUNDS + 1):
                interaction = client.interactions.create(
                    model=model,
                    input=history,
                    tools=tools,
                    system_instruction=instructions,
                    store=False,
                )
                calls = [step for step in interaction.steps if step.type == "function_call"]
                if not calls:
                    return interaction.output_text or "Gemini returned no text response."
                if round_number == MAX_TOOL_ROUNDS:
                    break

                # Gemini requires its model steps to be included in order before
                # the function results are returned on the next stateless turn.
                history.extend(step.model_dump() for step in interaction.steps)
                for call in calls:
                    if call.name not in DATABASE_TOOL_NAMES:
                        output = json.dumps({"error": "Tool is not allowed."})
                    else:
                        try:
                            arguments = call.arguments or {}
                            result = await session.call_tool(call.name, arguments=arguments)
                            output = _tool_output(result)
                            if getattr(result, "isError", False):
                                output = json.dumps({"error": output})
                        except Exception as error:
                            output = json.dumps({"error": str(error)})

                    history.append({
                        "type": "function_result",
                        "name": call.name,
                        "call_id": call.id,
                        "result": [{"type": "text", "text": output}],
                    })

            return "I couldn't finish the database request within the tool-call limit."


def ask_llm(question, *, instructions=DEFAULT_INSTRUCTIONS, model=None):
    """Answer a question through Gemini, using read-only PostgreSQL MCP tools.

    Configure GEMINI_API_KEY and DATABASE_URL in the environment or
    .streamlit/secrets.toml. GEMINI_MODEL is optional and defaults to
    gemini-3.8-flash.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string.")

    api_key = _gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Set GEMINI_API_KEY in the "
            "environment or .streamlit/secrets.toml."
        )

    selected_model = model or _setting("GEMINI_MODEL", DEFAULT_MODEL)
    client = genai.Client(api_key=api_key)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.run(
                _ask_with_mcp(client, question.strip(), instructions, selected_model)
            )
        except BaseExceptionGroup as group:
            leaves = []

            def collect_leaves(error):
                nested = getattr(error, "exceptions", None)
                if nested:
                    for child in nested:
                        collect_leaves(child)
                else:
                    leaves.append(error)

            collect_leaves(group)
            if len(leaves) == 1:
                raise leaves[0] from None
            raise
    raise RuntimeError("ask_llm() cannot run inside an active asyncio event loop.")
