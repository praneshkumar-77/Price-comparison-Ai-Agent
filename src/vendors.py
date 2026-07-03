"""Vendor interface plus mock vendor implementations.

Replace the mock vendors with real API clients or scrapers by
implementing the same `Vendor` interface — the agent doesn't care
where the price data comes from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.models import PriceQuote


class Vendor(ABC):
    """Common interface every vendor client must implement."""

    name: str

    @abstractmethod
    def get_price(self, product_name: str) -> PriceQuote:
        """Return a PriceQuote for the given product name."""
        raise NotImplementedError


class MockVendor(Vendor):
    """A vendor backed by an in-memory price catalog, for testing/demo.

    catalog: {product_name: {"price": float, "shipping": float, "in_stock": bool}}
    """

    def __init__(self, name: str, catalog: Dict[str, dict], simulate_failure: bool = False):
        self.name = name
        self.catalog = catalog
        self.simulate_failure = simulate_failure

    def get_price(self, product_name: str) -> PriceQuote:
        if self.simulate_failure:
            return PriceQuote(
                vendor_name=self.name,
                price=None,
                error="Vendor API timeout",
            )

        entry = self.catalog.get(product_name)
        if entry is None:
            return PriceQuote(
                vendor_name=self.name,
                price=None,
                in_stock=False,
                error="Product not found in catalog",
            )

        return PriceQuote(
            vendor_name=self.name,
            price=entry["price"],
            shipping=entry.get("shipping", 0.0),
            in_stock=entry.get("in_stock", True),
        )


def build_sample_vendors() -> list:
    """A handful of mock vendors used by the demo run and the tests."""
    vendor_a = MockVendor(
        "VendorA",
        catalog={
            "Wireless Mouse": {"price": 19.99, "shipping": 4.99, "in_stock": True},
            "USB-C Hub": {"price": 29.99, "shipping": 0.0, "in_stock": True},
        },
    )
    vendor_b = MockVendor(
        "VendorB",
        catalog={
            "Wireless Mouse": {"price": 17.50, "shipping": 8.00, "in_stock": True},
            "USB-C Hub": {"price": 31.00, "shipping": 0.0, "in_stock": False},
        },
    )
    vendor_c = MockVendor(
        "VendorC",
        catalog={
            "Wireless Mouse": {"price": 18.99, "shipping": 0.0, "in_stock": True},
            "USB-C Hub": {"price": 27.50, "shipping": 3.50, "in_stock": True},
        },
    )
    vendor_d = MockVendor(
        "VendorD",
        catalog={
            "Wireless Mouse": {"price": 15.00, "shipping": 0.0, "in_stock": False},
        },
    )
    return [vendor_a, vendor_b, vendor_c, vendor_d]
