import os
from datetime import date as calendar_date

from kettle.branches import BRANCHES
from kettle.extract import read_eur_rate, read_products, read_till_export
from kettle.load import load_sales
from kettle.report import (
    build_product_summary,
    build_summary,
    write_product_summary,
    write_rejections,
    write_summary,
)
from kettle.transform import clean_rows


def run(date, data_dir="data", output_dir="output"):
    try:
        parsed_date = calendar_date.fromisoformat(date)
        if parsed_date.isoformat() != date:
            raise ValueError
    except (ValueError, TypeError) as error:
        raise ValueError("Processing date must be YYYY-MM-DD") from error
    os.makedirs(output_dir, exist_ok=True)
    products = read_products(data_dir)

    all_rows = []
    rejected = []
    for branch in BRANCHES:
        print("Processing " + branch + "...")
        rows = read_till_export(data_dir, branch, date, products=products, rejected=rejected)
        rate = None
        if BRANCHES[branch]["currency"] == "EUR":
            rate = read_eur_rate(data_dir, date)
        cleaned = clean_rows(rows, branch, rate, products=products, rejected=rejected, date=date)
        print("  " + str(len(cleaned)) + " rows")
        all_rows = all_rows + cleaned

    load_sales(all_rows, output_dir, date)
    summary = build_summary(all_rows, date)
    path = write_summary(summary, output_dir, date)
    write_product_summary(build_product_summary(all_rows, date, products), output_dir, date)
    write_rejections(rejected, output_dir, date)
    print(f"Rejected {len(rejected)} invalid rows; see rejected_rows_{date}.csv")
    print("Done! Summary written to " + path)
    return summary
