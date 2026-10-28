import csv
import sqlite3
from decimal import Decimal

import pytest

from kettle.extract import read_products, read_till_export
from kettle.pipeline import run
from kettle.report import build_product_summary, build_summary, write_product_summary
from kettle.transform import clean_rows

FIELDS = ["date", "branch", "product", "category", "items_sold", "revenue_gbp"]


def sale(branch="leeds", product="Latte", quantity=1, total=350, transaction="L1"):
    return {
        "branch": branch,
        "product": product,
        "quantity": quantity,
        "line_total_pence": total,
        "transaction_id": transaction,
    }


def test_product_groups_use_catalogue_and_till_prices(products):
    rows = [
        sale("york", "Latte", 1, 400),
        sale("leeds", "Latte", 2, 700),
        sale("leeds", "Flat White", 1, 340),
        sale("leeds", "Latte", 1, 350),
    ]
    assert build_product_summary(rows, "2026-09-14", products) == [
        {
            "date": "2026-09-14",
            "branch": "leeds",
            "product": "Flat White",
            "category": "Coffee",
            "items_sold": 1,
            "revenue_gbp": "3.40",
        },
        {
            "date": "2026-09-14",
            "branch": "leeds",
            "product": "Latte",
            "category": "Coffee",
            "items_sold": 3,
            "revenue_gbp": "10.50",
        },
        {
            "date": "2026-09-14",
            "branch": "york",
            "product": "Latte",
            "category": "Coffee",
            "items_sold": 1,
            "revenue_gbp": "4.00",
        },
    ]


def test_product_refunds_and_zero_net_groups(products):
    rows = [
        sale(quantity=2, total=700),
        sale(quantity=-2, total=-700),
        sale(product="Croissant", quantity=-1, total=-260),
    ]
    summary = build_product_summary(rows, "2026-09-14", products)
    assert [(row["product"], row["items_sold"], row["revenue_gbp"]) for row in summary] == [
        ("Croissant", -1, "-2.60"),
        ("Latte", 0, "0.00"),
    ]


def test_product_money_is_exact_even_above_float_precision(products):
    rows = [sale(total=9007199254740993)]
    assert build_product_summary(rows, "2026-09-14", products)[0]["revenue_gbp"] == (
        "90071992547409.93"
    )
    assert build_summary(rows, "2026-09-14")[0]["revenue_gbp"] == "90071992547409.93"


def test_unknown_products_do_not_reach_product_report(products):
    rejected = []
    rows = [["L1", "14/09/2026 09:00", "T1", "Mocha", "1", "3.40"]]
    cleaned = clean_rows(rows, "leeds", products=products, rejected=rejected)
    assert build_product_summary(cleaned, "2026-09-14", products) == []
    assert rejected[0]["reason"] == "Unknown or blank product"


def test_skus_and_aliases_share_canonical_names(products, tmp_path):
    rows = [["L1", "16/09/2026 09:00", "T1", "flat-wht", "1", "3.40"]]
    leeds = clean_rows(rows, "leeds", products=products)
    tills = tmp_path / "raw/tills"
    tills.mkdir(parents=True)
    (tills / "edinburgh_2026-09-16.jsonl").write_text(
        '{"transaction_id":"E1","timestamp":"2026-09-16T09:00:00",'
        '"till":"T1","items":[{"sku":"FW01","qty":1,"price_pence":340}]}\n'
    )
    edinburgh = clean_rows(
        read_till_export(tmp_path, "edinburgh", "2026-09-16", products),
        "edinburgh",
        products=products,
    )
    report = build_product_summary(leeds + edinburgh, "2026-09-16", products)
    assert {row["product"] for row in report} == {"Flat White"}
    assert {row["category"] for row in report} == {"Coffee"}


def test_empty_product_summary_is_header_only(tmp_path, products):
    assert build_product_summary([], "2026-09-14", products) == []
    path = write_product_summary([], tmp_path, "2026-09-14")
    with open(path, encoding="utf-8", newline="") as stream:
        assert list(csv.reader(stream)) == [FIELDS]


def test_product_csv_has_exact_header_and_is_replaced(tmp_path, products):
    report = build_product_summary([sale()], "2026-09-14", products)
    path = write_product_summary(report, tmp_path, "2026-09-14")
    with open(path, encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == FIELDS
        assert len(list(reader)) == 1
    write_product_summary([], tmp_path, "2026-09-14")
    with open(path, encoding="utf-8", newline="") as stream:
        assert list(csv.reader(stream)) == [FIELDS]


@pytest.mark.parametrize("date", ["2026-09-14", "2026-09-15", "2026-09-16"])
def test_product_totals_equal_daily_and_warehouse(tmp_path, date):
    daily = run(date, output_dir=tmp_path)
    with (tmp_path / f"product_summary_{date}.csv").open(encoding="utf-8") as stream:
        product_rows = list(csv.DictReader(stream))
    catalogue = {product["name"]: product["category"] for product in read_products("data")}
    assert [(row["branch"], row["product"]) for row in product_rows] == sorted(
        (row["branch"], row["product"]) for row in product_rows
    )
    assert {row["branch"] for row in product_rows} == {row["branch"] for row in daily}
    with sqlite3.connect(tmp_path / "warehouse.db") as database:
        for branch in daily:
            rows = [row for row in product_rows if row["branch"] == branch["branch"]]
            assert sum(int(row["items_sold"]) for row in rows) == branch["items_sold"]
            assert sum(Decimal(row["revenue_gbp"]) for row in rows) == Decimal(
                branch["revenue_gbp"]
            )
            for row in rows:
                assert row["date"] == date
                assert row["category"] == catalogue[row["product"]]
                actual = database.execute(
                    "SELECT SUM(quantity), SUM(line_total_pence) FROM sales "
                    "WHERE branch = ? AND product = ? AND substr(sold_at, 1, 10) = ?",
                    (row["branch"], row["product"], date),
                ).fetchone()
                assert actual == (int(row["items_sold"]), int(Decimal(row["revenue_gbp"]) * 100))


def test_reports_and_other_days_survive_rerun(tmp_path):
    run("2026-09-14", output_dir=tmp_path)
    run("2026-09-15", output_dir=tmp_path)
    names = [
        f"{kind}_{date}.csv"
        for kind in ["daily_summary", "product_summary"]
        for date in ["2026-09-14", "2026-09-15"]
    ]
    before = {name: (tmp_path / name).read_bytes() for name in names}
    with sqlite3.connect(tmp_path / "warehouse.db") as database:
        sales_before = database.execute(
            "SELECT * FROM sales ORDER BY sold_at, branch, product"
        ).fetchall()
    run("2026-09-14", output_dir=tmp_path)
    assert before == {name: (tmp_path / name).read_bytes() for name in names}
    with sqlite3.connect(tmp_path / "warehouse.db") as database:
        assert database.execute(
            "SELECT * FROM sales ORDER BY sold_at, branch, product"
        ).fetchall() == (sales_before)
