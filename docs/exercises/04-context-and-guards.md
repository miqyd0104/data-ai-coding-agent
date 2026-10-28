# Exercise 04: context, skills and guards

Work continued on local branch `exercise-04`.

`AGENTS.md` contains concise business and working rules: day-first dates, signed
refunds, integer pence, FX direction/rounding, protected raw/customer data,
unknown-product rejection and tests before commits. It avoids duplicating a
folder inventory. `CLAUDE.md` imports it for Claude installations using that
instruction-file convention. The import syntax is documented in
[Claude's memory reference](https://code.claude.com/docs/en/memory#import-additional-files).

The task-specific skill is `.claude/skills/add-till-format/SKILL.md`. It describes
the registry and adapter boundary, missing opening-day files, synthetic tests,
refunds, duplicate identity, unknown SKUs and reconciliation. Its structure was
checked with the skill-creator validator.

To exercise that workflow, Glasgow was added with one registry entry using the
existing Leeds CSV parser. Synthetic files were created only in a temporary test
directory. A failing test became green and checks aliases, multiple items,
refunds, exact duplicates, distinct sales in one minute, unknown products and
absence before opening. No Glasgow business data or Z-report was invented.
This tests the workflow and implementation; it does not prove a fresh Claude
session would automatically discover and invoke the skill.

## Guards implemented and verified

`.claude/settings.json` keeps manual mode and adds:

```json
"deny": ["Edit(./data/raw/**)", "Read(./data/raw/loyalty_members.csv)"]
```

A PostToolUse hook for Claude's Edit/Write tools calls
`.claude/hooks/test-python-edit.py`. For Python paths it locates the checkout,
runs `uv run pytest -q`, and returns failures using the documented hook response.
The hook was invoked directly with a real temporary failing test. It reported
the failure, the test was removed in a `finally` block, and the restored suite
passed. Unit tests additionally cover successful runs, non-Python edits, missing
uv and timeouts. See `04-hook-catches-real-failure.json`.

The hook supplies feedback after an edit; it cannot undo that edit. A matcher
for Edit/Write does not run after arbitrary shell edits. Those boundaries follow
the [official hook reference](https://code.claude.com/docs/en/hooks#posttooluse).

The deny rules are configured, but their enforcement by a running Claude client
was **not tested**, because no `claude` executable is installed. No protected
file was modified or read to fake that demonstration. The published
[permission rules](https://code.claude.com/docs/en/permissions#read-and-edit)
describe tool checks and their limits; indirect subprocess file access needs
operating-system restrictions for complete enforcement. This project's rules
are not a general process-level file-access boundary and do not govern Codex.

## Reflection and remaining interactive checks

Stable business rules belong in AGENTS.md; a reusable task procedure belongs in
a skill; a repeatable mechanical check belongs in a guard. Tests are executable
evidence, whereas telling an agent to be careful is only an instruction.
Commit shared `.claude/settings.json`; keep personal `.claude/settings.local.json`
ignored, as this repo already does.

The following exact exercise demonstrations remain for an authenticated Claude
session: clear context and compare its test-command answer; confirm skill
auto-selection; attempt the protected raw edit and customer-data read and observe
denial. They were not simulated or claimed as successful. The expected command
answer from the completed project instructions is `uv run pytest`.
