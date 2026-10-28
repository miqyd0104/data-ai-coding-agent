from datetime import datetime
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal, InvalidOperation

from kettle.branches import BRANCHES


def clean_rows(rows, branch, eur_rate=None, *, products, rejected=None, date=None):
    """Validate till rows, preserve refunds, and remove exact duplicate sales.

    Rejection metadata deliberately excludes raw row contents and customer data.
    """
    config = BRANCHES[branch]
    rate = None
    if config["currency"] == "EUR":
        try:
            rate = Decimal(str(eur_rate))
        except InvalidOperation as error:
            raise ValueError("A positive EUR-per-GBP rate is required") from error
        if not rate.is_finite() or rate <= 0:
            raise ValueError("A positive EUR-per-GBP rate is required")
    cleaned = []
    source_totals = []
    seen = set()
    for row_number, row in enumerate(rows, 1):
        try:
            if not row:
                continue
            if len(row) != 6:
                raise ValueError("Expected six till fields")
            txn_id, ts, till, product, qty, price = (
                row[index] for index in config.get("columns", range(6))
            )
            txn_id, till = txn_id.strip(), till.strip()
            if not txn_id or not till:
                raise ValueError("Missing transaction or till ID")
            sold_at = parse_till_timestamp(ts)
            if date is not None and sold_at.date().isoformat() != date:
                raise ValueError("Timestamp does not match processing date")
            try:
                qty = int(qty)
            except (ValueError, TypeError) as error:
                raise ValueError("Invalid quantity") from error
            source_price = parse_price_to_pence(price, config["price_unit"])
            if source_price < 0:
                raise ValueError("Unit price must not be negative")
            product = normalise_product_name(product, products)
            if product is None:
                raise ValueError("Unknown or blank product")
            key = (branch, txn_id, sold_at, till, product, qty, source_price)
            if key in seen:
                continue
            seen.add(key)
            price_pence = source_price
            if rate is not None:
                price_pence = int(
                    (Decimal(source_price) / rate).quantize(Decimal(1), rounding=ROUND_HALF_UP)
                )
            cleaned.append(
                {
                    "transaction_id": txn_id,
                    "branch": branch,
                    "sold_at": sold_at.isoformat(),
                    "till_id": till,
                    "product": product,
                    "quantity": qty,
                    "unit_price_pence": price_pence,
                    "line_total_pence": qty * price_pence,
                }
            )
            source_totals.append(qty * source_price)
        except (ValueError, TypeError) as error:
            if rejected is not None:
                rejected.append({"branch": branch, "row_number": row_number, "reason": str(error)})
    if rate is not None and cleaned:
        _allocate_fx_pennies(cleaned, source_totals, rate)
    return cleaned


def _allocate_fx_pennies(rows, source_totals, rate):
    """Largest-remainder allocation, including refunds, of the rounded day total.

    Each line differs from its exact conversion by less than one penny. Stable
    transaction keys break ties so changing input order cannot change a sale.
    """
    exact = [Decimal(total) / rate for total in source_totals]
    allocated = [int(total.to_integral_value(rounding=ROUND_FLOOR)) for total in exact]
    target = int((Decimal(sum(source_totals)) / rate).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    order = sorted(
        range(len(rows)),
        key=lambda index: (
            -(exact[index] - allocated[index]),
            rows[index]["transaction_id"],
            rows[index]["till_id"],
            rows[index]["sold_at"],
            rows[index]["product"],
            rows[index]["quantity"],
            source_totals[index],
        ),
    )
    for index in order[: target - sum(allocated)]:
        allocated[index] += 1
    for row, total in zip(rows, allocated):
        row["line_total_pence"] = total


def format_pence(pence):
    """Format an integer number of pence as a pounds string for reports.

    >>> format_pence(340)
    '£3.40'
    >>> format_pence(-120)
    '-£1.20'
    """
    sign = "-" if pence < 0 else ""
    pounds, pennies = divmod(abs(pence), 100)
    return f"{sign}£{pounds}.{pennies:02d}"


def parse_price_to_pence(value, unit):
    """Turn a till price string into an integer number of pence (or cents).

    `unit` is "pounds" for tills that export prices like "3.40" and "pence"
    for tills that export prices like "340". Surrounding whitespace is ignored.
    Raise ValueError if the value is not a valid price (including fractions
    of a penny, e.g. "3.405" pounds or "340.5" pence).
    """
    if unit not in {"pounds", "pence"}:
        raise ValueError(f"Unknown price unit: {unit}")
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation as error:
        raise ValueError("Invalid price") from error
    if not amount.is_finite():
        raise ValueError("Price must be finite")
    pence = amount * (100 if unit == "pounds" else 1)
    if pence != pence.to_integral_value():
        raise ValueError("Price contains a fraction of a penny")
    return int(pence)


def parse_till_timestamp(value):
    """Parse a till timestamp into a datetime.

    Accepts the UK format "14/09/2026 08:15" (day first!) and ISO 8601
    ("2026-09-14T08:15:00"). Surrounding whitespace is ignored.
    Raise ValueError for anything else.
    """
    value = value.strip()
    if "/" in value:
        return datetime.strptime(value, "%d/%m/%Y %H:%M")
    if "T" not in value:
        raise ValueError("Expected a UK timestamp or ISO date and time")
    return datetime.fromisoformat(value)


def normalise_product_name(raw_name, products):
    """Match a messy till product name to its canonical catalogue name.

    `products` is the list loaded from data/reference/products.json. Matching
    ignores case, surrounding whitespace and hyphens-vs-spaces, and also
    checks each product's aliases. Return None if there is no match.

    >>> normalise_product_name(" flat-white ", products)
    'Flat White'
    """

    def match_key(name):
        return " ".join(name.replace("-", " ").split()).casefold()

    if not isinstance(raw_name, str) or not raw_name.strip():
        return None
    key = match_key(raw_name)
    for product in products:
        names = [product["name"], *product.get("aliases", [])]
        if any(key == match_key(name) for name in names):
            return product["name"]
    return None
