import csv
import json
from pathlib import Path

from kettle.pipeline import run


def test_add_till_skill_glasgow_reuses_leeds_format(tmp_path):
    data = tmp_path / "data"
    tills = data / "raw/tills"
    tills.mkdir(parents=True)
    (data / "reference").mkdir()
    (data / "reference/products.json").write_text(
        Path("data/reference/products.json").read_text()
    )
    rates = data / "raw/exchange_rates"
    rates.mkdir()
    (rates / "2026-09-17.json").write_text(json.dumps({
        "base": "GBP", "date": "2026-09-17", "rates": {"EUR": 1.2},
    }))
    header = "transaction_id,timestamp,till_id,product,quantity,unit_price\n"
    for branch in ["leeds", "manchester", "york", "dublin"]:
        (tills / f"{branch}_2026-09-17.csv").write_text(header)
    rows = [
        ["G1", "17/09/2026 09:00", "T1", "flat wht", "2", "3.40"],
        ["G1", "17/09/2026 09:00", "T1", "Croissant", "1", "2.60"],
        ["G1", "17/09/2026 09:00", "T1", "flat wht", "2", "3.40"],
        ["G2", "17/09/2026 09:00", "T2", "Flat White", "-1", "3.40"],
        ["G3", "17/09/2026 09:00", "T1", "Mocha", "1", "3.40"],
        ["G4", "17/09/2026 09:00", "T2", "Flat White", "1", "3.40"],
    ]
    with (tills / "glasgow_2026-09-17.csv").open("w", newline="") as stream:
        stream.write(header)
        csv.writer(stream).writerows(rows)
    summary = run("2026-09-17", data_dir=data, output_dir=tmp_path / "output")
    assert summary == [{"date": "2026-09-17", "branch": "glasgow", "transactions": 3,
                        "items_sold": 3, "revenue_gbp": "9.40"}]
    with (tmp_path / "output/rejected_rows_2026-09-17.csv").open() as stream:
        rejected = list(csv.DictReader(stream))
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "Unknown or blank product"


def test_glasgow_without_an_export_is_omitted(tmp_path):
    summary = run("2026-09-14", output_dir=tmp_path)
    assert "glasgow" not in {row["branch"] for row in summary}
