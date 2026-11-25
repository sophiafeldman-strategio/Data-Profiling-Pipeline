# Meridian trade data quality report

Prepared by Sophia Feldman for Meridian Capital Markets.
Source: the combined CSV and JSON blotter profiled in `output/summary_stats.md` (2,000 rows, 9 columns).

The NA count and the blank count are the same in every column below (121 cells). Do not add those two numbers together. Treat them as one missing-value problem until you confirm whether each cell is a pandas NA, an empty string, or both.

## Completeness

A record is incomplete when a field needed to identify or value the trade is missing.

- `instrument_id` is missing on 88 rows (8.8%). Those rows cannot be tied to a security.
- `buyer` is missing on 11 rows and `seller` is missing on 22 rows. The trade still has an id, but one side of the trade is unnamed.
- `trade_id`, `trade_date`, `quantity`, and `price` are populated on every row.
- No cell is a Python `None`. The gaps are pandas missing values and blank strings.

8.8% of rows are incomplete on the required fields, and every one of those failures is a missing `instrument_id`.

## Consistency

The same kind of fact is not stored the same way, and some trade ids are reused.

- Trade dates use four patterns. 1,808 dates (90.4%) are `YYYY-MM-DD`. 64 use dots (`YYYY.MM.DD`), 68 use dashes as `DD-MM-YYYY` or `MM-DD-YYYY`, and 60 use slashes. Nothing falls outside those four patterns.
- The two-digit dates can be read as day-first or month-first. A date such as `05-06-2024` is not one calendar day until the source says which part is the month.
- 1,048 trade ids occur more than once. 882 rows are exact copies of another row. The other 166 repeated ids are the same id on rows that differ in at least one column. Those 166 are not safe to treat as duplicates or as distinct trades without a business rule.

## Accuracy

These checks can show that a value is implausible. They cannot prove the original blotter was wrong.

- 46 prices are zero or negative (2.3% of rows). The price column ranges from -497.46 to 499.76. A traded price at or below zero should be reviewed before it is used.
- Quantity ranges from 167 to 49,952, which is a plausible share count on its own. This profile does not compare quantity or price to the reference data.

## Timeliness

Every row has a trade date, so the file is not missing dates. The dates are not in one format, so a sort or a "latest date" calculation will be wrong for the 192 rows that are not `YYYY-MM-DD` until those dates are parsed.

## Validity

A value is invalid when it breaks a rule for that field, even if the cell is filled in.

- Prices at or below zero fail a basic price rule (46 rows).
- Dates that are not `YYYY-MM-DD` fail a single-format rule (192 rows). The ambiguous two-digit dates are the more serious subset because the day and month can be swapped.
- `instrument_type` has 3 distinct values and `trade_status` has 5. This profile does not check those values against an allowed list.

## User story

As a Meridian product owner, I want a profiling report of the combined trade blotter so that I can see which trades are incomplete, inconsistent, or invalid before the data is used for reporting. I want a full picture of the data's reliability and quality before using the data for analysis. 

### Acceptance criteria

- The pipeline loads the CSV and the JSON blotter and combines them into one table.
- The report states row count, column types, missing values, duplicate rows, and repeated trade ids.
- Missing values are split into pandas NA, Python `None`, and blank text.
- The report lists prices at or below zero and counts each trade-date pattern.
- A missing or unreadable input file stops that load and prints an error instead of writing a partial profile.
- The findings are grouped under completeness, consistency, accuracy, timeliness, and validity.
