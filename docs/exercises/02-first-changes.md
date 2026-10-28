# Exercise 02: helpers and review

Created the local `exercise-02` branch and committed the four helpers separately:

| Commit | Change | Verification at that point |
| --- | --- | --- |
| `70520ba` | Integer pence formatting, including negative amounts | 6 formatting tests passed |
| `0c748c1` | UK day-first and ISO timestamps | 8 timestamp tests passed |
| `49e4b26` | Catalogue names, aliases, hyphens and whitespace | 12 name tests passed |
| `b2cd084` | Exact price parsing with Decimal | All 40 original tests passed |

The plan for prices was to parse decimal strings exactly, multiply pounds by
100, require a whole number of pence, then convert to `int`. An actual shell
calculation confirmed that `int(float("4.35") * 100)` gives **434**, and the same
pattern for `0.29` gives **28**. Decimal avoids both errors and rejects fractional
pennies rather than silently truncating them.

The supplied `tests/test_transform.py` was not edited. The original smoke test
was also left unchanged. Every helper commit was reviewed with Git, and the
saved logs in `docs/validation/02-*.txt` record the test results.

At the end of exercise 02 the helpers existed but `clean_rows` still did not
use them. KC-103 later connected them to the real pipeline.

## Permission-mode reflection

The terminal work was performed by Codex. Claude Code is not installed, so the
interactive Shift+Tab/manual/accept-edits/auto/plan comparisons were **not run**.
They cannot honestly be described as completed Claude sessions.

Manual review is useful when learning an unfamiliar repository or inspecting a
sensitive command. Accepting edits still requires reviewing the entire diff.
Automatic execution needs tests and bounded permissions. Planning is useful
when money rules, assumptions or a larger design need agreement before edits.
Passing tests are not enough if the agent changes the tests to match its code;
the unchanged original test files and Git history provide an independent check.
