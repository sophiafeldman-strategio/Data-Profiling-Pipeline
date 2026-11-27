# Meridian Data Schema

Source files: `meridian_reference_data.csv`, `meridian_trades.csv`, `meridian_trades.json`

## Overview

This dataset models a securities trade blotter for "Meridian Capital Markets," plus a reference/master file of the instruments traded.

- **`meridian_reference_data.csv`** — instrument master (30 rows, one per instrument): ID, name, asset class, venue, issuer, currency, status.
- **`meridian_trades.csv`** — 100,000 trade records in flat/tabular form, `snake_case` fields.
- **`meridian_trades.json`** — the same 100,000 trade records, re-shaped into nested objects with different (camelCase) field names, simulating a second source system exporting the same underlying trades.

## `meridian_reference_data.csv` (instrument master — 30 rows)

| Field | Type | Description |
|---|---|---|
| `instrument_id` | string(4) | Ticker/security code, e.g. `MRCX` |
| `instrument_name` | string | Full instrument name |
| `asset_class` | enum | `Equities`, `Exchange Traded Funds`, `Fixed Income` |
| `instrument_type` | enum | `Equity`, `ETF`, `Bond` |
| `trading_venue` | enum | `NYSE`, `NASDAQ`, `NYSE Arca`, `OTC` |
| `issuer` | string | Legal entity name |
| `currency` | string(3) | ISO currency code |
| `status` | enum | Instrument status |

## `meridian_trades.csv` (trade blotter — 100,000 rows)

| Field | Type | Description |
|---|---|---|
| `trade_id` | string | Trade identifier, format `TRD-XXXXXXXXXX` (10 hex chars) |
| `instrument_id` | string(4) | Instrument code, references `meridian_reference_data.instrument_id` |
| `instrument_type` | enum | `Equity`, `ETF`, `Bond` |
| `trade_date` | string | Trade date |
| `buyer` | string | Buying broker/firm name |
| `seller` | string | Selling broker/firm name |
| `quantity` | integer | Units traded |
| `price` | float | Execution price, USD |
| `trade_status` | enum | `EXECUTED`, `SETTLED`, `CANCELLED`, `PENDING`, `REJECTED` |

## `meridian_trades.json` (same trades, alternate schema)

Nested structure, camelCase, per record:

```
{
  "tradeReference": string,
  "security": {
    "securityCode": string,
    "securityType": string
  },
  "executionDate": string,
  "counterparties": {
    "buyingFirm": string,
    "sellingFirm": string
  },
  "tradeDetails": {
    "units": integer,
    "executionPrice": float,
    "settlementStatus": string
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
