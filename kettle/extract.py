import csv
import json
import os
from decimal import Decimal

from kettle.branches import BRANCHES


def read_till_export(data_dir, branch, date, products=None):
    config = BRANCHES[branch]
    path = os.path.join(data_dir, "raw", "tills", f"{branch}_{date}.{config['format']}")
    try:
        stream = open(path, encoding="utf-8")
    except FileNotFoundError:
        if config["optional"]:
            return []
        raise
    with stream:
        if config["format"] == "csv":
            return list(csv.reader(stream))[1:]
        catalogue = {product["id"]: product["name"] for product in products or []}
        rows = []
        for line in stream:
            if not line.strip():
                continue
            transaction = json.loads(line)
            for item in transaction["items"]:
                rows.append([
                    transaction["transaction_id"], transaction["timestamp"], transaction["till"],
                    catalogue.get(item["sku"], ""), str(item["qty"]), str(item["price_pence"]),
                ])
        return rows


def read_products(data_dir):
    path = os.path.join(data_dir, "reference", "products.json")
    with open(path) as f:
        return json.load(f)


def read_eur_rate(data_dir, date):
    path = os.path.join(data_dir, "raw", "exchange_rates", date + ".json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f, parse_float=Decimal)
    if data.get("base") != "GBP" or data.get("date") != date:
        raise ValueError("Exchange rate must use GBP as base and match the processing date")
    return data["rates"]["EUR"]
