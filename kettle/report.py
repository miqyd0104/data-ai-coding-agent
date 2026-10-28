import csv
import os

from kettle.transform import format_pence


def build_summary(rows, date):
    summary = {}
    for r in rows:
        b = r["branch"]
        if b not in summary:
            summary[b] = {"date": date, "branch": b, "txns": set(), "items_sold": 0, "revenue": 0}
        summary[b]["txns"].add(r["transaction_id"])
        summary[b]["items_sold"] += r["quantity"]
        summary[b]["revenue"] += r["line_total_pence"]

    result = []
    for s in summary.values():
        result.append(
            {
                "date": s["date"],
                "branch": s["branch"],
                "transactions": len(s["txns"]),
                "items_sold": s["items_sold"],
                "revenue_gbp": format_pence(s["revenue"]).replace("£", "", 1),
            }
        )
    return result


def write_summary(summary, output_dir, date):
    path = os.path.join(output_dir, "daily_summary_" + date + ".csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["date", "branch", "transactions", "items_sold", "revenue_gbp"]
        )
        w.writeheader()
        for row in summary:
            w.writerow(row)
    return path


def write_rejections(rejected, output_dir, date):
    path = os.path.join(output_dir, f"rejected_rows_{date}.csv")
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["date", "branch", "row_number", "reason"])
        writer.writeheader()
        writer.writerows({"date": date, **row} for row in rejected)
    return path


def build_product_summary(rows, date, products):
    """Aggregate accepted warehouse rows according to specs/product-summary.md."""
    catalogue = {product["name"]: product["category"] for product in products}
    groups = {}
    for row in rows:
        key = (row["branch"], row["product"])
        if key not in groups:
            groups[key] = {"items_sold": 0, "revenue_pence": 0}
        groups[key]["items_sold"] += row["quantity"]
        groups[key]["revenue_pence"] += row["line_total_pence"]
    return [
        {
            "date": date,
            "branch": branch,
            "product": product,
            "category": catalogue[product],
            "items_sold": groups[(branch, product)]["items_sold"],
            "revenue_gbp": format_pence(groups[(branch, product)]["revenue_pence"]).replace(
                "£", "", 1
            ),
        }
        for branch, product in sorted(groups)
    ]


def write_product_summary(summary, output_dir, date):
    path = os.path.join(output_dir, f"product_summary_{date}.csv")
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "date",
                "branch",
                "product",
                "category",
                "items_sold",
                "revenue_gbp",
            ],
        )
        writer.writeheader()
        writer.writerows(summary)
    return path
