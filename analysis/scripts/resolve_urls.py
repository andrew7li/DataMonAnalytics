from pathlib import Path
from urllib.parse import urljoin
import time
import random

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "pricecharting_url_lookup.csv"
)

PRICECHARTING_SET_URLS = {
    "Mega Evolution":
        "https://www.pricecharting.com/console/pokemon-mega-evolution?sort=model-number&model-number=&model-number=&exclude-hardware=false&exclude-variants=false&show-images=true&in-collection=",

    "Phantasmal Flames":
        "https://www.pricecharting.com/console/pokemon-phantasmal-flames",

    "Ascended Heroes":
        "https://www.pricecharting.com/console/pokemon-ascended-heroes",
    
    "Scarlet & Violet Base":
        "https://www.pricecharting.com/console/pokemon-scarlet-&-violet",

    "Paldea Evolved":
        "https://www.pricecharting.com/console/pokemon-paldea-evolved",

    "Obsidian Flames":
        "https://www.pricecharting.com/console/pokemon-obsidian-flames",

    "Paradox Rift":
        "https://www.pricecharting.com/console/pokemon-paradox-rift",
    
    "Temporal Forces":
        "https://www.pricecharting.com/console/pokemon-temporal-forces",
    
    "Twilight Masquerade":
        "https://www.pricecharting.com/console/pokemon-twilight-masquerade",
    
    "Stellar Crown":
        "https://www.pricecharting.com/console/pokemon-stellar-crown",

    "Surging Sparks":
        "https://www.pricecharting.com/console/pokemon-surging-sparks",
    
    "Journey Together":
        "https://www.pricecharting.com/console/pokemon-journey-together",

    "Destined Rivals":
        "https://www.pricecharting.com/console/pokemon-destined-rivals", 
    
    "Black Bolt":
        "https://www.pricecharting.com/console/pokemon-black-bolt",

    "Prismatic Evolutions":
        "https://www.pricecharting.com/console/pokemon-prismatic-evolutions",
    
    "Scarlet & Violet 151":
        "https://www.pricecharting.com/console/pokemon-scarlet-&-violet-151",

    "Shrouded Fable":
        "https://www.pricecharting.com/console/pokemon-shrouded-fable", 

    "White Flare":
        "https://www.pricecharting.com/console/pokemon-white-flare", 
        
    # Add more sets here later:
    #
    # "Phantasmal Flames":
    #     "https://www.pricecharting.com/console/pokemon-phantasmal-flames?...",
}


# =========================================================
# HELPERS
# =========================================================

def random_sleep(a=1.0, b=2.5):
    time.sleep(random.uniform(a, b))


def clean_text(text):

    if text is None:
        return ""

    return " ".join(str(text).split())


def scroll_to_bottom(page):
    """
    Scroll until no additional content loads.
    """

    last_height = 0

    while True:

        page.mouse.wheel(0, 5000)

        time.sleep(1.5)

        new_height = page.evaluate(
            "document.body.scrollHeight"
        )

        if new_height == last_height:
            break

        last_height = new_height

    print("Finished scrolling.")


def parse_card_title(title):
    """
    Parse:
        Bulbasaur #1
        Bulbasaur [Reverse Holo] #1
        Mega Venusaur ex #3
    """

    title = clean_text(title)

    is_reverse_holo = "[Reverse Holo]" in title
    is_holo = (
        "[Holo]" in title
        and not is_reverse_holo
    )

    cleaned = (
        title
        .replace("[Reverse Holo]", "")
        .replace("[Holo]", "")
        .strip()
    )

    if "#" in cleaned:

        name_part, number_part = cleaned.rsplit("#", 1)

        card_name = name_part.strip()
        card_number = number_part.strip()

    else:

        card_name = cleaned
        card_number = ""

    if is_reverse_holo:
        variant = "Reverse Holo"

    elif is_holo:
        variant = "Holo"

    else:
        variant = "Normal"

    return (
        card_name,
        card_number,
        variant
    )


# =========================================================
# SCRAPER
# =========================================================

def scrape_set_page(page, set_name, url):

    print(f"\nScraping set: {set_name}")

    page.goto(url)

    page.wait_for_load_state(
        "networkidle"
    )

    random_sleep(2, 4)

    # IMPORTANT:
    # Scroll so all lazy-loaded cards appear
    scroll_to_bottom(page)

    random_sleep(1, 2)

    soup = BeautifulSoup(
        page.content(),
        "html.parser"
    )

    rows = []

    links = soup.select('a[href^="/game/"]')

    print(f"Found {len(links)} raw links")

    for link in links:

        title = clean_text(
            link.get_text()
        )

        if not title:
            continue

        # Skip non-card links
        if "#" not in title:
            continue

        href = link.get("href")

        if not href:
            continue

        full_url = urljoin(
            "https://www.pricecharting.com",
            href
        )

        (
            card_name,
            card_number,
            variant
        ) = parse_card_title(title)

        rows.append({
            "setName": set_name,
            "pricechartingTitle": title,
            "pricechartingCardName": card_name,
            "pricechartingCardNumber": card_number,
            "pricechartingVariant": variant,
            "pricechartingUrl": full_url,
        })

    print(f"Parsed {len(rows)} cards")

    return rows


# =========================================================
# MAIN
# =========================================================

def main():

    all_rows = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        for (
            set_name,
            url
        ) in PRICECHARTING_SET_URLS.items():

            rows = scrape_set_page(
                page,
                set_name,
                url
            )

            all_rows.extend(rows)

            random_sleep(2, 4)

        browser.close()

    lookup_df = pd.DataFrame(all_rows)

    lookup_df = lookup_df.drop_duplicates(
        subset=[
            "setName",
            "pricechartingTitle",
            "pricechartingUrl"
        ]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    lookup_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n===================================")
    print(f"Saved: {OUTPUT_PATH}")
    print(f"Rows: {len(lookup_df)}")
    print("===================================")


if __name__ == "__main__":
    main()