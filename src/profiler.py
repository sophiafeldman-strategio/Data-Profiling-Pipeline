from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame

user = "Sophia Feldman"
company_name = "Strategio"
client_name = "Meridian Capital"
IMPORTANT_COLUMNS = ["trade_id", "instrument_id", "trade_date", "quantity", "price"]
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


def _none_mask(series: pd.Series) -> pd.Series:
    """ Helper function: builds a yes/no column(series) for null values, returns True when cell contains a None value 
    Args: Pandas Series
    Returns: Pandas Series (yes/no for null values)
    """
    return pd.Series([value is None for value in series], index=series.index)


def _blank_mask(series: pd.Series) -> pd.Series:
    """ Helper function: builds a yes/no column(series) for blank values, returns True when cell contains an empty string
    Args: Pandas Series
    Returns: Pandas Series (yes/no for blank values)
    """
    if series.dtype != object:
        return pd.Series(False, index=series.index) # numeric columns cannot be blank
    return series.notna() & series.astype(str).str.strip().eq("") # text columns can be blank, strip whitespace and check for empty string (true when equal to "" & cell is present)


def _empty_counts(series: pd.Series) -> tuple[int, int, int]:
    """ Helper function: count the number of none_mask, _blank_mask and isna values in a series.
    Args: Pandas Series
    Returns: tuple of ints for na, none, blank counts """
    none = _none_mask(series)
    na = series.isna() & ~none # na only, NOT none  (isna true for none and NaN)
    return int(na.sum()), int(none.sum()), int(_blank_mask(series).sum()) # returns the sum of na, none and blank values in a series


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

    # Initialize the NA, None, and blank totals. Numeric columns show min and max; other columns show a unique count.
    na_total = none_total = blank_total = 0
    column_rows = []
    for column in df.columns:
        na_count, none_count, blank_count = _empty_counts(df[column])
        na_total += na_count
        none_total += none_count
        blank_total += blank_count
        if column in ranges.index:
            low = ranges.loc[column, "min"]
            high = ranges.loc[column, "max"]
            values = f"{low:g} to {high:g}"
        else:
            values = f"{df[column].nunique(dropna=True)} unique"
        column_rows.append(
            f"| {column} | {df[column].dtype} | {na_count} | {none_count} | {blank_count} | {values} |"
        )

    # Build the summary table for the dataframe
    summary_table = "\n".join(
        [
            "| Column | Type | NA | Null | Blank | Values |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            *column_rows,
        ]
    )

    # Initialize, then count missing rows for each required column.
    missing_rows = [] # list count of missing rows for each column
    incomplete_masks = [] # list: the boolean mask for each column
    for column in IMPORTANT_COLUMNS:
        na_count, none_count, blank_count = _empty_counts(df[column])
        empty = df[column].isna() | _none_mask(df[column]) | _blank_mask(df[column])
        incomplete_masks.append(empty)
        missing_rows.append(
            f"| {column} | {na_count} | {none_count} | {blank_count} | {_percent(int(empty.sum()), row_count)} |"
        )
    incomplete_rows = int(pd.concat(incomplete_masks, axis=1).any(axis=1).sum())

    missing_table = "\n".join(
        [
            "| Column | NA | Null | Blank | Share of rows empty |",
            "| --- | ---: | ---: | ---: | ---: |",
            *missing_rows,
            f"| Any of these columns |  |  |  | {_percent(incomplete_rows, row_count)} |",
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
| NA cells | {na_total} |
| Null cells | {none_total} |
| Blank strings | {blank_total} |

{summary_table}

## Missing values in required trade fields

NA is a pandas missing value. Null is a Python None. Blank is an empty string. A row is incomplete when any required field is one of the three.

{missing_table}

## Invalid prices

Prices at or below zero: {invalid_prices} ({_percent(invalid_prices, row_count)} of rows).

## Trade date formats

{len(dates)} non-empty dates. The two-digit patterns can be read as day-first or month-first, so they are counted separately from the ISO dates.

{date_table}

Repeated trade ids minus identical rows: {repeated_ids - duplicate_rows}. Those ids appear more than once, but the copies are not the same across every column.
"""
    output_path.write_text(report)
    return output_path
