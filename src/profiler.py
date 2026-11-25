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
    if total == 0:
        return "0.0%"
    return f"{count / total:.1%}"


def _none_mask(series: pd.Series) -> pd.Series:
    return pd.Series([value is None for value in series], index=series.index)


def _blank_mask(series: pd.Series) -> pd.Series:
    if series.dtype != object:
        return pd.Series(False, index=series.index)
    return series.notna() & series.astype(str).str.strip().eq("")


def _empty_counts(series: pd.Series) -> tuple[int, int, int]:
    none = _none_mask(series)
    na = series.isna() & ~none
    return int(na.sum()), int(none.sum()), int(_blank_mask(series).sum())


def summary_stats(df: DataFrame) -> Path:
    """Write a readable markdown profile of the dataframe."""
    output_path = Path("output/summary_stats.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = len(df)

    numeric = df.select_dtypes(include="number")
    ranges = numeric.agg(["min", "max"]).T if not numeric.empty else pd.DataFrame()

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

    summary_table = "\n".join(
        [
            "| Column | Type | NA | Null | Blank | Values |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            *column_rows,
        ]
    )

    missing_rows = []
    incomplete_masks = []
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

    invalid_prices = int(((df["price"].notna()) & (df["price"] <= 0)).sum()) if "price" in df else 0
    dates = df["trade_date"].dropna().astype(str).str.strip()
    dates = dates[dates.ne("")]
    date_rows = []
    matched = pd.Series(False, index=dates.index)
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

    repeated_ids = int(df["trade_id"].duplicated().sum()) if "trade_id" in df else 0
    duplicate_rows = int(df.duplicated().sum())

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
