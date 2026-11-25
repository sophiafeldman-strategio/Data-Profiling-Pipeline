# Meridian Data Documentation

Source files: `meridian_reference_data.csv`, `meridian_trades.csv`, `meridian_trades.json`
Generator: `sim10_data/code/generate_meridian_data.py`

Note: `NEW_LUUM_GPSv2Tracker_TX-WC (8).xlsm` also lives in this data folder but is unrelated to the Meridian dataset (a GPS tracker workbook) — flagged under Data Quality below, not covered elsewhere in this doc.

---

## 1. Data Description

This is a **synthetic capital-markets trade dataset** for "Meridian Capital Markets," built for use in an Enterprise Simulator. It models a securities trade blotter plus a reference/master file of the instruments traded, and is deliberately seeded with realistic data quality defects for cleansing/reconciliation exercises.

Three files, two systems:

- **`meridian_reference_data.csv`** — a static instrument master (30 rows, one per instrument): ID, name, asset class, venue, issuer, currency, status. Clean, no defects introduced.
- **`meridian_trades.csv`** — 100,000 trade records in flat/tabular form, `snake_case` fields. Represents one source system's export.
- **`meridian_trades.json`** — the *same* 100,000 trade records, re-shaped into nested objects with different (camelCase, business-style) field names — simulating a second source system exporting the same underlying trades. Values are otherwise identical to the CSV (same rows, same injected errors, same order).

This two-format design (`meridian_trades.csv` vs `.json`) is itself the main modeling feature: it forces a **field-mapping/reconciliation problem** on top of the usual cleansing problem — the two files must be joined conceptually via `trade_id` ↔ `tradeReference` despite completely different schemas.

---

## 2. Schema

### 2.1 `meridian_reference_data.csv` (instrument master — 30 rows)

| Field | Type | Description | Notes |
|---|---|---|---|
| `instrument_id` | string(4) | Ticker/security code, e.g. `MRCX` | Primary key. All-caps, 4 chars |
| `instrument_name` | string | Full instrument name | |
| `asset_class` | enum | `Equities`, `Exchange Traded Funds`, `Fixed Income` | |
| `instrument_type` | enum | `Equity`, `ETF`, `Bond` | Short form of `asset_class`; maps to `meridian_trades` `instrument_type` |
| `trading_venue` | enum | `NYSE`, `NASDAQ`, `NYSE Arca`, `OTC` | |
| `issuer` | string | Legal entity name | |
| `currency` | string(3) | ISO currency code | Always `USD` in this dataset |
| `status` | enum | `Active` | Only value present |

### 2.2 `meridian_trades.csv` (trade blotter — 100,000 rows)

| Field | Type | Description | Notes |
|---|---|---|---|
| `trade_id` | string | Trade identifier, format `TRD-XXXXXXXXXX` (10 hex chars) | **Not unique** — see DQ issues |
| `instrument_id` | string(4) or blank | FK → `meridian_reference_data.instrument_id` | Blank in ~8% of rows |
| `instrument_type` | enum | `Equity`, `ETF`, `Bond` | Always populated, even when `instrument_id` is blank |
| `trade_date` | string | Trade date | **Mixed formats** — see DQ issues |
| `buyer` | string or blank | Buying broker/firm name | Drawn from a fixed list of 20 brokers; blank in some rows |
| `seller` | string or blank | Selling broker/firm name | Same list as `buyer`, never equal to `buyer` on a given row; blank in some rows |
| `quantity` | integer | Units traded | Range 100–50,000 |
| `price` | float | Execution price, USD | Range ~$10.00–$500.00; **can be negative** — see DQ issues |
| `trade_status` | enum | `EXECUTED`, `SETTLED`, `CANCELLED`, `PENDING`, `REJECTED` | Roughly evenly distributed |

### 2.3 `meridian_trades.json` (same 100,000 trades, alternate schema)

Nested structure, camelCase, per record:

```
{
  "tradeReference": string,              // == trade_id
  "security": {
    "securityCode": string,              // == instrument_id
    "securityType": string                // == instrument_type
  },
  "executionDate": string,               // == trade_date
  "counterparties": {
    "buyingFirm": string,                // == buyer
    "sellingFirm": string                 // == seller
  },
  "tradeDetails": {
    "units": integer,                    // == quantity
    "executionPrice": float,             // == price
    "settlementStatus": string            // == trade_status
  }
}
```

Field mapping CSV → JSON:

