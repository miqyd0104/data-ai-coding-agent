from kettle.transform import clean_rows


def test_kc102_refunds_reduce_quantity_and_revenue():
    row = ["L1", "14/09/2026 09:00", "T1", "Latte", "-2", "3.50"]
    sale = clean_rows([row], "leeds")[0]
    assert sale["quantity"] == -2
    assert sale["line_total_pence"] == -700


def test_kc102_separate_sales_in_same_minute_are_preserved():
    rows = [
        ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.50"],
        ["L2", "14/09/2026 09:00", "T2", "Latte", "1", "3.50"],
        ["L1", "14/09/2026 09:00", "T1", "Latte", "2", "3.50"],
        ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.40"],
    ]
    assert len(clean_rows(rows, "leeds")) == 4
