import pytest

from kettle.transform import clean_rows, parse_price_to_pence


def test_kc103_catalogue_alias_is_used_in_warehouse_rows(products):
    row = ["L1", "14/09/2026 09:00", "T1", " flat-wht ", "1", "3.40"]
    assert clean_rows([row], "leeds", products=products)[0]["product"] == "Flat White"


@pytest.mark.parametrize("name", ["", "Mocha"])
def test_kc103_unknown_names_are_rejected_with_reason(products, name):
    rejected = []
    row = ["L1", "14/09/2026 09:00", "T1", name, "1", "3.40"]
    assert clean_rows([row], "leeds", products=products, rejected=rejected) == []
    assert rejected == [{"branch": "leeds", "row_number": 1, "reason": "Unknown or blank product"}]


@pytest.mark.parametrize(
    "index,value,reason",
    [
        (4, "two", "Invalid quantity"),
        (5, "3.405", "Price contains a fraction of a penny"),
        (5, "NaN", "Price must be finite"),
        (5, "-3.40", "Unit price must not be negative"),
        (0, "", "Missing transaction or till ID"),
        (2, "", "Missing transaction or till ID"),
        (1, "15/09/2026 09:00", "Timestamp does not match processing date"),
    ],
)
def test_invalid_rows_are_reported_and_valid_rows_survive(products, index, value, reason):
    good = ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.50"]
    bad = good.copy()
    bad[index] = value
    rejected = []
    cleaned = clean_rows(
        [bad, good], "leeds", products=products, rejected=rejected, date="2026-09-14"
    )
    assert len(cleaned) == 1
    assert rejected == [{"branch": "leeds", "row_number": 1, "reason": reason}]


@pytest.mark.parametrize(
    "value,unit", [("NaN", "pounds"), ("Infinity", "pence"), ("3.40", "euros")]
)
def test_price_parser_rejects_nonfinite_and_unknown_units(value, unit):
    with pytest.raises(ValueError):
        parse_price_to_pence(value, unit)
