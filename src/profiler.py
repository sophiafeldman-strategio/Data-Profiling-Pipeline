from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame

user = "Sophia Feldman"
company_name = "Strategio"
client_name = "Meridian Capital"
REFERENCE_PATH = Path("data_info/meridian_reference_data.csv")
SCORE_THRESHOLD = 90
TRADE_WINDOW_START = "2025-01-01"
TRADE_WINDOW_END = "2026-06-30"
ALLOWED_VALUES = {
    "instrument_type": {"Equity", "ETF", "Bond"},
    "trade_status": {"EXECUTED", "SETTLED", "CANCELLED", "PENDING", "REJECTED"},
}
# 3 = the row cannot be used for analysis without this.
# 2 = the row still has a security and a price, but a date, a size, or a party is missing.
# 1 = only a label is wrong. The trade can still be identified and priced.
WEIGHT = {
    "trade_id": 3,
    "instrument_id": 3,
    "price": 3,
    "trade_date": 2,
    "quantity": 2,
    "buyer": 2,
    "seller": 2,
    "instrument_type": 1,
    "trade_status": 1,
}
WHY = {
    "trade_id": "A row with no trade id, or an id reused on another row, is not one trade you can count.",
    "instrument_id": "Without a known security, the row cannot be joined to the reference list or used in a price history.",
    "price": "Price is the value the analysis is about. Zero or negative is not a usable execution price.",
    "trade_date": "A date that is not YYYY-MM-DD inside 2025-01-01 to 2026-06-30 cannot sit on a timeline.",
    "quantity": "Size is needed for volume, and it is less damaging than a missing price.",
    "buyer": "A missing party blocks who traded. It does not block what the security was worth.",
    "seller": "Same as buyer: settlement needs a party, a price history does not.",
    "instrument_type": "Equity, ETF, or Bond is a label. The instrument id already names the security.",
    "trade_status": "Status is a label on a trade you can already identify.",
}
DATE_PATTERNS = [
    ("YYYY-MM-DD", r"^\d{4}-\d{2}-\d{2}$"),
    ("YYYY.MM.DD", r"^\d{4}\.\d{2}\.\d{2}$"),
    ("DD-MM-YYYY or MM-DD-YYYY", r"^\d{2}-\d{2}-\d{4}$"),
    ("DD/MM/YYYY or MM/DD/YYYY", r"^\d{2}/\d{2}/\d{4}$"),
]
CATEGORIES = ("completeness", "consistency", "accuracy", "timeliness", "validity")


def _percent(count: int, total: int) -> str:
    """Return count divided by total as a percent string, such as 8.8%.

    Args:
        count: Number of rows in the group.
        total: Number of rows in the file.
    """
    if total == 0:
        return "0.0%"
    return f"{count / total:.1%}"


def _missing_mask(series: pd.Series) -> pd.Series:
    """Mark cells that are empty.

    NA and blank text both count as missing. A numeric column only checks NA,
    because a number cannot be blank text.

    Args:
        series: One column from the blotter.
    Returns:
        True for each missing cell.
    """
    if series.dtype != object:
        return series.isna()
    blank = series.notna() & series.astype(str).str.strip().eq("")
    return series.isna() | blank


def invalid_category_count(series: pd.Series, allowed: set[str]) -> int:
    """Count filled-in values that are not on the allowed list.

    Blank cells are skipped. A blank instrument type is a missing value, not an
    illegal category.

    Args:
        series: One text column from the blotter.
        allowed: Values that column is allowed to hold.
    Returns:
        How many non-blank cells fall outside allowed.
    """
    present = series.dropna().astype(str).str.strip()
    present = present[present.ne("")]
    return int((~present.isin(allowed)).sum())


def load_reference(path: Path = REFERENCE_PATH) -> DataFrame:
    """Load the instrument master from the reference CSV.

    Each row is one security Meridian can trade. The score uses instrument_id
    and instrument_type from this file. The other columns (name, asset class,
    venue, issuer, currency, status) stay in the file for context.

    Args:
        path: Path to meridian_reference_data.csv.
    Returns:
        The reference table, with every column read as text.
    Raises:
        ValueError: The file has no instrument_id or instrument_type column.
    """
    reference = pd.read_csv(path, dtype=str)
    missing = {"instrument_id", "instrument_type"} - set(reference.columns)
    if missing:
        raise ValueError(f"Reference file is missing columns: {', '.join(sorted(missing))}")
    return reference


def _rate(passed: pd.Series) -> float:
    """Turn a pass/fail mask into a score from 0 to 100.

    Args:
        passed: True on each row that passed one check.
    Returns:
        The percent of rows that passed. An empty frame scores 0.
    """
    if len(passed) == 0:
        return 0.0
    return float(passed.mean() * 100)


