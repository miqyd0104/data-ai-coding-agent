import pytest

from kettle.transform import clean_rows


def test_kc101_eur_per_gbp_is_divided_not_multiplied(products):
    # EUR 11.71 / 1.1712 = GBP 9.99829..., rounded to GBP 10.00.
    row = ["2026-09-14T09:00:00", "Latte", "11.71", "1", "T1", "D1"]
    sale = clean_rows([row], "dublin", 1.1712, products=products)[0]
    assert sale["unit_price_pence"] == 1000
    assert sale["line_total_pence"] == 1000


def test_kc102_rounds_branch_total_once_and_allocates_fx_pennies(products):
    # 3 x EUR 0.01 / 1.5 = GBP 0.02; per-unit rounding incorrectly gives GBP 0.03.
    rows = [["2026-09-14T09:00:00", "Latte", "0.01", "1", "T1", f"D{i}"] for i in range(3)]
    cleaned = clean_rows(rows, "dublin", "1.5", products=products)
    assert sum(row["line_total_pence"] for row in cleaned) == 2
    assert sorted(row["line_total_pence"] for row in cleaned) == [0, 1, 1]
    reversed_cleaned = clean_rows(rows[::-1], "dublin", "1.5", products=products)
    assert {row["transaction_id"]: row["line_total_pence"] for row in cleaned} == {
        row["transaction_id"]: row["line_total_pence"] for row in reversed_cleaned
    }


def test_kc102_fx_allocation_handles_refunds(products):
    # EUR 0.03 - EUR 0.01 = EUR 0.02; at 1.5 this rounds to GBP 0.01.
    rows = [
        ["2026-09-14T09:00:00", "Latte", "0.01", str(qty), "T1", f"D{i}"]
        for i, qty in enumerate([3, -1])
    ]
    cleaned = clean_rows(rows, "dublin", "1.5", products=products)
    assert sum(row["line_total_pence"] for row in cleaned) == 1
    assert cleaned[1]["line_total_pence"] <= 0


@pytest.mark.parametrize("rate", [None, "NaN", "Infinity", 0, -1])
def test_invalid_rate_fails_visibly_instead_of_dropping_every_sale(products, rate):
    with pytest.raises(ValueError, match="positive EUR-per-GBP"):
        clean_rows([], "dublin", rate, products=products)
