from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame

user = "Sophia Feldman"
company_name = "Strategio"
client_name = "Meridian Capital"
IMPORTANT_COLUMNS = ["trade_id", "instrument_id", "trade_date", "quantity", "price"]
ALLOWED_VALUES = {
    "instrument_type": {"Equity", "ETF", "Bond"},
    "trade_status": {"EXECUTED", "SETTLED", "CANCELLED", "PENDING", "REJECTED"},
}
DATE_PATTERNS = [
    ("YYYY-MM-DD", r"^\d{4}-\d{2}-\d{2}$"),
    ("YYYY.MM.DD", r"^\d{4}\.\d{2}\.\d{2}$"),
    ("DD-MM-YYYY or MM-DD-YYYY", r"^\d{2}-\d{2}-\d{4}$"),
    ("DD/MM/YYYY or MM/DD/YYYY", r"^\d{2}/\d{2}/\d{4}$"),
]


def _percent(count: int, total: int) -> str:
    """ Helper function: calculate percentage of total 
    Args: int (count of items)
    Returns: str (percentage of total)
    """
    if total == 0:
        return "0.0%"
    return f"{count / total:.1%}"


def _missing_mask(series: pd.Series) -> pd.Series:
    """True where a cell is missing or blank. NA, None, and empty text count as the same gap."""
    if series.dtype != object:
        return series.isna()
    blank = series.notna() & series.astype(str).str.strip().eq("")
    return series.isna() | blank


def invalid_category_count(series: pd.Series, allowed: set[str]) -> int:
    """Count non-empty values that are not in the allowed set."""
    present = series.dropna().astype(str).str.strip()
    present = present[present.ne("")]
    return int((~present.isin(allowed)).sum())


def summary_stats(df: DataFrame) -> Path:
    """Write a readable markdown profile of the dataframe.
    Args: Pandas DataFrame
    Returns: Path to output file (output/summary_stats.md)
    """
    output_path = Path("output/summary_stats.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = len(df)

    numeric = df.select_dtypes(include="number")
    ranges = numeric.agg(["min", "max"]).T if not numeric.empty else pd.DataFrame() #Transpose the result to get column names as index

    # Missing means NA, None, or blank text. Numeric columns show min and max; other columns show a unique count.
    missing_total = 0
    column_rows = []
    for column in df.columns:
        missing = _missing_mask(df[column])
        missing_count = int(missing.sum())
        missing_total += missing_count
        if column in ranges.index:
            low = ranges.loc[column, "min"]
            high = ranges.loc[column, "max"]
            values = f"{low:g} to {high:g}"
        else:
            values = f"{df.loc[~missing, column].nunique()} unique"
        column_rows.append(
            f"| {column} | {df[column].dtype} | {missing_count} | {values} |"
        )

    summary_table = "\n".join(
        [
            "| Column | Type | Missing | Values |",
            "| --- | --- | ---: | --- |",
            *column_rows,
        ]
    )

    missing_rows = []
    incomplete_masks = []
    for column in IMPORTANT_COLUMNS:
        missing = _missing_mask(df[column])
        missing_count = int(missing.sum())
        incomplete_masks.append(missing)
        missing_rows.append(
            f"| {column} | {missing_count} | {_percent(missing_count, row_count)} |"
        )
    incomplete_rows = int(pd.concat(incomplete_masks, axis=1).any(axis=1).sum())

    missing_table = "\n".join(
        [
            "| Column | Missing | Share of rows |",
            "| --- | ---: | ---: |",
            *missing_rows,
            f"| Any of these columns | {incomplete_rows} | {_percent(incomplete_rows, row_count)} |",
        ]
    )

    # Count invalid prices (equal to or below 0)
    invalid_prices = int(((df["price"].notna()) & (df["price"] <= 0)).sum()) if "price" in df else 0
    dates = df["trade_date"].dropna().astype(str).str.strip()
    dates = dates[dates.ne("")] # remove empty strings
    date_rows = []
    matched = pd.Series(False, index=dates.index)
    # Loop through date patterns to count the pattern types
    for label, pattern in DATE_PATTERNS:
        count = int(dates.str.match(pattern).sum())
        matched = matched | dates.str.match(pattern)
        date_rows.append(f"| {label} | {count} | {_percent(count, len(dates))} |")
    other_dates = int((~matched).sum())
    date_rows.append(f"| Other | {other_dates} | {_percent(other_dates, len(dates))} |")
    date_table = "\n".join(
        [
            "| Pattern | Count | Share of non-empty dates |",
            "| --- | ---: | ---: |",
            *date_rows,
        ]
    )
    allowed_rows = []
    for column, allowed in ALLOWED_VALUES.items():
        if column not in df:
            continue
        invalid = invalid_category_count(df[column], allowed)
        allowed_rows.append(
            f"| {column} | {', '.join(sorted(allowed))} | {invalid} | {_percent(invalid, row_count)} |"
        )
    allowed_table = "\n".join(
        [
            "| Column | Allowed values | Outside the list | Share of rows |",
            "| --- | --- | ---: | ---: |",
            *allowed_rows,
        ]
    )
    # Count repeated trade ids and duplicate rows
    repeated_ids = int(df["trade_id"].duplicated().sum()) if "trade_id" in df else 0
    duplicate_rows = int(df.duplicated().sum())

# Build the report markdown
    report = f"""# Data profile

Prepared: {datetime.now().strftime("%Y-%m-%d")}
Prepared by: {user}
Company Name: {company_name}
Prepared for client: {client_name}


| Metric | Value |
| --- | ---: |
| Records | {row_count} |
| Columns | {df.shape[1]} |
| Duplicate rows | {duplicate_rows} |
| Repeated trade ids | {repeated_ids} |
| Missing cells | {missing_total} |

{summary_table}

## Missing values in required trade fields

A cell is missing when it is empty or has no value. A row is incomplete when any required field is missing.

{missing_table}

## Invalid prices

Prices at or below zero: {invalid_prices} ({_percent(invalid_prices, row_count)} of rows).

## Trade date formats

{len(dates)} non-empty dates. The two-digit patterns can be read as day-first or month-first, so they are counted separately from the ISO dates.

{date_table}

## Values outside the allowed lists

{allowed_table}

Repeated trade ids minus identical rows: {repeated_ids - duplicate_rows}. Those ids appear more than once, but the copies are not the same across every column.
"""
    output_path.write_text(report)
    return output_path
