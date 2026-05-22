import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "data" / "external" / "scrydex" / "pricing-data-graded" / "fixture.json"

# TODO: This eventually would be the result of the API: https://scrydex.com/docs/getting-started/prices#graded,
# but is mocked for now.
data = None

# Load file
with open(DATA_PATH, "r") as f:
    data = json.load(f)

prices = data.get("prices", [])

if not prices:
    print("No pricing data found.")
else:
    # Average market price
    avg_market = sum(p["market"] for p in prices) / len(prices)

    # Highest market value item
    highest = max(prices, key=lambda x: x["market"])

    print(f"Average market price: {avg_market:.2f}")
    print("Highest market item:")
    print(highest)
