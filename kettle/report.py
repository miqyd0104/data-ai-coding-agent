import csv
import os


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
    for b in summary:
        s = summary[b]
        result.append({
            "date": s["date"],
            "branch": s["branch"],
            "transactions": len(s["txns"]),
            "items_sold": s["items_sold"],
            "revenue_gbp": "%.2f" % (s["revenue"] / 100),
        })
    return result


def write_summary(summary, output_dir, date):
    path = os.path.join(output_dir, "daily_summary_" + date + ".csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "branch", "transactions", "items_sold", "revenue_gbp"])
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
