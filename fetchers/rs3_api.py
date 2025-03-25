import requests
from typing import Optional

BASE_URL = "https://prices.runescape.wiki/api/v1/rs3"
HEADERS = {
    "User-Agent": "RS3-Market-Watcher/1.0 (by S3venScars)"
}

def fetch_latest(item_id: int) -> Optional[dict]:
    url = f"{BASE_URL}/latest?id={item_id}"
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        return res.json()["data"].get(str(item_id), None)
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
        return None

def fetch_mapping() -> dict:
    """Returns a dictionary of item_id -> item_name"""
    url = f"{BASE_URL}/mapping"
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        return {entry["id"]: entry for entry in data}
    except Exception as e:
        print(f"Error fetching item mapping: {e}")
        return {}
