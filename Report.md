# Meridian trade data quality report

Prepared by Sophia Feldman for Meridian Capital Markets.
Source: two copies of the same trade file, saved with different column names. Combined, that is 2,000 rows. Each trade was also checked against Meridian's list of 30 securities.

## Can this file be used?

**No.** The overall score is **86.8** out of 100. Do not use this file for analysis, past trends, or a forecasting model until every category is at least 90. Consistency is the category below that bar.

The overall score is a weighted average of the checks, not a plain average of the five categories. The weight is how hard it is to use a row when that field is bad.

| Weight | Fields | Why |
| ---: | --- | --- |
| 3 | Trade id, instrument id, price | Without these you cannot name the trade, name the security, or say what it was worth. |
| 2 | Trade date, quantity, buyer, seller | The row can still be priced. A missing date, size, or party blocks the timeline, the volume, or who traded. |
| 1 | Instrument type, trade status | These are labels. The instrument id already names the security. |

Buyer and seller are 2, not 3. A missing party blocks settlement. It does not block a price history.

| Category | Score | Against the 90 bar |
| --- | ---: | --- |
| Completeness | 96.7 | Meets |
| Consistency | 53.6 | Below |
| Accuracy | 98.6 | Meets |
| Timeliness | 90.4 | Meets |
| Validity | 100.0 | Meets |
| Overall (weighted) | 86.8 |  |

## What failed

**Consistency is 53.6 because repeated trades are two different problems, and both are scored.**

1,764 rows fail “Is this row the only copy of this exact trade?” They come from loading both copies of the file. Where the same trade appears once in each copy, the rows match. The second copy adds nothing. Keeping both makes a sum of volume, an average price, or a count of trades too high. Drop the extra copy.

400 rows fail “Does this trade id describe only one trade?” The same id is on two trades that differ in security, date, party, or price. Those are not extra copies. Do not drop one, and do not merge them. Give the second trade a new id, or leave it out of totals.

A row can fail both questions when an id has an exact copy and also a second, different trade. Instrument type still matches the reference security on every row.

**The other categories clear 90.** Completeness is 96.7: trade id is always present, instrument id is present on 91.2% of rows, and buyer and seller are rarely blank. Accuracy is 98.6 because 97.7% of prices are above zero and every quantity is above zero. Timeliness is 90.4: that share of dates is `YYYY-MM-DD` inside 1 Jan 2025 to 30 Jun 2026. Validity is 100. Every filled instrument id is one of the 30 reference securities, and no row gives that security a different type.

A blank instrument id fails completeness. A filled id that is not on the reference list would fail validity. This file has the first problem and not the second.

## Next steps

The file is close to usable. Four of the five categories already clear 90. The work that unlocks analysis is the duplicate trade ids. After that cleanup, the same pipeline can total volume, average price, and count trades by security and by month.

1. **Drop the exact copies.** Remove 1,764 rows that repeat another row in full. Where the same trade appears in both copies, keep one row. Nothing is lost. Sums and averages stop counting the same trade twice.
2. **Merge only when the two rows are the same trade and one of them fills a blank.** If the security, date, and price match and one copy has a buyer or a seller the other is missing, keep the filled value. On this file that case did not occur: the same trade in both copies was already identical. There is nothing to merge.
3. **Set aside the 400 rows whose trade id describes more than one trade.** Give the second trade a new id, or leave it out of totals. Do not merge them. A merged row would mix two securities or two prices under one trade.
4. **Re-score the cleaned file.** The file is ready for historical totals only when every category is at least 90.
5. **Then run the history.** Sum quantity, average price, and count trades by security and by month. Leave out rows that still have no instrument id, a price at or below zero, or a date that is not `YYYY-MM-DD`. Those are a small share of the file. They should not sit inside a trend.

## User story

As a Meridian product owner, I want a weighted score of the combined blotter, checked against the instrument list, so I can see whether the file is fit for analysis before anyone builds a trend or a model on it.

### Acceptance criteria

- The pipeline loads both blotters, combines them, and scores completeness, consistency, accuracy, timeliness, and validity.
- Trade id, instrument id, and price use weight 3. Date, quantity, buyer, and seller use weight 2. Instrument type and trade status use weight 1.
- The file is not marked ready unless every category is at least 90.
- A filled instrument id that is not on the reference list fails validity.
- A missing or unreadable input file stops the load and prints an error.
