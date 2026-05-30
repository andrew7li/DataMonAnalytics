from pathlib import Path
import time
import random

import pandas as pd
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

LINKS_PATH = BASE_DIR / "data" / "processed" / "ex_pricecharting_url_lookup.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "ex_pricecharting_sales.csv"

HEADLESS = True
CHECKPOINT_EVERY = 25

# Set to a number like 10 for testing, or None for full run
TEST_LIMIT = None

# Optional debugging filter.
# Example: "Nidoking"
DEBUG_CARD_FILTER = None

GRADES = {
    "PSA 10": "completed-auctions-manual-only",
    "Grade 9": "completed-auctions-graded",
    "Grade 8": "completed-auctions-new",
    "Grade 7": "completed-auctions-cib",
    "Grade 6": "completed-auctions-grade-six",
    "Grade 5": "completed-auctions-grade-five",
    "Grade 4": "completed-auctions-grade-four",
    "Grade 3": "completed-auctions-grade-three",
    "Grade 2": "completed-auctions-box-and-manual",
    "Grade 1": "completed-auctions-loose-and-manual",
}


# ============================================================
# HELPERS
# ============================================================

def random_sleep(a=0.5, b=1.25):
    time.sleep(random.uniform(a, b))


def clean_price(price_text):
    if pd.isna(price_text) or price_text is None:
        return None

    cleaned = (
        str(price_text)
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


def get_available_grade_options(page):
    """
    Reads the completed-sales dropdown and returns only:
    - PSA 10
    - Grade 9 through Grade 1
    - only grades where the dropdown count is not 0

    Example option:
        <option value="completed-auctions-manual-only">PSA 10 (30)</option>
    """

    options = page.query_selector_all("#completed-auctions-condition option")

    available = {}

    for option in options:
        text = option.inner_text().strip()
        value = option.get_attribute("value")

        for grade_name, expected_value in GRADES.items():
            if value != expected_value:
                continue

            if "(0)" in text:
                continue

            available[grade_name] = value

    return available


def scrape_grade_live(page, metadata, grade_name, option_value):
    """
    Reliable grade scraper.

    This actually selects the grade in the dropdown, waits for the
    corresponding sales table, and then scrapes the visible/live DOM.

    This is slower than scraping hidden divs directly, but fixes pages
    where EX-era grade tables do not fully populate until the grade
    is selected.
    """

    page.select_option(
        "#completed-auctions-condition",
        value=option_value
    )

    selector = f"div.{option_value} table.hoverable-rows tbody tr"

    try:
        page.wait_for_selector(selector, timeout=8000)
    except Exception:
        print(f"    {grade_name}: dropdown showed sales, but rows did not load")
        return []

    rows = page.query_selector_all(selector)

    sales = []

    for row in rows:
        date_el = row.query_selector("td.date")
        title_link = row.query_selector("td.title a")
        price_el = row.query_selector("span.js-price")

        sale_date = date_el.inner_text().strip() if date_el else None
        title = title_link.inner_text().strip() if title_link else None
        ebay_url = title_link.get_attribute("href") if title_link else None
        price_text = price_el.inner_text().strip() if price_el else None
        price = clean_price(price_text)

        if sale_date is None and title is None and price is None:
            continue

        sales.append({
            **metadata,
            "grade": grade_name,
            "saleDate": sale_date,
            "saleTitle": title,
            "salePrice": price,
            "salePriceText": price_text,
            "ebayUrl": ebay_url,
        })

    return sales


def scrape_card(page, row):
    url = row["pricechartingUrl"]

    metadata = {
        "setName": row.get("setName"),
        "pricechartingTitle": row.get("pricechartingTitle"),
        "pricechartingCardName": row.get("pricechartingCardName"),
        "pricechartingCardNumber": row.get("pricechartingCardNumber"),
        "pricechartingVariant": row.get("pricechartingVariant"),
        "pricechartingUrl": url,
    }

    print(f"\nScraping: {metadata['pricechartingTitle']}")
    print(url)

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        print(f"Failed to load page: {e}")
        return []

    # Give the dropdown/table JS a moment to initialize.
    page.wait_for_timeout(1000)

    available_grades = get_available_grade_options(page)

    if not available_grades:
        print("No target graded sales available.")
        return []

    all_sales = []

    for grade_name, option_value in available_grades.items():
        print(f"  {grade_name}")

        try:
            sales = scrape_grade_live(
                page=page,
                metadata=metadata,
                grade_name=grade_name,
                option_value=option_value,
            )

            print(f"    found {len(sales)} sales")
            all_sales.extend(sales)

        except Exception as e:
            print(f"    failed {grade_name}: {e}")

        page.wait_for_timeout(300)

    return all_sales


def save_checkpoint(rows):
    if not rows:
        return

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)


def load_existing_sales():
    """
    Resume support.

    If OUTPUT_PATH already exists, load it and skip URLs that already
    have sales rows saved.
    """

    if not OUTPUT_PATH.exists():
        return [], set()

    existing = pd.read_csv(OUTPUT_PATH)

    existing_rows = existing.to_dict("records")

    already_scraped = set()

    if "pricechartingUrl" in existing.columns:
        already_scraped = set(existing["pricechartingUrl"].dropna().unique())

    return existing_rows, already_scraped


def prepare_links():
    links = pd.read_csv(LINKS_PATH)

    links = links.dropna(subset=["pricechartingUrl"]).drop_duplicates(
        subset=["pricechartingUrl"]
    )

    if DEBUG_CARD_FILTER:
        links = links[
            links["pricechartingTitle"]
            .fillna("")
            .str.contains(DEBUG_CARD_FILTER, case=False, na=False)
        ]

    if TEST_LIMIT is not None:
        links = links.head(TEST_LIMIT)

    return links


# ============================================================
# MAIN
# ============================================================

def main():
    links = prepare_links()

    all_sales, already_scraped = load_existing_sales()

    if already_scraped:
        print(f"Already scraped URLs: {len(already_scraped)}")

    links = links[~links["pricechartingUrl"].isin(already_scraped)]

    print(f"Remaining URLs to scrape: {len(links)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)

        context = browser.new_context()

        # Keep this for speed, but do not block scripts/XHR/document.
        context.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["image", "stylesheet", "font", "media"]
            else route.continue_()
        )

        page = context.new_page()

        for i, (_, row) in enumerate(links.iterrows(), start=1):
            print(f"\n[{i}/{len(links)}]")

            sales = scrape_card(page, row)
            all_sales.extend(sales)

            if i % CHECKPOINT_EVERY == 0:
                save_checkpoint(all_sales)
                print(f"Checkpoint saved: {len(all_sales)} sales")

            random_sleep(0.75, 1.75)

        browser.close()

    save_checkpoint(all_sales)

    print(f"\nSaved final sales CSV:")
    print(OUTPUT_PATH)
    print(f"Total sales rows: {len(all_sales)}")


if __name__ == "__main__":
    main()