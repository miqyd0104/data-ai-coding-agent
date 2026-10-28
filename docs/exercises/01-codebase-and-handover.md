# Exercise 01: codebase investigation

This investigation describes the inherited code at commit `4c5d322`, before
the fixes. Use `git show 4c5d322:<path>` to inspect the original line numbers.
The original `HANDOVER.md` is retained as teaching material, including its errors.

## First questions

The entry point is `kettle/__main__.py`. It calls `pipeline.run`, which reads four
hard-coded branches, cleans their CSV rows, replaces that date's SQLite sales,
and creates the daily CSV. `extract.py` reads files, `transform.py` cleans rows,
`load.py` manages SQLite, and `report.py` aggregates sales. The unfinished helpers
are independent of the original `clean_rows` implementation.

The first Leeds row (`data/raw/tills/leeds_2026-09-14.csv:2`) is transaction
`LDS-0914-0001`, 14 September at 07:01, till T2, ` Americano `, quantity 1,
unit price `3.00`. Extraction drops the header and returns six strings.
Cleaning parses the UK timestamp, converts the price to 300 pence and the name
to `Americano`, and constructs an eight-field sale with a 300-pence line total.
The loader inserts it into `sales`; reporting adds one item and £3.00 to Leeds,
counting its transaction once even though the same transaction also buys tea.

Leeds and York use day-first timestamps and prices in pounds. Manchester uses
ISO timestamps and integer pence. Dublin uses ISO timestamps, different column
positions and prices in euros. Edinburgh's supplied file is JSON Lines, with
one transaction containing a list of SKU-labelled items; the original pipeline
never reads it.

The original pipeline reads the four configured till CSVs and the daily EUR
rate. It does not read the catalogue, Z-reports or loyalty-members file.
`read_products` being defined does not mean it is called.

Run tests with `uv run pytest` and a day with `uv run python -m kettle 2026-09-14`.
The baseline result was 39 failed and 1 passed; the smoke test verified only
that the program ran. See `docs/validation/00-baseline.txt`.

## Ten handover claims checked

| # | Handover claim | What was actually true | Evidence in the original version |
| --- | --- | --- | --- |
| 1 | Every till is picked up automatically. | False. Only Leeds, Manchester, York and Dublin are processed. Edinburgh needs configuration and a JSONL adapter. | `kettle/pipeline.py:8`, `:15`; `data/raw/tills/edinburgh_2026-09-16.jsonl:1`. |
| 2 | All CSV unit prices are pounds. | False. Leeds/York use pounds, Manchester pence, Dublin euros. The branch name controls parsing; headers alone do not identify units. | `kettle/transform.py:25`; Leeds CSV line 2 has `3.00`; Manchester line 2 has `350`; Dublin line 2 has `5.25`. |
| 3 | Dublin is converted to GBP. | The direction is wrong. The first €5.25 item becomes round(525 × 1.1712) = 615 pence. A rate in EUR per GBP requires division: 525 / 1.1712 ≈ 448.26 pence, or £4.48. | `kettle/transform.py:31`; `data/raw/exchange_rates/2026-09-14.json:5`; Dublin CSV line 2. |
| 4 | Negative quantities are till mistakes. | This is an unsupported explanation. They are signed, normally priced product lines, consistent with refunds. Preserving them is necessary to reconcile Finance's net sales. | `kettle/transform.py:22`; Leeds CSV line 38 has Hot Chocolate, −1, £3.20; York line 12 has Americano, −1, £3.00. Neither file contains a reason field proving why a refund occurred. |
| 5 | Only exact duplicates are removed. | False. The key is branch, timestamp and title-cased product. It ignores transaction, till, quantity and price, so distinct sales disappear. | `kettle/transform.py:35`; Leeds CSV lines 35 and 36 are different transaction IDs selling Flat White in the same minute. |
| 6 | Product names are matched to the catalogue. | False. The code only strips whitespace and applies `.title()`. `read_products` has no caller. | `kettle/transform.py:33`; `kettle/extract.py:13`; original `pipeline.py` imports and calls. |
| 7 | Bad rows are handled gracefully. | They are silently discarded. `int("two")` raises; a bare exception handler suppresses it, without a log, count or rejection record. | Leeds CSV line 218; `kettle/transform.py:23`, `:50`. |
| 8 | UK dates are day first. | Correct for Leeds and York. `01/02/2026` means 1 February. | `kettle/transform.py:17–18`; the supplied timestamp tests. |
| 9 | The handover's pip/python commands are the right setup. | They are not reliable for this project's environment. This machine's default Python is 3.14; the repo selects 3.12 and uv installs the project's development dependencies. The uv commands were run successfully. | `.python-version:1`; `pyproject.toml`; README setup; baseline terminal log. |
| 10 | A server emails the summary at 6am. | Cannot be confirmed from this repository. There is no email sender or scheduler definition here. Inspect the old server's scheduled jobs, mail configuration, delivery logs and recipients with its owner. | Original `pipeline.py:25–29` only loads and writes a CSV; no mail/scheduler code was found. |

The handover is right that the Z-reports are not pipeline inputs and that the
loader replaces the requested date. Its broad claim that the pipeline is in
good shape is contradicted by silent data loss and unreconciled totals.

## Maintenance smells and reflection

- The bare `except` hides both invalid input and programming errors. Replace it
  with explicit validation and rejection records.
- `extract.py:8` opens a file without a context manager. The completed version
  closes CSV and JSONL streams using `with`.
- Branch-specific rules are scattered. The completed version uses one registry
  and a shared cleaning path.
- Floating-point price handling, positive-only quantities, the duplicate key
  and unused catalogue all need behavioural tests.
- SQLite is appropriate for this small exercise. Its presence alone is not a
  reason to replace the database or introduce a larger framework.

Trust comes from inspected code, hand calculations, tests that fail before a
fix, and independent reconciliation. The comments and handover repeat the same
incorrect refund explanation; an agent can copy a confident comment without
checking its business meaning. Andy should have verified each claim before
publishing the handover. No email schedule can be inferred from CSV generation.

The loyalty file's name was listed, but its contents were never opened or used.
There was no second learner to compare answers with, and no claim is made about
how long a human would have taken without an agent.
