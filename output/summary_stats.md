# Data profile

Prepared: 2026-11-27
Prepared by: Sophia Feldman
Company Name: Strategio
Prepared for client: Meridian Capital

## Can this file be used?

Overall score: **86.8** out of 100.

This file should not be used for analysis, past trends, or a forecasting model until every category is at least 90. Categories below 90: consistency.

The overall score weights each check by how hard it is to use the row without that field. It is not a plain average. Weight 3 is trade id, instrument id, and price. Weight 2 is date, quantity, buyer, and seller. Weight 1 is instrument type and trade status. Buyer and seller are 2 rather than 3 because a missing party blocks who traded, not what the security was worth.

| Category | Score | Against the 90 bar |
| --- | ---: | --- |
| Completeness | 96.7 | Meets the bar |
| Consistency | 53.6 | Below the bar |
| Accuracy | 98.6 | Meets the bar |
| Timeliness | 90.4 | Meets the bar |
| Validity | 100.0 | Meets the bar |
| Overall (weighted) | 86.8 |  |

| Category | Question | Weight | Rows passing |
| --- | --- | ---: | ---: |
| Completeness | Does the row have a trade id? | 3 | 100.0 |
| Completeness | Does the row have an instrument id? | 3 | 91.2 |
| Completeness | Does the row have a buyer? | 2 | 98.9 |
| Completeness | Does the row have a seller? | 2 | 97.8 |
| Accuracy | Is the price above zero? | 3 | 97.7 |
| Accuracy | Is the quantity above zero? | 2 | 100.0 |
| Timeliness | Is the date YYYY-MM-DD and inside 2025-01-01 to 2026-06-30? | 2 | 90.4 |
| Consistency | Is this row the only copy of this exact trade? | 3 | 11.8 |
| Consistency | Does this trade id describe only one trade? | 3 | 80.0 |
| Consistency | Does the instrument type match the reference security? | 1 | 100.0 |
| Validity | Is a filled instrument id on the reference list? | 3 | 100.0 |
| Validity | Is the instrument type Equity, ETF, or Bond? | 1 | 100.0 |
| Validity | Is the trade status on the allowed list? | 1 | 100.0 |

Two repeat problems are scored separately. 1764 rows are an exact copy of another row: same id and same trade, so the extra row can be dropped. 400 rows use a trade id that also appears on a different trade. Those rows are not extra copies. Dropping or merging them would mix two trades. A row can be counted in both when an id has a copy and also a second, different trade.

Filled instrument ids not on the reference list of 30 securities: 0. Rows whose type disagrees with that security: 0.

## Why the weights

| Field | Weight | Why this weight |
| --- | ---: | --- |
| `trade_id` | 3 | A row with no trade id, or an id reused on another row, is not one trade you can count. |
| `instrument_id` | 3 | Without a known security, the row cannot be joined to the reference list or used in a price history. |
| `price` | 3 | Price is the value the analysis is about. Zero or negative is not a usable execution price. |
| `trade_date` | 2 | A date that is not YYYY-MM-DD inside 2025-01-01 to 2026-06-30 cannot sit on a timeline. |
| `quantity` | 2 | Size is needed for volume, and it is less damaging than a missing price. |
| `buyer` | 2 | A missing party blocks who traded. It does not block what the security was worth. |
| `seller` | 2 | Same as buyer: settlement needs a party, a price history does not. |
| `instrument_type` | 1 | Equity, ETF, or Bond is a label. The instrument id already names the security. |
| `trade_status` | 1 | Status is a label on a trade you can already identify. |

The reference file (`data_info/meridian_reference_data.csv`) is the list of securities a trade should point to: id, name, asset class, type, venue, issuer, currency, and status.

## Profile counts

| Metric | Value |
| --- | ---: |
| Records | 2000 |
| Columns | 9 |
| Duplicate rows | 882 |
| Repeated trade ids | 1048 |
| Missing cells | 242 |

| Column | Type | Missing | Values |
| --- | --- | ---: | --- |
| trade_id | object | 0 | 952 unique |
| instrument_id | object | 176 | 30 unique |
| instrument_type | object | 0 | 3 unique |
| trade_date | object | 0 | 535 unique |
| buyer | object | 22 | 20 unique |
| seller | object | 44 | 20 unique |
| quantity | int64 | 0 | 167 to 49952 |
| price | float64 | 0 | -497.46 to 499.76 |
| trade_status | object | 0 | 5 unique |

## Invalid prices

Prices at or below zero: 46 (2.3% of rows).

## Trade date formats

| Pattern | Count | Share of non-empty dates |
| --- | ---: | ---: |
| YYYY-MM-DD | 1808 | 90.4% |
| YYYY.MM.DD | 64 | 3.2% |
| DD-MM-YYYY or MM-DD-YYYY | 68 | 3.4% |
| DD/MM/YYYY or MM/DD/YYYY | 60 | 3.0% |
| Other | 0 | 0.0% |

## Values outside the allowed lists

| Column | Allowed values | Outside the list |
| --- | --- | ---: |
| instrument_type | Bond, ETF, Equity | 0 |
| trade_status | CANCELLED, EXECUTED, PENDING, REJECTED, SETTLED | 0 |

Repeated trade ids minus identical rows: 166.
