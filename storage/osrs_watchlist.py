import json
import os

WATCHLIST_FILE = "osrs_watchlist.json"

def load_watchlist() -> list[int]:
    if not os.path.exists(WATCHLIST_FILE):
        return []

    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_watchlist(item_ids: list[int]) -> None:
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(item_ids, f, indent=2)

def add_item(item_id: int) -> None:
    watchlist = load_watchlist()
    if item_id not in watchlist:
        watchlist.append(item_id)
        save_watchlist(watchlist)

def remove_item(item_id: int) -> None:
    watchlist = load_watchlist()
    if item_id in watchlist:
        watchlist.remove(item_id)
        save_watchlist(watchlist)