| CSV field | JSON path |
|---|---|
| `trade_id` | `tradeReference` |
| `instrument_id` | `security.securityCode` |
| `instrument_type` | `security.securityType` |
| `trade_date` | `executionDate` |
| `buyer` | `counterparties.buyingFirm` |
| `seller` | `counterparties.sellingFirm` |
| `quantity` | `tradeDetails.units` |
| `price` | `tradeDetails.executionPrice` |
| `trade_status` | `tradeDetails.settlementStatus` |

---

## 3. Data Quality Issues

Verified by direct inspection of the generated files (not just the generator script), on the current 100,000-row dataset.

| # | Issue | Scope | Detail |
|---|---|---|---|
| 1 | **Duplicate `trade_id`s** | 4,583 IDs reused → 9,362 rows (~9.4% of all rows) share an ID with at least one other row | IDs are duplicated but the underlying trade *content differs* (different instrument, date, counterparties, price) — these are not accidental double-exports, they're colliding keys on genuinely different trades. `trade_id` is **not usable as a primary key** without a synthetic surrogate. |
| 2 | **Missing `instrument_id`** | 7,940 rows (7.94%) | `instrument_id` is blank while `instrument_type` remains populated, so the instrument type is known but it can't be resolved to a specific security or joined to the reference file. |
| 3 | **Inconsistent `trade_date` formats** | 10,013 rows (~10%) not in ISO `YYYY-MM-DD` | Breakdown: 89,987 `YYYY-MM-DD`, 3,392 `YYYY.MM.DD`, 3,327 `DD/MM/YYYY`, 3,294 `MM-DD-YYYY`. Critically, **1,336 of the `DD/MM/YYYY` rows have day ≤ 12**, making them genuinely ambiguous with `MM/DD/YYYY` — they cannot be parsed correctly by position alone without a per-row format detector. |
| 4 | **Negative prices** | 2,996 rows (~3.0%) | `price` ranges from -$500.00 to $499.99; negative values are not economically valid for an execution price and indicate either a sign/data-entry error or (if intentional, e.g. a correction/reversal) an undocumented convention. |
| 5 | **Missing counterparty** | 2,551 rows missing `buyer`, 2,383 rows missing `seller` (~4.9% of rows total, one side blank at a time) | No row is missing both sides, and `buyer` is never equal to `seller` when both are populated — but a blank counterparty makes the trade impossible to fully reconcile/settle. |
| 6 | **Two incompatible schemas for the same data** | All 100,000 records | `meridian_trades.csv` and `meridian_trades.json` encode identical trades under different field names and nesting (see §2.3). Any pipeline ingesting both sources needs an explicit mapping layer; naive concatenation/union will silently produce two disjoint, unaligned schemas. |
| 7 | **`quantity` and numeric fields typed as strings in JSON dict read** | N/A — informational | `units`/`quantity` and `executionPrice`/`price` are written as native JSON numbers but as plain strings in the CSV (as CSV always is) — routine but worth flagging for any strict-typing ingestion step. |
| 8 | **Unrelated file in the data directory** | `NEW_LUUM_GPSv2Tracker_TX-WC (8).xlsm` (~4.9 MB) | Not referenced by the generator script and not part of the Meridian schema — appears to be an unrelated file (a GPS tracker workbook) that landed in the same folder. Worth relocating or excluding from any Meridian ingestion job so it isn't mistaken for part of this dataset. |

### Fields with no observed issues
- `instrument_type`, `trade_status`: always populated, values stay within the expected enum.
- `quantity`: always positive, within the 100–50,000 generation range.
- `trade_date` values (once parsed): all fall within the expected 2025-01-01 to 2026-06-30 generation window.
- `instrument_id` values (when present): all 30 distinct codes match the reference file exactly — no orphaned/unknown instrument codes.
- `buyer`/`seller` (when present): always two distinct brokers from the expected 20-broker list; no self-trades.
- Reference data (`meridian_reference_data.csv`): fully populated, one row per instrument, no defects introduced by the generator.

### Root cause
All of the above (issues 1–5) are **intentionally injected** by `generate_meridian_data.py` (lines 55–93) as synthetic noise for a data-cleansing exercise, at these rates: ~5% duplicate trade IDs, ~8% missing instrument IDs, ~10% non-ISO dates, ~3% negative prices, ~5% missing buyer or seller. Issues 6–8 are structural/environmental rather than randomly injected.
