import os
import sqlite3


def load_sales(rows, output_dir, date):
    db = sqlite3.connect(os.path.join(output_dir, "warehouse.db"))
    db.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            transaction_id TEXT,
            branch TEXT,
            sold_at TEXT,
            till_id TEXT,
            product TEXT,
            quantity INTEGER,
            unit_price_pence INTEGER,
            line_total_pence INTEGER
        )
    """)
    # make re-runs idempotent
    db.execute("DELETE FROM sales WHERE substr(sold_at, 1, 10) = ?", (date,))
    for r in rows:
        db.execute(
            "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                r["transaction_id"],
                r["branch"],
                r["sold_at"],
                r["till_id"],
                r["product"],
                r["quantity"],
                r["unit_price_pence"],
                r["line_total_pence"],
            ),
        )
    db.commit()
    db.close()
