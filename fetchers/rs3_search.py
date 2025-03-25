import json
import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from .rs3_index import load_cached_index

CACHE_FILE = "data/rs3_search_cache.json"
CACHE_EXPIRY = 4 * 3600  # 4 hours

def _format_item_name(name):
    return urllib.parse.quote(name.replace(" ", "_").replace("+", "%2B"))

def _fetch_wiki_item(name):
    formatted_name = _format_item_name(name)
    url = f"https://runescape.wiki/w/Exchange:{formatted_name}"
    resp = requests.get(url, headers={"User-Agent": "S3venScars/RS3-Market-Watcher"})
    if resp.status_code != 200:
        raise ValueError(f"Could not fetch exchange page for '{formatted_name}'")
    soup = BeautifulSoup(resp.text, "html.parser")
    info = {}

    try:
        info["name"] = name
        info["url"] = url
        info["item_id"] = int(soup.select_one('a[title="Module:GEPrices/data"]')['href'].split("=")[-1])
        table = soup.find("table", class_="infobox")
        for row in table.find_all("tr"):
            header = row.find("th")
            data = row.find("td")
            if not header or not data:
                continue
            key = header.text.strip().lower()
            val = data.text.strip().replace(",", "").replace(" coins", "")
            if "alch" in key:
                info["high_alch" if "high" in key else "low_alch"] = int(val) if val.isdigit() else 0
            elif "store price" in key:
                info["store_price"] = int(val) if val.isdigit() else 0
            elif "buy limit" in key:
                info["buy_limit"] = int(val) if val.isdigit() else 0
            elif "volume" in key:
                info["volume"] = int(val.replace(",", "")) if val.replace(",", "").isdigit() else 0
            elif "ge price" in key:
                info["ge_price"] = int(val) if val.isdigit() else 0
    except Exception as e:
        raise ValueError(f"Error parsing exchange info: {e}")

    return info

def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            if time.time() - data.get("timestamp", 0) < CACHE_EXPIRY:
                return data.get("items", [])
    return []

def _save_cache(items):
    with open(CACHE_FILE, "w") as f:
        json.dump({"timestamp": time.time(), "items": items}, f, indent=2)

def refresh_cache(force=False):
    items = load_cached_index(force_refresh=force)
    _save_cache(items)
    return items

def search_items(term):
    term = term.lower()
    items = _load_cache()
    return [item for item in items if term in item["name"].lower()]
