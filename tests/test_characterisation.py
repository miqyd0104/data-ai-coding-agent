"""Small snapshots of the inherited behaviour; BUG comments flag known defects."""

from kettle.report import build_summary
from kettle.transform import clean_rows


def test_leeds_row_shape_and_day_first_timestamp():
    rows = [["L1", "01/02/2026 09:00", "T1", " flat white ", "2", "3.40"]]
    assert clean_rows(rows, "leeds") == [{
        "transaction_id": "L1", "branch": "leeds", "sold_at": "2026-02-01T09:00:00",
        "till_id": "T1", "product": "Flat White", "quantity": 2,
        "unit_price_pence": 340, "line_total_pence": 680,
    }]


def test_manchester_prices_are_already_pence():
    row = ["M1", "2026-09-14T09:00:00", "T2", "Latte", "2", "350"]
    assert clean_rows([row], "manchester")[0]["line_total_pence"] == 700


def test_dublin_inherited_conversion():
    row = ["2026-09-14T09:00:00", "Latte", "11.71", "1", "T1", "D1"]
    # BUG: KC-101 multiplies by EUR per GBP, inflating the price.
    assert clean_rows([row], "dublin", 1.1712)[0]["unit_price_pence"] == 1371


def test_inherited_negative_quantity():
    row = ["L1", "14/09/2026 09:00", "T1", "Latte", "-1", "3.50"]
    # BUG: KC-102 treats a refund as a sale.
    assert clean_rows([row], "leeds")[0]["line_total_pence"] == 350


def test_inherited_deduplication_collision():
    rows = [
        ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.50"],
        ["L2", "14/09/2026 09:00", "T2", "Latte", "1", "3.50"],
    ]
    # BUG: KC-102 drops a distinct transaction in the same minute.
    assert len(clean_rows(rows, "leeds")) == 1


def test_exact_export_duplicate_is_removed():
    row = ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.50"]
    assert len(clean_rows([row, row.copy()], "leeds")) == 1


def test_bad_quantity_is_skipped():
    row = ["L1", "14/09/2026 09:00", "T1", "Latte", "two", "3.50"]
    assert clean_rows([[], row], "leeds") == []


def test_summary_counts_transactions_once_and_sums_lines():
    rows = [
        {"branch": "leeds", "transaction_id": "L1", "quantity": 2,
         "line_total_pence": 680},
        {"branch": "leeds", "transaction_id": "L1", "quantity": 1,
         "line_total_pence": 220},
        {"branch": "york", "transaction_id": "Y1", "quantity": -1,
         "line_total_pence": -350},
    ]
    assert build_summary(rows, "2026-09-14") == [
        {"date": "2026-09-14", "branch": "leeds", "transactions": 1,
         "items_sold": 3, "revenue_gbp": "9.00"},
        {"date": "2026-09-14", "branch": "york", "transactions": 1,
         "items_sold": -1, "revenue_gbp": "-3.50"},
    ]


def test_summary_with_no_sales_is_empty():
    assert build_summary([], "2026-09-14") == []
