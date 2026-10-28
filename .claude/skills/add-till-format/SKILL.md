---
name: add-till-format
description: Add a Kettle & Crumb branch or till export format using the shared pipeline and catalogue, with tests for missing files, refunds and reconciliation.
---

Read `AGENTS.md` and the branch's supplied export schema. Inspect only the
relevant till sample and catalogue; customer loyalty data is unrelated.

1. Compare the format, column order, date format, price units, currency, IDs and
   product identifiers with `kettle/branches.py` and `kettle/extract.py`.
   Reuse an existing format when possible; a Leeds-style branch should only
   need a registry entry, not another parser or branch-specific transform.
2. Before implementation, add tiny synthetic tests outside `data/raw/` for an
   ordinary sale, a refund, multiple items, an exact duplicate and an unknown
   product/SKU. Check that distinct sales in the same minute both survive.
3. Test the day before opening without an export. Mark that branch optional
   if absence is expected; missing required established-branch files must fail.
4. Add the registry entry and, only for a genuinely new format, adapt extraction
   to the shared six fields: transaction ID, timestamp, till ID, product name,
   signed quantity and native unit price. Use the registry's column mapping for
   nonstandard CSV layouts. Map SKUs using the catalogue, never catalogue prices.
5. Keep price parsing, catalogue normalisation, refunds and duplicate handling
   in `clean_rows`. Record malformed input and unknown products as rejections.
6. Run the new tests red, implement, then run `uv run pytest`. Check daily and
   product totals against independently calculated expected values or supplied
   Z-reports. Verify reruns do not duplicate warehouse rows or alter other dates.
7. Review the diff, verify raw data is unchanged, then commit with the ticket ID
   when one exists. Report any business assumptions or unavailable real data.
