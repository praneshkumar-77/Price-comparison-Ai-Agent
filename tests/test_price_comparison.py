"""Test suite for the Price Comparison AI Agent.

Covers: cheapest-vendor selection, price+shipping total-cost ranking,
out-of-stock handling, vendor failure handling, and empty-result
edge cases.
"""

import pytest

from src.agent import PriceComparisonAgent
from src.models import PriceQuote
from src.vendors import MockVendor, build_sample_vendors


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def sample_agent():
    return PriceComparisonAgent(build_sample_vendors())


# ---------------------------------------------------------------------
# Core comparison behavior
# ---------------------------------------------------------------------

def test_collects_a_quote_from_every_vendor(sample_agent):
    quotes = sample_agent.collect_quotes("Wireless Mouse")
    vendor_names = {q.vendor_name for q in quotes}
    assert vendor_names == {"VendorA", "VendorB", "VendorC", "VendorD"}


def test_picks_lowest_total_cost_not_lowest_sticker_price(sample_agent):
    """VendorB has the lowest sticker price ($17.50) but VendorC wins
    overall once shipping is included ($18.99 + $0.00 = $18.99)."""
    best = sample_agent.best_deal("Wireless Mouse")
    assert best.vendor_name == "VendorC"
    assert best.total_cost == 18.99


def test_ranking_orders_vendors_cheapest_total_first(sample_agent):
    report = sample_agent.compare("Wireless Mouse")
    totals = [q.total_cost for q in report["ranked"]]
    assert totals == sorted(totals)
    assert report["ranked"][0].vendor_name == "VendorC"


def test_out_of_stock_vendor_is_excluded_from_ranking(sample_agent):
    """VendorD has the cheapest raw price ($15.00) but is out of stock,
    so it must never be recommended as the best deal."""
    report = sample_agent.compare("Wireless Mouse")
    ranked_names = [q.vendor_name for q in report["ranked"]]
    assert "VendorD" not in ranked_names
    assert report["best_deal"].vendor_name != "VendorD"


def test_second_product_ranking_and_out_of_stock_handling(sample_agent):
    """VendorB has USB-C Hub out of stock, so it's excluded. Among the
    remaining vendors, VendorA wins on total cost ($29.99 + free
    shipping) even though VendorC has the lower sticker price ($27.50),
    because VendorC's $3.50 shipping pushes its total to $31.00."""
    report = sample_agent.compare("USB-C Hub")
    ranked_names = [q.vendor_name for q in report["ranked"]]
    assert "VendorB" not in ranked_names
    assert report["best_deal"].vendor_name == "VendorA"
    assert report["best_deal"].total_cost == pytest.approx(29.99)


# ---------------------------------------------------------------------
# Failure / edge-case handling
# ---------------------------------------------------------------------

def test_failed_vendor_does_not_crash_comparison():
    healthy = MockVendor(
        "HealthyVendor",
        catalog={"Widget": {"price": 10.0, "shipping": 1.0, "in_stock": True}},
    )
    broken = MockVendor("BrokenVendor", catalog={}, simulate_failure=True)

    agent = PriceComparisonAgent([healthy, broken])
    report = agent.compare("Widget")

    assert report["best_deal"].vendor_name == "HealthyVendor"
    broken_quote = next(q for q in report["quotes"] if q.vendor_name == "BrokenVendor")
    assert broken_quote.error is not None
    assert broken_quote.total_cost is None


def test_all_vendors_out_of_stock_returns_no_best_deal():
    v1 = MockVendor("V1", catalog={"Widget": {"price": 5.0, "in_stock": False}})
    v2 = MockVendor("V2", catalog={"Widget": {"price": 6.0, "in_stock": False}})

    agent = PriceComparisonAgent([v1, v2])
    report = agent.compare("Widget")

    assert report["best_deal"] is None
    assert report["ranked"] == []


def test_product_not_in_any_catalog_returns_no_best_deal():
    v1 = MockVendor("V1", catalog={"Widget": {"price": 5.0}})
    agent = PriceComparisonAgent([v1])

    report = agent.compare("Nonexistent Product")

    assert report["best_deal"] is None
    quote = report["quotes"][0]
    assert quote.error == "Product not found in catalog"


def test_no_vendors_configured_returns_no_best_deal():
    agent = PriceComparisonAgent([])
    report = agent.compare("Widget")

    assert report["quotes"] == []
    assert report["best_deal"] is None


# ---------------------------------------------------------------------
# PriceQuote model behavior
# ---------------------------------------------------------------------

def test_price_quote_total_cost_sums_price_and_shipping():
    quote = PriceQuote(vendor_name="X", price=10.0, shipping=2.5, in_stock=True)
    assert quote.total_cost == 12.5


def test_price_quote_total_cost_is_none_when_out_of_stock():
    quote = PriceQuote(vendor_name="X", price=10.0, shipping=2.5, in_stock=False)
    assert quote.total_cost is None


def test_price_quote_total_cost_is_none_on_error():
    quote = PriceQuote(vendor_name="X", price=None, error="timeout")
    assert quote.total_cost is None
    assert quote.is_valid is False
