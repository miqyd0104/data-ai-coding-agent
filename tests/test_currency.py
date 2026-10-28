from kettle.transform import clean_rows


def test_kc101_eur_per_gbp_is_divided_not_multiplied():
    # EUR 11.71 / 1.1712 = GBP 9.99829..., rounded to GBP 10.00.
    row = ["2026-09-14T09:00:00", "Latte", "11.71", "1", "T1", "D1"]
    sale = clean_rows([row], "dublin", 1.1712)[0]
    assert sale["unit_price_pence"] == 1000
    assert sale["line_total_pence"] == 1000
