# Kettle & Crumb working rules

- Use `uv run` for Python commands; never install packages with `pip` here.
- UK till dates are day first. Negative quantities are refunds, not mistakes.
- Store money as integer pence; use Decimal for parsing and currency conversion.
- Rates are EUR per GBP: divide euros by the rate. Round the branch/day total
  half up and allocate the remaining pennies across lines deterministically.
- Never modify `data/raw/` or read `data/raw/loyalty_members.csv`.
- Reject unknown products with a recorded reason; do not guess names or prices.
- Run `uv run pytest` before every commit. Keep the supplied helper tests unchanged.
