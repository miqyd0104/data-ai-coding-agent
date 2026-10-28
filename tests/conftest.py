import pytest


@pytest.fixture
def products():
    """Tiny hand-written catalogue for unit tests."""
    return [
        {"id": "FW01", "name": "Flat White", "category": "Coffee",
         "aliases": ["flat wht"]},
        {"id": "LT01", "name": "Latte", "category": "Coffee", "aliases": ["caffe latte"]},
        {"id": "CR01", "name": "Croissant", "category": "Bakery", "aliases": []},
    ]
