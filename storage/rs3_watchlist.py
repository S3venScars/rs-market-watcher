import json
import os

WATCHLIST_FILE = "rs3_watchlist.json"

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_watchlist(data: list[dict]):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_item(item_id: int, name: str):
    watchlist = load_watchlist()
    if not any(entry["id"] == item_id for entry in watchlist):
        watchlist.append({"id": item_id, "name": name})
        save_watchlist(watchlist)

def remove_item(item_id: int):
    watchlist = load_watchlist()
    watchlist = [item for item in watchlist if item["id"] != item_id]
    save_watchlist(watchlist)
