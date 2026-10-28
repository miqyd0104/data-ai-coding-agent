from kettle.transform import clean_rows
from kettle.pipeline import run
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
import csv
import json
import sqlite3
import pytest


def test_kc102_refunds_reduce_quantity_and_revenue(products):
    row = ["L1", "14/09/2026 09:00", "T1", "Latte", "-2", "3.50"]
    sale = clean_rows([row], "leeds", products=products)[0]
    assert sale["quantity"] == -2
    assert sale["line_total_pence"] == -700


def test_kc102_separate_sales_in_same_minute_are_preserved(products):
    rows = [
        ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.50"],
        ["L2", "14/09/2026 09:00", "T2", "Latte", "1", "3.50"],
        ["L1", "14/09/2026 09:00", "T1", "Latte", "2", "3.50"],
        ["L1", "14/09/2026 09:00", "T1", "Latte", "1", "3.40"],
    ]
    assert len(clean_rows(rows, "leeds", products=products)) == 4


@pytest.mark.parametrize("date", ["2026-09-14", "2026-09-15", "2026-09-16"])
def test_every_branch_matches_finance_z_reports_to_the_penny(tmp_path, date):
    with open("data/raw/z_reports.csv", encoding="utf-8") as stream:
        expected = [row for row in csv.DictReader(stream) if row["date"] == date]
    rate = Decimal(str(json.loads(
        Path(f"data/raw/exchange_rates/{date}.json").read_text()
    )["rates"]["EUR"]))
    actual = {row["branch"]: row for row in run(date, output_dir=tmp_path)}
    assert set(actual) == {row["branch"] for row in expected}
    for row in expected:
        summary = actual[row["branch"]]
        revenue = Decimal(row["net_sales"])
        if row["currency"] == "EUR":
            revenue = (revenue / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        assert summary["transactions"] == int(row["transactions"])
        assert summary["items_sold"] == int(row["items_sold"])
        assert summary["revenue_gbp"] == f"{revenue:.2f}"
    # Re-running must replace the day, while preserving all other days.
    with sqlite3.connect(tmp_path / "warehouse.db") as database:
        before = database.execute("SELECT * FROM sales ORDER BY rowid").fetchall()
    assert run(date, output_dir=tmp_path) == list(actual.values())
    with sqlite3.connect(tmp_path / "warehouse.db") as database:
        assert database.execute("SELECT * FROM sales ORDER BY rowid").fetchall() == before