def _weighted(checks: list[dict], category: str | None = None) -> float:
    """Average the check scores, using each check's field weight.

    A weight of 3 pulls the average more than a weight of 1. Pass category
    to score one data-quality category. Leave it out to score the whole file.

    Args:
        checks: Dicts with category, weight, and score keys.
        category: One of completeness, consistency, accuracy, timeliness, validity.
    Returns:
        The weighted average. Zero when there are no checks to average.
    """
    chosen = checks if category is None else [check for check in checks if check["category"] == category]
    total_weight = sum(check["weight"] for check in chosen)
    if total_weight == 0:
        return 0.0
    return sum(check["weight"] * check["score"] for check in chosen) / total_weight


def quality_scores(df: DataFrame, reference: DataFrame) -> dict:
    """Score the blotter. Each check is the share of rows that pass, then weighted.

    Weights live on the field, not on the five categories. The category score is the
    weighted average of its checks. The overall score is the weighted average of every check.
    A blank instrument id fails completeness only. A filled id that is not on the
    reference list fails validity. A known id with the wrong type fails consistency.

    Args:
        df: Combined trade blotter.
        reference: Instrument master from load_reference.
    Returns:
        Category scores, the weighted overall score, the check list, and the
        counts of unknown instrument ids and type mismatches.
    """
    # Split instrument ids into three groups before scoring them.
    blank_id = _missing_mask(df["instrument_id"])
    instrument = df["instrument_id"].astype(str).str.strip()
    ref_type = reference.set_index("instrument_id")["instrument_type"]
    known = ~blank_id & instrument.isin(ref_type.index)
    unknown = ~blank_id & ~instrument.isin(ref_type.index)
    # Only a known security can disagree with the reference type.
    type_mismatch = known & df["instrument_type"].astype(str).ne(instrument.map(ref_type))
    iso = df["trade_date"].astype(str).str.strip().str.match(r"^\d{4}-\d{2}-\d{2}$")
    parsed = pd.to_datetime(df["trade_date"], format="%Y-%m-%d", errors="coerce")
    # An exact copy matches another row on every column. A shared id with different
    # columns is a second trade, even when one of those rows is also a copy.
    exact_copy = df.duplicated(keep=False)
    distinct_rows = df.drop_duplicates()
    conflicting_ids = distinct_rows.loc[distinct_rows["trade_id"].duplicated(keep=False), "trade_id"]
    different_trade = df["trade_id"].isin(set(conflicting_ids))

    # Each check is a category, the field whose weight it uses, a label, and the rows that pass.
    rows = [
        ("completeness", "trade_id", "Does the row have a trade id?", ~_missing_mask(df["trade_id"])),
        ("completeness", "instrument_id", "Does the row have an instrument id?", ~blank_id),
        ("completeness", "buyer", "Does the row have a buyer?", ~_missing_mask(df["buyer"])),
        ("completeness", "seller", "Does the row have a seller?", ~_missing_mask(df["seller"])),
        ("accuracy", "price", "Is the price above zero?", df["price"].notna() & (df["price"] > 0)),
        ("accuracy", "quantity", "Is the quantity above zero?", df["quantity"].notna() & (df["quantity"] > 0)),
        ("timeliness", "trade_date", "Is the date YYYY-MM-DD and inside 2025-01-01 to 2026-06-30?", iso & parsed.between(TRADE_WINDOW_START, TRADE_WINDOW_END)),
        ("consistency", "trade_id", "Is this row the only copy of this exact trade?", ~exact_copy),
        ("consistency", "trade_id", "Does this trade id describe only one trade?", ~different_trade),
        ("consistency", "instrument_type", "Does the instrument type match the reference security?", ~type_mismatch),
        ("validity", "instrument_id", "Is a filled instrument id on the reference list?", ~unknown),
        ("validity", "instrument_type", "Is the instrument type Equity, ETF, or Bond?", df["instrument_type"].astype(str).isin(ALLOWED_VALUES["instrument_type"])),
        ("validity", "trade_status", "Is the trade status on the allowed list?", df["trade_status"].astype(str).isin(ALLOWED_VALUES["trade_status"])),
    ]
    checks = [
        {"category": category, "field": field, "check": label, "weight": WEIGHT[field], "score": _rate(passed)}
        for category, field, label, passed in rows
    ]
    scores = {category: _weighted(checks, category) for category in CATEGORIES}
    scores["overall"] = _weighted(checks)
    scores["checks"] = checks
    scores["unknown_instrument"] = int(unknown.sum())
    scores["type_mismatch"] = int(type_mismatch.sum())
    scores["exact_copy"] = int(exact_copy.sum())
    scores["different_trade"] = int(different_trade.sum())
    scores["below_threshold"] = [category for category in CATEGORIES if scores[category] < SCORE_THRESHOLD]
    return scores


