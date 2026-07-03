"""Core data models used across the price comparison agent."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """A product to search for across vendors."""

    name: str
    sku: Optional[str] = None


@dataclass
class PriceQuote:
    """A single vendor's quote for a product."""

    vendor_name: str
    price: Optional[float]        # None if vendor failed to respond
    shipping: Optional[float] = 0.0
    in_stock: bool = True
    error: Optional[str] = None    # populated if the vendor call failed

    @property
    def total_cost(self) -> Optional[float]:
        if self.price is None or not self.in_stock or self.error:
            return None
        return round(self.price + (self.shipping or 0.0), 2)

    @property
    def is_valid(self) -> bool:
        return self.error is None and self.in_stock and self.price is not None
