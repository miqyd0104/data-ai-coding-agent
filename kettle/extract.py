import csv
import json
import os
from decimal import Decimal

from kettle.branches import BRANCHES


def read_till_export(data_dir, branch, date, products=None, rejected=None):
    config = BRANCHES[branch]
    path = os.path.join(data_dir, "raw", "tills", f"{branch}_{date}.{config['format']}")
    try:
        with open(path, encoding="utf-8") as stream:
            if config["format"] == "csv":
                return list(csv.reader(stream))[1:]
            return _read_jsonl(stream, products, branch, rejected)
    except FileNotFoundError:
        if config["optional"]:
            return []
        raise


def _read_jsonl(stream, products, branch, rejected):
    catalogue = {product["id"]: product["name"] for product in products or []}
    rows = []
    for row_number, line in enumerate(stream, 1):
        if not line.strip():
            continue
        try:
            transaction = json.loads(line)
            if not isinstance(transaction, dict):
                raise TypeError
            if not all(
                isinstance(transaction.get(field), str) and transaction[field].strip()
                for field in ["transaction_id", "timestamp", "till"]
            ):
                raise ValueError
            if not isinstance(transaction.get("items"), list) or not transaction["items"]:
                raise ValueError
        except (ValueError, TypeError):
            if rejected is not None:
                rejected.append(
                    {
                        "branch": branch,
                        "row_number": row_number,
                        "reason": "Invalid JSONL transaction",
                    }
                )
            continue
        for item in transaction["items"]:
            if not isinstance(item, dict) or not {"sku", "qty", "price_pence"} <= item.keys():
                if rejected is not None:
                    rejected.append(
                        {"branch": branch, "row_number": row_number, "reason": "Invalid JSONL item"}
                    )
                continue
            sku = item["sku"]
            name = catalogue.get(sku, "") if isinstance(sku, str) else ""
            rows.append(
                [
                    transaction["transaction_id"],
                    transaction["timestamp"],
                    transaction["till"],
                    name,
                    str(item["qty"]),
                    str(item["price_pence"]),
                ]
            )
    return rows


def read_products(data_dir):
    path = os.path.join(data_dir, "reference", "products.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_eur_rate(data_dir, date):
    path = os.path.join(data_dir, "raw", "exchange_rates", date + ".json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f, parse_float=Decimal)
    if data.get("base") != "GBP" or data.get("date") != date:
        raise ValueError("Exchange rate must use GBP as base and match the processing date")
    return data["rates"]["EUR"]
