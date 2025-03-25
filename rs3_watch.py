import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from fetchers.rs3_scraper import get_exchange_info
from fetchers.rs3_index import load_cached_index
from fetchers import rs3_search
from storage import rs3_watchlist as watchlist
import sys

VERSION = "1.1.0"

console = Console()

def clear_screen():
    input("\n[Press Enter to continue...]")
    os.system('cls' if os.name == 'nt' else 'clear')

def show_watchlist():
    items = watchlist.load_watchlist()

    if not items:
        console.print("[yellow]Your watchlist is empty.[/yellow]")
        return

    table = Table(title="RS3 Market Watchlist")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("GE Price", justify="right", style="green")
    table.add_column("High Alch", justify="right", style="magenta")
    table.add_column("Low Alch", justify="right", style="magenta")
    table.add_column("Store", justify="right")
    table.add_column("Buy Limit", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Alch Profit", justify="right", style="yellow")

    for item in items:
        try:
            item_data = get_exchange_info(item["name"])
        except Exception as e:
            console.print(f"[red]Failed to fetch Exchange:{item['name']}: {e}[/red]")
            continue

        ge_price = item_data.get("ge_price", 0)
        high_alch = item_data.get("high_alch", 0)
        low_alch = item_data.get("low_alch", 0)
        store_price = item_data.get("store_price", 0)
        buy_limit = item_data.get("buy_limit", 0)
        volume = item_data.get("volume", 0)
        alch_profit = high_alch - ge_price if ge_price else 0

        table.add_row(
            str(item_data["item_id"]),
            item_data["name"].title(),
            str(ge_price),
            str(high_alch),
            str(low_alch),
            str(store_price),
            str(buy_limit),
            f"{volume:,}" if volume else "-",
            f"{alch_profit:,} gp" if alch_profit >= 0 else f"[red]{alch_profit:,} gp[/red]",
        )

    console.print(table)

def manual_add():
    item_name = input("Enter item name to add: ").strip().lower().replace(" ", "_")
    try:
        item_data = get_exchange_info(item_name)
        watchlist.add_item(item_data["item_id"], item_data["name"])
        console.print(f"[green]Added {item_data['name']} (ID {item_data['item_id']}) to watchlist.[/green]")
    except Exception as e:
        console.print(f"[red]Item not found or failed to fetch: {e}[/red]")

def search_items():
    term = input("Enter search term: ").strip().lower()
    index = load_cached_index()

    seen = set()
    results = []

    for item in index:
        name = item["name"].lower()
        if term in name and name not in seen:
            seen.add(name)
            results.append(item)

    if not results:
        console.print("[yellow]No items found.[/yellow]")
        return

    results.sort(key=lambda x: x["name"])
    per_page = 20
    total_pages = (len(results) + per_page - 1) // per_page
    page = 0

    while True:
        start = page * per_page
        end = start + per_page
        page_results = results[start:end]

        table = Table(title=f"Search Results - Page {page + 1} of {total_pages}")
        table.add_column("Name", style="bold")
        table.add_column("Price", justify="right")
        table.add_column("URL", overflow="fold")

        for item in page_results:
            table.add_row(item["name"], str(item.get("price", "—")), item["url"])

        console.print(table)
        console.print("[dim][N]ext, [P]rev, [A]dd <name>, [Q]uit[/dim]")

        cmd = input(">> ").strip().lower()

        if cmd == "n" and page < total_pages - 1:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd.startswith("a "):
            arg = cmd[2:].strip()
            match = next((item for item in results if item["name"].lower() == arg.lower()), None)
            if match:
                try:
                    item_data = get_exchange_info(match["name"])
                    watchlist.add_item(item_data["item_id"], item_data["name"])
                    console.print(f"[green]Added {item_data['name']} (ID {item_data['item_id']}) to watchlist.[/green]")
                except Exception as e:
                    console.print(f"[red]Failed to fetch item: {e}[/red]")
            else:
                console.print("[red]Name not found in current page.[/red]")
        elif cmd == "q":
            break
        else:
            console.print("[red]Unknown command.[/red]")

def simulate_profit():
    items = watchlist.load_watchlist()

    if not items:
        console.print("[yellow]Your watchlist is empty.[/yellow]")
        return

    table = Table(title="Watchlist Items")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="bold")
    for item in items:
        table.add_row(str(item["id"]), item["name"])
    console.print(table)

    raw_input = input("Enter item ID or name to simulate: ").strip().lower()

    selected = None
    if raw_input.isdigit():
        item_id = int(raw_input)
        selected = next((item for item in items if item["id"] == item_id), None)
    else:
        selected = next((item for item in items if item["name"].lower() == raw_input), None)

    if not selected:
        console.print("[red]Item not found in watchlist.[/red]")
        return

    try:
        item_data = get_exchange_info(selected["name"])
    except Exception as e:
        console.print(f"[red]Item fetch failed: {e}[/red]")
        return

    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        console.print("[red]Invalid quantity.[/red]")
        return

    ge_price = item_data.get("ge_price", 0)
    high_alch = item_data.get("high_alch", 0)

    buy_total = ge_price * quantity
    sell_total = ge_price * quantity
    profit_range = sell_total - buy_total
    alch_profit = (high_alch - ge_price) * quantity

    panel = Panel.fit(
        f"[bold cyan]{item_data['name']}[/bold cyan] (ID {item_data['item_id']})\n\n"
        f"[green]Buy (GE):[/green] {ge_price} gp × {quantity} = {buy_total:,} gp\n"
        f"[yellow]Estimated Sell:[/yellow] {sell_total:,} gp\n"
        f"[yellow]Profit Range:[/yellow] {profit_range:,} gp\n\n"
        f"[magenta]High Alch:[/magenta] {high_alch} gp\n"
        f"[magenta]Alch Profit:[/magenta] {alch_profit:,} gp",
        title="Profit Simulation",
        border_style="blue"
    )

    console.print(panel)

