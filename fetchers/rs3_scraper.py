import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "RS3-Market-Watcher/1.0 (by YourName)"
}

BASE_URL = "https://runescape.wiki/w/Exchange:"


def get_exchange_info(item_name: str) -> dict:
    url = BASE_URL + item_name.replace(" ", "_")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise ValueError(f"Could not fetch exchange page for '{item_name}'")

    soup = BeautifulSoup(response.text, "lxml")

    def get_by_id(element_id):
        tag = soup.find(id=element_id)
        if tag:
            return tag.get_text(strip=True).replace(",", "")
        return None

    def to_int(val):
        return int(val) if val and val.isdigit() else None

    return {
        "name": item_name,
        "ge_price": to_int(get_by_id("GEPrice")),
        "high_alch": to_int(get_by_id("exchange-highalch")),
        "low_alch": to_int(get_by_id("exchange-lowalch")),
        "store_price": to_int(get_by_id("exchange-value")),
        "buy_limit": to_int(get_by_id("exchange-limit")),
        "volume": to_int(get_by_id("GEVolume")),
        "item_id": to_int(get_by_id("exchange-itemid")),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
    }
