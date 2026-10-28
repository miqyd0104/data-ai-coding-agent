import json

from kettle.extract import read_products, read_till_export
from kettle.pipeline import run


def test_kc104_jsonl_transactions_are_flattened_into_shared_rows(tmp_path):
    tills = tmp_path / "raw" / "tills"
    tills.mkdir(parents=True)
    transaction = {
        "transaction_id": "E1", "timestamp": "2026-09-16T09:00:00", "till": "T1",
        "items": [{"sku": "FW01", "qty": 2, "price_pence": 340},
                  {"sku": "CR01", "qty": 1, "price_pence": 260}],
    }
    (tills / "edinburgh_2026-09-16.jsonl").write_text(json.dumps(transaction) + "\n")
    rows = read_till_export(tmp_path, "edinburgh", "2026-09-16",
                            products=read_products("data"))
    assert rows == [
        ["E1", "2026-09-16T09:00:00", "T1", "Flat White", "2", "340"],
        ["E1", "2026-09-16T09:00:00", "T1", "Croissant", "1", "260"],
    ]


def test_kc104_edinburgh_is_optional_before_opening(tmp_path):
    summary = run("2026-09-14", output_dir=tmp_path)
    assert {row["branch"] for row in summary} == {"leeds", "manchester", "york", "dublin"}


def test_kc104_edinburgh_reconciles_on_opening_day(tmp_path):
    summary = run("2026-09-16", output_dir=tmp_path)
    edinburgh = next(row for row in summary if row["branch"] == "edinburgh")
    assert edinburgh == {
        "date": "2026-09-16", "branch": "edinburgh", "transactions": 120,
        "items_sold": 207, "revenue_gbp": "664.00",
    }
