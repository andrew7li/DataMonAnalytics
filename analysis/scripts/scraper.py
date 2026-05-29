from pathlib import Path
import time
import random

import pandas as pd
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parents[2]

LINKS_PATH = BASE_DIR / "data" / "processed" / "pricecharting_url_lookup.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "sv_pricecharting_sales.csv"

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


def random_sleep(a=1.0, b=2.5):
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


def scrape_grade(page, metadata, grade_name, option_value):
    page.select_option(
        "#completed-auctions-condition",
        value=option_value
    )

    random_sleep(1.0, 2.0)

    selector = f"div.{option_value} tbody tr"
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
        page.goto(url, wait_until="networkidle", timeout=60000)
    except Exception as e:
        print(f"Failed to load page: {e}")
        return []

    random_sleep(1.5, 3.0)

    available_grades = get_available_grade_options(page)

    if not available_grades:
        print("No target graded sales available.")
        return []

    all_sales = []

    for grade_name, option_value in available_grades.items():
        print(f"  {grade_name}")

        try:
            sales = scrape_grade(
                page,
                metadata,
                grade_name,
                option_value
            )

            print(f"    found {len(sales)} sales")
            all_sales.extend(sales)

        except Exception as e:
            print(f"    failed {grade_name}: {e}")

        random_sleep(0.5, 1.5)

    return all_sales


def save_checkpoint(rows):
    if not rows:
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)


def main():
    links = pd.read_csv(LINKS_PATH)

    links = links.dropna(subset=["pricechartingUrl"]).drop_duplicates(
        subset=["pricechartingUrl"]
    )

    print(f"Loaded {len(links)} unique PriceCharting URLs")

    all_sales = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for i, (_, row) in enumerate(links.iterrows(), start=1):
            print(f"\n[{i}/{len(links)}]")

            sales = scrape_card(page, row)
            all_sales.extend(sales)

            if i % 10 == 0:
                save_checkpoint(all_sales)
                print(f"Checkpoint saved: {len(all_sales)} sales")

            random_sleep(2.0, 4.0)

        browser.close()

    save_checkpoint(all_sales)

    print(f"\nSaved final sales CSV:")
    print(OUTPUT_PATH)
    print(f"Total sales rows: {len(all_sales)}")


if __name__ == "__main__":
    main()