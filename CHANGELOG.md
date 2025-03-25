# Changelog

## [v1.1.0] – 2025-03-26
### ✨ Added
- **Multi-table index parsing**: Each skill page now scrapes all valid `wikitable sortable` tables instead of just one. This ensures coverage for items like *grimy herbs*, potions, tools, and more.
- **Item deduplication** in search results using a `seen` set to prevent repeat entries (e.g. "Grimy marrentill" showing 3x).
- Support for **removing items by name or ID** in the watchlist.
- Support for **simulating profit by name or ID** with automatic watchlist table preview.

### 🛠 Changed
- Refactored all terminal logging to use `rich.console.Console.print()` with proper color support (blue, yellow, red, cyan).
- Improved terminal output with table counts per skill shown during index refresh.
- Replaced `soup.find_all("table", class_="...")` with `soup.select("table.wikitable.sortable")` for broader compatibility.

### 🧼 Fixed
- Index not refreshing older cache correctly when over 4 hours old.
- CLI search returning `No items found` for valid cases (e.g. "grimy").

---

## [v1.0.0] – Initial release
- RS3 Market Watch core with basic watchlist, GE price lookups, and simulated profit calculations.
