"""Till configuration; shared parsing lives in extract and transform."""

BRANCHES = {
    "leeds": {"format": "csv", "price_unit": "pounds", "currency": "GBP", "optional": False},
    "manchester": {"format": "csv", "price_unit": "pence", "currency": "GBP", "optional": False},
    "york": {"format": "csv", "price_unit": "pounds", "currency": "GBP", "optional": False},
    "dublin": {
        "format": "csv",
        "price_unit": "pounds",
        "currency": "EUR",
        "optional": False,
        "columns": (5, 0, 4, 1, 3, 2),
    },
    "edinburgh": {"format": "jsonl", "price_unit": "pence", "currency": "GBP", "optional": True},
    "glasgow": {"format": "csv", "price_unit": "pounds", "currency": "GBP", "optional": True},
}
