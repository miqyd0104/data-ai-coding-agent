# Exercise 05: specification-led product reporting

The user approved the reporting choices in chat before implementation:
date/branch/product/category/net-items/revenue columns, pounds with two decimal
places, refunds subtracting, unknown products rejected with a reason, and no
rows for absent branches. `specs/product-summary.md` fixes the exact column
names, ordering, empty-file behaviour, zero-net groups, FX handling and acceptance
criteria. Its acceptance table maps each rule to a named test.

On local branch `exercise-05`, eleven tests failed before the implementation.
The completed report reuses accepted warehouse rows, groups by branch and
canonical product, uses catalogue categories, and sums integer line totals.
Both report types now format money without binary floating point. A large
integer test catches loss of pennies beyond floating-point integer precision.

Integration tests cover all three fixture dates, check every product group
against SQLite, add up to each daily branch total, and verify stable output on
reruns without changing another date. Additional tests preserve a valid JSONL
transaction after malformed input, reject an unknown SKU and fail clearly for
missing required CSVs or an invalid processing date.

The specification surfaced choices the ticket did not settle: zero-net product
groups remain visible, absent branches produce no rows, revenue strings have
no currency symbol, and Dublin reports use the stored FX-allocated line totals.
These are written explicitly so another engineer can implement the same result.

The work used the written spec as the implementation boundary within this Codex
chat; no separate Claude session or human training-session timing is claimed.
