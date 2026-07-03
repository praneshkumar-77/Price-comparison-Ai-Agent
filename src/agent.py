"""Price Comparison AI Agent.

Queries a set of vendors for a product, ranks the results by total
cost (price + shipping), and recommends the best deal — skipping
vendors that are out of stock or that failed to respond.
"""

from typing import List, Optional

from src.models import PriceQuote
from src.vendors import Vendor, build_sample_vendors


class PriceComparisonAgent:
    def __init__(self, vendors: List[Vendor]):
        self.vendors = vendors

    def collect_quotes(self, product_name: str) -> List[PriceQuote]:
        """Query every vendor for the product. Never raises: a vendor
        exception is caught and turned into an error quote so one bad
        vendor can't take down the whole comparison."""
        quotes = []
        for vendor in self.vendors:
            try:
                quotes.append(vendor.get_price(product_name))
            except Exception as exc:  # defensive: vendor client misbehaved
                quotes.append(
                    PriceQuote(vendor_name=vendor.name, price=None, error=str(exc))
                )
        return quotes

    def rank_quotes(self, quotes: List[PriceQuote]) -> List[PriceQuote]:
        """Return only valid (in-stock, priced) quotes sorted cheapest first."""
        valid = [q for q in quotes if q.is_valid]
        return sorted(valid, key=lambda q: q.total_cost)

    def best_deal(self, product_name: str) -> Optional[PriceQuote]:
        quotes = self.collect_quotes(product_name)
        ranked = self.rank_quotes(quotes)
        return ranked[0] if ranked else None

    def compare(self, product_name: str) -> dict:
        """Full comparison report: all quotes + the recommended vendor."""
        quotes = self.collect_quotes(product_name)
        ranked = self.rank_quotes(quotes)
        return {
            "product": product_name,
            "quotes": quotes,
            "ranked": ranked,
            "best_deal": ranked[0] if ranked else None,
        }


def _print_report(report: dict) -> None:
    print(f"\nComparing prices for '{report['product']}' across "
          f"{len(report['quotes'])} vendors...\n")

    header = f"{'Vendor':<12} {'Price':<8} {'Shipping':<10} {'Total':<9} {'Stock'}"
    print(header)
    print("-" * len(header))

    for q in sorted(report["quotes"], key=lambda q: (q.total_cost is None, q.total_cost)):
        if q.error:
            print(f"{q.vendor_name:<12} {'-':<8} {'-':<10} {'-':<9} Error: {q.error}")
        elif not q.in_stock:
            print(f"{q.vendor_name:<12} {'-':<8} {'-':<10} {'-':<9} Out of Stock")
        else:
            print(f"{q.vendor_name:<12} ${q.price:<7.2f} ${q.shipping:<9.2f} "
                  f"${q.total_cost:<8.2f} In Stock")

    best = report["best_deal"]
    if best:
        shipping_note = "free shipping" if best.shipping == 0 else f"${best.shipping:.2f} shipping"
        print(f"\nBest deal: {best.vendor_name} — ${best.total_cost:.2f} total ({shipping_note})")
    else:
        print("\nNo vendor currently has this product in stock.")


if __name__ == "__main__":
    agent = PriceComparisonAgent(build_sample_vendors())
    report = agent.compare("Wireless Mouse")
    _print_report(report)
