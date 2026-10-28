import json

import pytest

from kettle.extract import read_till_export
from kettle.pipeline import run
from kettle.transform import clean_rows


@pytest.mark.parametrize(
    "bad_line",
    [
        "{broken",
        "{}",
        "[]",
        '{"items": false}',
        '{"transaction_id":"E0","timestamp":"x","till":"T1","items":[{}]}',
    ],
)
def test_malformed_jsonl_is_reported_without_losing_next_transaction(tmp_path, products, bad_line):
    tills = tmp_path / "raw/tills"
    tills.mkdir(parents=True)
    good = {
        "transaction_id": "E1",
        "timestamp": "2026-09-16T09:00:00",
        "till": "T1",
        "items": [{"sku": "LT01", "qty": 1, "price_pence": 350}],
    }
    (tills / "edinburgh_2026-09-16.jsonl").write_text(bad_line + "\n" + json.dumps(good) + "\n")
    rejected = []
    rows = read_till_export(
        tmp_path, "edinburgh", "2026-09-16", products=products, rejected=rejected
    )
    assert rows == [["E1", "2026-09-16T09:00:00", "T1", "Latte", "1", "350"]]
    assert len(rejected) == 1
    assert rejected[0]["row_number"] == 1


def test_unknown_sku_is_rejected_instead_of_being_guessed(tmp_path, products):
    tills = tmp_path / "raw/tills"
    tills.mkdir(parents=True)
    transaction = {
        "transaction_id": "E1",
        "timestamp": "2026-09-16T09:00:00",
        "till": "T1",
        "items": [{"sku": "NOPE", "qty": 1, "price_pence": 350}],
    }
    (tills / "edinburgh_2026-09-16.jsonl").write_text(json.dumps(transaction) + "\n")
    rows = read_till_export(tmp_path, "edinburgh", "2026-09-16", products=products)
    rejected = []
    assert clean_rows(rows, "edinburgh", products=products, rejected=rejected) == []
    assert rejected[0]["reason"] == "Unknown or blank product"


def test_missing_required_till_export_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_till_export(tmp_path, "leeds", "2026-09-14")


@pytest.mark.parametrize("date", ["not-a-date", "2026-09-31", "20260914"])
def test_processing_date_must_be_iso_calendar_date(tmp_path, date):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        run(date, output_dir=tmp_path)
