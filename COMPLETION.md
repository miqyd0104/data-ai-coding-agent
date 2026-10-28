# Completed exercise work

Completed locally on 28 October 2026 using Codex's terminal tools. The coding
tasks, all four KC tickets, stretch fixes, Glasgow workflow example and product
report are implemented. **106 tests pass**, and all **13 supplied branch/day
records reconcile** to Finance's transaction counts, net quantities and revenue.

The Claude-specific interactive learning demonstrations remain unperformed:
Claude Code is not installed here. Permission settings are prepared, the hook
was tested directly, and no Claude session behaviour is claimed. Details are
recorded in the exercise 02 and 04 answers below. Changes are committed locally;
they have not been pushed to GitHub.

## Run it

From this repository's directory:

```sh
uv run pytest -q
uv run python -m kettle 2026-09-14
uv run python -m kettle 2026-09-15
uv run python -m kettle 2026-09-16
```

Each day writes three CSVs under `output/` plus `output/warehouse.db`:

- `daily_summary_<date>.csv`: branch transactions, net items and GBP revenue.
- `product_summary_<date>.csv`: branch/product/category net sales.
- `rejected_rows_<date>.csv`: invalid-row reasons, without copied raw contents.

All three fixture dates have already been run. Generated reports remain ignored
by Git and can be recreated with the commands above.

## Exercise answers and evidence

| Exercise | Result |
| --- | --- |
| [01: Codebase and handover](docs/exercises/01-codebase-and-handover.md) | Row walkthrough, ten-claim fact check, evidence and maintenance assessment |
| [02: First changes](docs/exercises/02-first-changes.md) | Four helper commits, original tests preserved, price precision demonstration |
| [03: TDD and reconciliation](docs/exercises/03-tdd-and-reconciliation.md) | Characterisation, red/green fixes, KC-101 through KC-104 and all stretch tasks |
| [04: Context and guards](docs/exercises/04-context-and-guards.md) | AGENTS.md, validated till skill, Glasgow, protected-path configuration and tested hook |
| [05: Product report](docs/exercises/05-product-summary.md) | Approved specification, acceptance mapping, CSV implementation and integration checks |

The local branches are cumulative: `exercise-02` → `exercise-03` → `exercise-04`
→ **`exercise-05`**, which is the final active branch. `main` retains the original
starting point. Use `git log --oneline` to review the separate commits.

Terminal evidence is in `docs/validation/`: the original 39 failures, targeted
red/green runs, the intentional hook failure, final pipeline runs, reconciliation
table and raw-data integrity check. The supplied helper and smoke tests and all
raw inputs are unchanged. The loyalty-members file was not opened.

## Verified figures

| Date | Branch | Transactions | Net items | GBP revenue |
| --- | --- | ---: | ---: | ---: |
| 14 Sep 2026 | Leeds | 138 | 245 | 759.70 |
| 14 Sep 2026 | Manchester | 162 | 280 | 874.30 |
| 14 Sep 2026 | York | 120 | 206 | 651.10 |
| 14 Sep 2026 | Dublin | 120 | 218 | 675.25 |
| 15 Sep 2026 | Leeds | 150 | 261 | 822.20 |
| 15 Sep 2026 | Manchester | 183 | 332 | 1056.80 |
| 15 Sep 2026 | York | 106 | 189 | 599.10 |
| 15 Sep 2026 | Dublin | 128 | 222 | 710.98 |
| 16 Sep 2026 | Leeds | 125 | 212 | 642.00 |
| 16 Sep 2026 | Manchester | 159 | 289 | 910.60 |
| 16 Sep 2026 | York | 100 | 186 | 589.30 |
| 16 Sep 2026 | Dublin | 117 | 208 | 651.68 |
| 16 Sep 2026 | Edinburgh | 120 | 207 | 664.00 |

Glasgow has only synthetic test data, so it appears in no supplied-date report.
Dublin's GBP figures use that day's EUR-per-GBP rate and the documented penny
allocation. No email delivery or external scheduler was configured or verified.
The original `HANDOVER.md` remains an intentionally inaccurate teaching artifact;
use these answers and `AGENTS.md` for the corrected rules.