def write_summary_stats(df: DataFrame, reference_path: Path = REFERENCE_PATH) -> Path:
    """Write the stakeholder profile and the column counts to output/summary_stats.md.

    The top of the file is the weighted score and the reason for each weight.
    The bottom is the same column profile as before: missing values, price
    range, date formats, and values outside the allowed lists.

    Args:
        df: Combined trade blotter.
        reference_path: Instrument master used to check instrument ids.
    Returns:
        Path of the written markdown file.
    """
    output_path = Path("output/summary_stats.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = len(df)
    reference = load_reference(reference_path)
    scores = quality_scores(df, reference)

    numeric = df.select_dtypes(include="number")
    ranges = numeric.agg(["min", "max"]).T if not numeric.empty else pd.DataFrame()
    missing_total = 0
    column_rows = []
    for column in df.columns:
        missing = _missing_mask(df[column])
        missing_count = int(missing.sum())
        missing_total += missing_count
        if column in ranges.index:
            values = f"{ranges.loc[column, 'min']:g} to {ranges.loc[column, 'max']:g}"
        else:
            values = f"{df.loc[~missing, column].nunique()} unique"
        column_rows.append(f"| {column} | {df[column].dtype} | {missing_count} | {values} |")

    dates = df["trade_date"].dropna().astype(str).str.strip()
    dates = dates[dates.ne("")]
    matched = pd.Series(False, index=dates.index)
    date_rows = []
    for label, pattern in DATE_PATTERNS:
        count = int(dates.str.match(pattern).sum())
        matched = matched | dates.str.match(pattern)
        date_rows.append(f"| {label} | {count} | {_percent(count, len(dates))} |")
    other_dates = int((~matched).sum())
    date_rows.append(f"| Other | {other_dates} | {_percent(other_dates, len(dates))} |")

    invalid_prices = int(((df["price"].notna()) & (df["price"] <= 0)).sum()) if "price" in df else 0
    repeated_ids = int(df["trade_id"].duplicated().sum()) if "trade_id" in df else 0
    duplicate_rows = int(df.duplicated().sum())
    held_back = ", ".join(scores["below_threshold"]) if scores["below_threshold"] else "none"

    weight_rows = "\n".join(f"| `{field}` | {WEIGHT[field]} | {WHY[field]} |" for field in WEIGHT)
    check_rows = "\n".join(
        f"| {check['category'].title()} | {check['check']} | {check['weight']} | {check['score']:.1f} |"
        for check in scores["checks"]
    )
    score_rows = "\n".join(
        f"| {category.title()} | {scores[category]:.1f} | {'Meets the bar' if scores[category] >= SCORE_THRESHOLD else 'Below the bar'} |"
        for category in CATEGORIES
    )
    allowed_rows = []
    for column, allowed in ALLOWED_VALUES.items():
        invalid = invalid_category_count(df[column], allowed)
        allowed_rows.append(f"| {column} | {', '.join(sorted(allowed))} | {invalid} |")

    report = f"""# Data profile

Prepared: {datetime.now().strftime("%Y-%m-%d")}
Prepared by: {user}
Company Name: {company_name}
Prepared for client: {client_name}

## Can this file be used?

Overall score: **{scores['overall']:.1f}** out of 100.

This file should not be used for analysis, past trends, or a forecasting model until every category is at least {SCORE_THRESHOLD}. Categories below {SCORE_THRESHOLD}: {held_back}.

The overall score weights each check by how hard it is to use the row without that field. It is not a plain average. Weight 3 is trade id, instrument id, and price. Weight 2 is date, quantity, buyer, and seller. Weight 1 is instrument type and trade status. Buyer and seller are 2 rather than 3 because a missing party blocks who traded, not what the security was worth.

| Category | Score | Against the {SCORE_THRESHOLD} bar |
| --- | ---: | --- |
{score_rows}
| Overall (weighted) | {scores['overall']:.1f} |  |

| Category | Question | Weight | Rows passing |
| --- | --- | ---: | ---: |
{check_rows}

Two repeat problems are scored separately. {scores['exact_copy']} rows are an exact copy of another row: same id and same trade, so the extra row can be dropped. {scores['different_trade']} rows use a trade id that also appears on a different trade. Those rows are not extra copies. Dropping or merging them would mix two trades. A row can be counted in both when an id has a copy and also a second, different trade.

Filled instrument ids not on the reference list of {reference['instrument_id'].nunique()} securities: {scores['unknown_instrument']}. Rows whose type disagrees with that security: {scores['type_mismatch']}.

## Why the weights

| Field | Weight | Why this weight |
| --- | ---: | --- |
{weight_rows}

The reference file (`{reference_path}`) is the list of securities a trade should point to: id, name, asset class, type, venue, issuer, currency, and status.

## Profile counts

| Metric | Value |
| --- | ---: |
| Records | {row_count} |
| Columns | {df.shape[1]} |
| Duplicate rows | {duplicate_rows} |
| Repeated trade ids | {repeated_ids} |
| Missing cells | {missing_total} |

| Column | Type | Missing | Values |
| --- | --- | ---: | --- |
{chr(10).join(column_rows)}

## Invalid prices

Prices at or below zero: {invalid_prices} ({_percent(invalid_prices, row_count)} of rows).

## Trade date formats

| Pattern | Count | Share of non-empty dates |
| --- | ---: | ---: |
{chr(10).join(date_rows)}

## Values outside the allowed lists

| Column | Allowed values | Outside the list |
| --- | --- | ---: |
{chr(10).join(allowed_rows)}

Repeated trade ids minus identical rows: {repeated_ids - duplicate_rows}.
"""
    output_path.write_text(report)
    return output_path
