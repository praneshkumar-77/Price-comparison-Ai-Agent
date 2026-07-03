# Price Comparison AI Agent

A lightweight Python agent that compares product prices across multiple
vendors, picks the best deal (factoring in shipping cost), and explains
its recommendation. Ships with a mock vendor layer so it runs fully
offline, plus a pytest suite that validates the comparison logic.

## Features

- `Vendor` clients with a common interface (`get_price`) — swap the mock
  implementations for real vendor APIs/scrapers without touching the
  agent logic.
- `PriceComparisonAgent` that:
  - Queries all configured vendors for a given product.
  - Normalizes price + shipping into a total cost.
  - Ranks vendors and returns the cheapest option.
  - Flags out-of-stock or failed vendors instead of crashing.
- Test suite covering: cheapest-vendor selection, shipping-cost
  tie-breaks, out-of-stock handling, vendor failure handling, and
  empty-catalog edge cases.

## Project Structure

```
price-comparison-agent/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── models.py      # Product / PriceQuote data classes
│   ├── vendors.py      # Vendor interface + mock vendor implementations
│   └── agent.py         # PriceComparisonAgent (core comparison logic)
├── tests/
│   └── test_price_comparison.py
└── .gitignore
```

## Getting Started

```bash
git clone <this-repo>
cd price-comparison-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the agent on a sample product
python -m src.agent

# Run the test suite
pytest -v
```

## Example Output

```
Comparing prices for 'Wireless Mouse' across 4 vendors...

Vendor       Price    Shipping   Total     Stock
-----------  -------  ---------  --------  --------
VendorC      $18.99   $0.00      $18.99    In Stock
VendorA      $19.99   $4.99      $24.98    In Stock
VendorB      $17.50   $8.00      $25.50    In Stock
VendorD      -        -          -         Out of Stock

Best deal: VendorC — $18.99 total (free shipping)
```

## Extending to Real Vendors

Implement the `Vendor` interface in `src/vendors.py`:

```python
class RealVendor(Vendor):
    def get_price(self, product_name: str) -> PriceQuote:
        # call a real API or scrape a vendor page here
        ...
```

Then register it in the agent's vendor list. No other code changes
needed — the agent, ranking, and tests all work against the `Vendor`
interface, not concrete implementations.

## License

MIT