def remove_item():
    items = watchlist.load_watchlist()

    if not items:
        console.print("[yellow]Your watchlist is empty.[/yellow]")
        return

    table = Table(title="Watchlist Items")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="bold")
    for item in items:
        table.add_row(str(item["id"]), item["name"])
    console.print(table)

    raw_input = input("Enter item ID or name to remove: ").strip().lower()

    selected = None
    if raw_input.isdigit():
        item_id = int(raw_input)
        selected = next((item for item in items if item["id"] == item_id), None)
    else:
        selected = next((item for item in items if item["name"].lower() == raw_input), None)

    if not selected:
        console.print("[red]Item not found in watchlist.[/red]")
        return

    watchlist.remove_item(selected["id"])
    console.print(f"[red]Removed {selected['name']} (ID {selected['id']}) from watchlist.[/red]")

def menu():
    while True:
        console.print("[bold cyan]RS3 Market Watcher[/bold cyan]")
        console.print("[1] Show watchlist")
        console.print("[2] Add item by name")
        console.print("[3] Remove item by ID or name")
        console.print("[4] Search items")
        console.print("[5] Simulate market profit")
        console.print("[6] Search wiki item by name")
        console.print("[7] Refresh search cache")
        console.print("[E] Exit")

        choice = input("Select option: ").strip().lower()

        if choice == "1":
            show_watchlist()
        elif choice == "2":
            manual_add()
        elif choice == "3":
            remove_item()
        elif choice == "4":
            search_items()
        elif choice == "5":
            simulate_profit()
        elif choice == "6":
            search_items()
        elif choice == "7":
            rs3_search.refresh_cache(force=True)
            console.print("[green]Search cache refreshed.[/green]")
        elif choice == "e":
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")

        clear_screen()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print(f"RS3 Market Watcher v{VERSION}")
        sys.exit(0)
    menu()

