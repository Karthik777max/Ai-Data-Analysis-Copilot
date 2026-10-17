"""Private MCP tools for inspecting CSV files and querying PostgreSQL."""

import os
from functools import lru_cache
from io import StringIO

import pandas as pd
from mcp.server.fastmcp import FastMCP
import sqlglot
from sqlglot import exp
from sqlalchemy import create_engine, inspect, text


mcp = FastMCP("DataAnalystCopilot")
MAX_QUERY_ROWS = 200
ALLOWED_SCHEMAS = {"public"}
EXCLUDED_TABLES = {"copilot_users", "copilot_logins", "copilot_uploads"}


@lru_cache(maxsize=1)
def _engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured for the MCP server.")
    return create_engine(database_url, pool_pre_ping=True)


def _visible_tables():
    inspector = inspect(_engine())
    return {
        (schema, table)
        for schema in ALLOWED_SCHEMAS
        for table in inspector.get_table_names(schema=schema)
        if table not in EXCLUDED_TABLES
    }


@mcp.tool()
def list_database_tables() -> list[dict]:
    """List tables in the public PostgreSQL schema that the copilot can inspect."""
    return [
        {"schema": schema, "table": table}
        for schema, table in sorted(_visible_tables())
    ]


@mcp.tool()
def describe_database_table(schema: str, table: str) -> dict:
    """Return column names and types for a visible PostgreSQL table."""
    if (schema, table) not in _visible_tables():
        raise ValueError("That table is not available to the copilot.")
    inspector = inspect(_engine())
    columns = inspector.get_columns(table, schema=schema)
    return {
        "schema": schema,
        "table": table,
        "columns": [
            {"name": column["name"], "type": str(column["type"]), "nullable": column["nullable"]}
            for column in columns
        ],
    }


@mcp.tool()
def run_read_only_query(sql: str, limit: int = 100) -> dict:
    """Run one read-only SELECT query against PostgreSQL and return at most 200 rows."""
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("Provide a SQL SELECT query.")
    if not 1 <= limit <= MAX_QUERY_ROWS:
        raise ValueError(f"Limit must be between 1 and {MAX_QUERY_ROWS}.")

    statement = sql.strip()
    if statement.endswith(";"):
        statement = statement[:-1].rstrip()
    if ";" in statement:
        raise ValueError("Only one SQL statement is allowed.")

    parsed_statements = sqlglot.parse(statement, read="postgres")
    if len(parsed_statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")
    parsed = parsed_statements[0]
    if parsed is None or parsed.key not in {"select", "union", "intersect", "except"}:
        raise ValueError("Only read-only SELECT queries are allowed.")

    cte_names = {
        cte.alias_or_name.casefold()
        for cte in parsed.find_all(exp.CTE)
    }
    allowed_tables = {table for _, table in _visible_tables()}
    for table_ref in parsed.find_all(exp.Table):
        if table_ref.name.casefold() in cte_names:
            continue
        schema = table_ref.db or "public"
        if schema not in ALLOWED_SCHEMAS or table_ref.name not in allowed_tables or table_ref.catalog:
            raise ValueError("Queries may only read available tables in the public schema.")

    engine = _engine()
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SET LOCAL statement_timeout = '10s'"))
            result = connection.execute(text(statement))
            columns = list(result.keys())
            rows = result.mappings().fetchmany(limit + 1)

    truncated = len(rows) > limit
    rows = rows[:limit]
    return {
        "columns": columns,
        "rows": [
            {key: (value if value is None or isinstance(value, (str, int, float, bool)) else str(value))
             for key, value in row.items()}
            for row in rows
        ],
        "row_count": len(rows),
        "truncated": truncated,
    }


@mcp.tool()
def inspect_dataset(csv_content: str) -> dict:
    """Inspect a CSV dataset and return its structure, data types, row count, and missing values."""
    df = pd.read_csv(StringIO(csv_content))
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(count) for col, count in df.isna().sum().items()},
    }


@mcp.tool()
def get_sample_rows(csv_content: str, limit: int = 5) -> list[dict]:
    """Return a small sample of rows from a CSV dataset."""
    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20.")
    df = pd.read_csv(StringIO(csv_content))
    return df.head(limit).fillna("").to_dict(orient="records")


if __name__ == "__main__":
    mcp.run()
