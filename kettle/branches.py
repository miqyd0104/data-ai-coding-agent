"""Till configuration; shared parsing lives in extract and transform."""

BRANCHES = {
    "leeds": {"format": "csv", "price_unit": "pounds", "optional": False},
    "manchester": {"format": "csv", "price_unit": "pence", "optional": False},
    "york": {"format": "csv", "price_unit": "pounds", "optional": False},
    "dublin": {"format": "csv", "price_unit": "pounds", "optional": False},
    "edinburgh": {"format": "jsonl", "price_unit": "pence", "optional": True},
}
