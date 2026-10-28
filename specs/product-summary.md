# Product summary specification

Reporting rules agreed with the user on 28 October 2026.

1. Each pipeline run writes `output/product_summary_<date>.csv` alongside the
   daily summary and warehouse, replacing that date's existing report on reruns.
2. The UTF-8 CSV header is exactly, in this order:
   `date,branch,product,category,items_sold,revenue_gbp`.
3. There is one row for each branch/canonical-product pair with at least one
   accepted sale or refund on the processing date. Product names and categories
   come from `data/reference/products.json`; aliases and Edinburgh SKUs resolve
   to those same names before reporting. Use till prices, not catalogue prices.
4. `date` is `YYYY-MM-DD`; `branch` uses the registry's lowercase identifier.
   `items_sold` is the signed net integer quantity. Refunds subtract quantities
   and revenue, including a product with only refunds. Keep groups whose sales
   and refunds net to zero, so activity is visible.
5. Revenue is GBP written as a decimal string with exactly two digits after the
   decimal point, no currency symbol or thousands separators. Negative revenue
   has a leading minus. Sum the warehouse's integer `line_total_pence` values;
   never recompute revenue from rounded GBP unit prices or use binary floats.
   Dublin uses the daily FX penny allocation described in `AGENTS.md`, so its
   product totals reconcile with its converted native-currency daily total.
6. Unknown or blank product names/SKUs are rejected before loading or reporting.
   Record the branch, logical row number and reason in `rejected_rows_<date>.csv`.
   Do not invent a category or silently include an unrecognised product.
7. A branch without accepted rows has no product rows; do not fabricate zero
   sales for absent branches. A completely empty day's product CSV still has
   its header and no data rows. Expected absent Edinburgh/Glasgow files are
   allowed; missing required established-branch files remain errors.
8. Sort output by branch then canonical product name, ascending, for repeatable
   reports. Only use rows for the requested processing date.
9. For every branch/day, product quantities and revenue must sum exactly to the
   daily summary and the warehouse. For the supplied fixture dates, transaction
   counts, net quantities and daily revenue must also match Finance's Z-reports
   (converting Dublin's net EUR total to GBP, rounded half up once).
10. Rerunning a date must reproduce both reports and replace its warehouse rows
    without duplicating them or changing other dates. Raw inputs stay unchanged.

## Acceptance tests

| Rule | Tests |
| --- | --- |
| 1–2 | `test_product_csv_has_exact_header_and_is_replaced` |
| 3 | `test_product_groups_use_catalogue_and_till_prices`; `test_skus_and_aliases_share_canonical_names` |
| 4 | `test_product_refunds_and_zero_net_groups` |
| 5 | `test_product_money_is_exact_even_above_float_precision`; currency tests; reconciliation tests |
| 6 | `test_unknown_products_do_not_reach_product_report`; data-quality tests |
| 7 | `test_empty_product_summary_is_header_only`; Edinburgh/Glasgow absence tests; required-file test |
| 8 | `test_product_groups_use_catalogue_and_till_prices`; wrong-date rejection test |
| 9 | `test_product_totals_equal_daily_and_warehouse`; Z-report reconciliation tests |
| 10 | `test_reports_and_other_days_survive_rerun`; raw hash and Git diff checks |
