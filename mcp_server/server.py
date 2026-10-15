
import pandas as pd
from io import StringIO
from mcp.server.fastmcp import FastMCP
import mcp



mcp = FastMCP("DataAnalystCopilot")


@mcp.tool()
def inspect_dataset(csv_content: str) -> dict:
    """Inspect a CSV dataset and return its structure,
    data types, row count, and missing values."""

    df = pd.read_csv(StringIO(csv_content))

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "data_types": {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        },
        "missing_values": {
            col: int(count)
            for col, count in df.isna().sum().items()
        },
    }


@mcp.tool()
def get_sample_rows(csv_content: str, limit: int = 5) -> list[dict]:
    """Return a small sample of rows from a CSV dataset."""

    df = pd.read_csv(StringIO(csv_content))

    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20")

    return df.head(limit).fillna("").to_dict(orient="records")


if __name__ == "__main__":
    mcp.run()
