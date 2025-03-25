import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BASE_URL = "https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch"
CACHE_FILE = "data/rs3_index.json"
META_FILE = "data/rs3_skill_index.json"
CACHE_EXPIRY_HOURS = 4
HEADERS = {"User-Agent": "RS3-Market-Watcher/1.0 (by S3venScars)"}


def fetch_market_index() -> list[dict]:
    with open(META_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    indexes = config.get("indexes", [])
    items = {}

    for page in indexes:
        print(f"[blue]Fetching index from:[/blue] {page}")
        url = f"{BASE_URL}/{page}"
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, "lxml")

            table = soup.find("table", class_=lambda c: c and "wikitable" in c)
            if not table:
                print(f"[yellow]Warning: No valid item table found on {page}[/yellow]")
                continue

            rows = table.find_all("tr")[1:]

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 10:
                    continue

                name_link = cols[1].find("a")
                url_link = cols[9].find("a")
                if not name_link or not url_link:
                    continue

                name = name_link.text.strip()
                price = cols[2].text.strip().replace(",", "").replace("?", "")
                try:
                    price = int(price)
                except ValueError:
                    price = None

                item_url = "https://runescape.wiki" + url_link["href"]

                key = name.lower()
                if key not in items:
                    items[key] = {
                        "name": name,
                        "price": price,
                        "url": item_url
                    }

        except Exception as e:
            print(f"[red]Error fetching {page}: {e}[/red]")

    final_list = list(items.values())

    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)

    # Update timestamp
    config["updated_at"] = datetime.utcnow().isoformat()
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return final_list


def load_cached_index(force_refresh=False) -> list[dict]:
    if force_refresh or not os.path.exists(CACHE_FILE):
        print("[cyan]Refreshing index: no cache found or forced refresh...[/cyan]")
        return fetch_market_index()

    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    try:
        last_updated = datetime.fromisoformat(meta["updated_at"])
    except Exception:
        print("[yellow]Warning: invalid or missing timestamp, forcing refresh...[/yellow]")
        return fetch_market_index()

    if datetime.utcnow() - last_updated > timedelta(hours=CACHE_EXPIRY_HOURS):
        print("[cyan]Refreshing index: data is older than 4 hours...[/cyan]")
        return fetch_market_index()

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
