# Exercise 03: test-driven fixes and extensions

Work continued cumulatively on local branch `exercise-03`. Small characterisation
tests captured the original row shape, timestamp and price rules, duplicate
handling, negative quantities and summary aggregation. The original Dublin,
refund and duplicate expectations were explicitly marked as bugs. They were
updated only when those behaviours were intentionally corrected; the history
preserves the initial snapshots (`afb6ad0`).

## KC-101: currency direction

Finance's €790.85 / 1.1712 = £675.247609… ⇒ **£675.25** for 14 September.
A tiny €11.71 example failed at 1371 pence before the fix and passed at 1000
pence afterwards. The pipeline initially improved from £917.66 to £668.92, but
did not reconcile yet, demonstrating why a single unit test is insufficient.
See `03-kc101-red.txt`, `03-kc101-green.txt` and commit `ca7fd94`.

## KC-104: Edinburgh

JSONL contains transaction metadata and multiple SKU-priced items. The adapter
maps each SKU to a catalogue name, flattens the items into the shared six-field
row, then reuses cleaning, loading and reporting. Till prices remain authoritative.
Missing Edinburgh exports are allowed, so the 14th still processes four branches.
On the 16th Edinburgh reconciles to **120 transactions, 207 net items, £664.00**.
The first adapter exposed the existing refund and duplicate bugs in Edinburgh
too, so those fixes were needed before the full integration test could pass.
The red tests and intermediate failure are saved; commit `5bb518c` adds the format.

## KC-102 and KC-103: stretch tasks

- Preserve signed refunds. Two returned £3.50 items contribute −2 items and −£7.00.
- Deduplicate by branch, transaction, timestamp, till, canonical product, signed
  quantity and native unit price. Different transactions, quantities, prices or
  tills survive even in the same minute.
- Use all the parsing helpers in real cleaning and map names through the catalogue.
  Unknown/blank products and invalid prices or quantities are rejected with reasons.
- Apply Decimal exchange rates and validate their date and GBP base.
- Round the accepted branch/day native EUR total once, half up. Allocate GBP pennies
  by largest fractional remainder, with stable transaction keys breaking ties.
  This keeps stored line totals and all reports consistent, including refunds.

After refunds, duplicates and product rejection were fixed, Dublin's unit-price
rounding still produced £675.11 on the 14th. A failing full-day test revealed
the remaining **14p** difference. The final allocation gives **£675.25**, and
all 13 supplied branch/day Z-reports now reconcile to the penny.

For foreign-currency sales, `unit_price_pence` is a rounded GBP unit quote.
`line_total_pence` includes allocated FX pennies, so it can differ from quantity
times that unit quote. Reports and reconciliations must sum the stored line totals.
This rounding policy is an explicit implementation assumption supporting the
exercise's whole-day reconciliation requirement.

The data lacks unique line IDs. Two genuinely separate, otherwise identical
lines inside the same transaction cannot be distinguished from an export
duplicate. The implemented rule is documented and tested; a production till
integration would need line IDs to remove this ambiguity.

The final Z-report tests run all three dates and check transactions, signed
items and revenue. Rerun tests check warehouse replacement; product-report
tests later also verify that other dates and their reports survive unchanged.
The implementation never uses the Z-report to set its output values.

## Reflection

Characterisation initially recorded known bugs; comments and hand calculations
prevented those snapshots being mistaken for the intended behaviour. Red tests
demonstrated the currency direction, refund, collision and rounding errors
before the fixes. Responsibility for business figures remains with the engineer
who reviews and ships them. There was no external business sign-off in this run.
