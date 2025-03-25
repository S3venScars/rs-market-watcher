import os
import json
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

CACHE_FILE = "data/rs3_index.json"
CACHE_EXPIRY = 4 * 3600  # 4 hours

INDEX_SKILLS = [
    "Archaeology", "Construction", "Construction_flatpacks", "Cooking", "Crafting",
    "Divination", "Farming", "Firemaking", "Fishing", "Fletching", "Herblore", "Hunter",
    "Invention", "Magic", "Melee_armour", "Melee_weapons", "Mining", "Necromancy",
    "Prayer", "Ranged", "Runecrafting", "Slayer", "Smithing", "Summoning", "Woodcutting"
]

BASE_URL = "https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/"
HEADERS = {
    "User-Agent": "S3venScars-RS3-Market-Watcher/1.0 (https://github.com/S3venScars)"
}


def fetch_market_index():
    all_items = []

    for skill in INDEX_SKILLS:
        url = BASE_URL + skill
        console.print(f"Fetching index from: {skill}", style="blue")

        try:
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200:
                console.print(f"[red]Failed to fetch {skill}: HTTP {resp.status_code}[/red]")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            tables = soup.select("table.wikitable.sortable")
            console.print(f"Found {len(tables)} table(s) on {skill}", style="cyan")

            if not tables:
                console.print(f"[yellow]Warning: No valid item table found on {skill}[/yellow]")
                continue

            for table in tables:
                rows = table.find_all("tr")[1:]  # Skip header

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 2:
                        continue

                    link_tag = cols[1].find("a")
                    if not link_tag:
                        continue

                    name = link_tag.get("title", "").strip()
                    url = "https://runescape.wiki" + link_tag.get("href", "").strip()

                    price = cols[2].text.strip().replace(",", "") if len(cols) >= 3 else None
                    price = int(price) if price and price.isdigit() else None

                    all_items.append({
                        "name": name,
                        "url": url,
                        "price": price
                    })

        except Exception as e:
            console.print(f"[red]Error processing {skill}: {e}[/red]")

    return all_items


def save_index(items):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "items": items
        }, f, indent=2)


def load_cached_index(force_refresh=False):
    if not os.path.exists(CACHE_FILE) or force_refresh:
        console.print("[cyan]Refreshing index: no cache found or forced refresh...[/cyan]")
        items = fetch_market_index()
        save_index(items)
        return items

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    timestamp = data.get("timestamp", 0)
    age = time.time() - timestamp

    if age > CACHE_EXPIRY:
        console.print("[cyan]Refreshing index: data is older than 4 hours...[/cyan]")
        items = fetch_market_index()
        save_index(items)
        return items

    return data.get("items", [])
