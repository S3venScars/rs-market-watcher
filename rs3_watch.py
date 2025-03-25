import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from fetchers.rs3_scraper import get_exchange_info
from fetchers.rs3_index import load_cached_index
from storage import rs3_watchlist as watchlist
from fetchers import rs3_search

console = Console()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_watchlist():
    items = watchlist.load_watchlist()

    if not items:
        console.print("[yellow]Your watchlist is empty.[/yellow]")
        input("\nPress Enter to continue...")
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
            console.print(f"[red]Failed to fetch {item['name']}: {e}[/red]")
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
    input("\nPress Enter to continue...")


def manual_add():
    item_name = input("Enter item name to add: ").strip()
    try:
        item_data = rs3_search.search_item(item_name)
        watchlist.add_item(item_data["id"], item_data["name"])
        console.print(f"[green]Added {item_data['name']} (ID {item_data['id']}) to watchlist.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to add item: {e}[/red]")
    input("\nPress Enter to continue...")


def search_items():
    term = input("Enter search term: ").strip().lower()
    index = load_cached_index()
    results = [item for item in index if term in item["name"].lower()]

    if not results:
        console.print("[yellow]No items found.[/yellow]")
        input("\nPress Enter to continue...")
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
            table.add_row(item["name"], str(item["price"] or "—"), item["url"])

        console.print(table)
        console.print("[dim][N]ext, [P]rev, [A]dd <name>, [Q]uit[/dim]")

        cmd = input(">> ").strip().lower()

        if cmd == "n" and page < total_pages - 1:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd.startswith("a "):
            arg = cmd[2:].strip()
            try:
                item_data = rs3_search.search_item(arg)
                watchlist.add_item(item_data["id"], item_data["name"])
                console.print(f"[green]Added {item_data['name']} (ID {item_data['id']}) to watchlist.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to fetch or add item: {e}[/red]")
        elif cmd == "q":
            break
        else:
            console.print("[red]Unknown command.[/red]")


def simulate_profit():
    item_id_input = input("Enter item ID to simulate: ").strip()
    if not item_id_input.isdigit():
        console.print("[red]Invalid ID.[/red]")
        return

    try:
        item_id = int(item_id_input)
        name = next(item["name"] for item in watchlist.load_watchlist() if item["id"] == item_id)
        item_data = get_exchange_info(name)
    except StopIteration:
        console.print("[red]Item ID not found in watchlist.[/red]")
        return
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
        f"[bold cyan]{item_data['name']}[/bold cyan] (ID {item_id})\n\n"
        f"[green]Buy (GE):[/green] {ge_price} gp × {quantity} = {buy_total:,} gp\n"
        f"[yellow]Estimated Sell:[/yellow] {sell_total:,} gp\n"
        f"[yellow]Profit Range:[/yellow] {profit_range:,} gp\n\n"
        f"[magenta]High Alch:[/magenta] {high_alch} gp\n"
        f"[magenta]Alch Profit:[/magenta] {alch_profit:,} gp",
        title="Profit Simulation",
        border_style="blue"
    )

    console.print(panel)
    input("\nPress Enter to continue...")


def wiki_item_search():
    item_name = input("Enter item name to search: ").strip()
    try:
        data = rs3_search.search_item(item_name)
        table = Table(title=f"Search Result: {data['name']}")
        table.add_column("Field", style="bold")
        table.add_column("Value", justify="right")
        table.add_row("Name", data["name"])
        table.add_row("ID", str(data["id"]))
        table.add_row("GE Price", f"{data['ge_price']:,} gp")
        table.add_row("High Alch", f"{data['high_alch']:,} gp")
        table.add_row("Exchange Page", data["url"])
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    input("\nPress Enter to continue...")


def refresh_search_cache():
    rs3_search.clear_search_cache()
    console.print("[green]Search cache cleared! Reloading watchlist...[/green]")

    for item in watchlist.load_watchlist():
        try:
            rs3_search.search_item(item["name"])
        except Exception as e:
            console.print(f"[red]Failed to refresh {item['name']}: {e}[/red]")

    console.print("[bold green]Watchlist data refreshed and re-cached![/bold green]")
    input("\nPress Enter to continue...")


def menu():
    while True:
        clear_screen()
        console.print("[bold cyan]RS3 Market Watcher[/bold cyan]\n")
        console.print("[1] Show watchlist")
        console.print("[2] Add item by name")
        console.print("[3] Remove item by ID")
        console.print("[4] Search items")
        console.print("[5] Simulate market profit")
        console.print("[6] Search wiki item by name")
        console.print("[7] Refresh search cache")
        console.print("[8] Export cache to Excel")
        console.print("[E] Exit")

        choice = input("\nSelect option: ").strip().lower()

        if choice == "1":
            show_watchlist()
        elif choice == "2":
            manual_add()
        elif choice == "3":
            try:
                item_id = int(input("Enter item ID to remove: "))
                watchlist.remove_item(item_id)
                console.print(f"[red]Removed {item_id} from watchlist.[/red]")
            except ValueError:
                console.print("[red]Invalid ID.[/red]")
                input("\nPress Enter to continue...")
        elif choice == "4":
            search_items()
        elif choice == "5":
            simulate_profit()
        elif choice == "6":
            wiki_item_search()
        elif choice == "7":
            refresh_search_cache()
        elif choice == "8":
            rs3_search.export_cache_to_excel()
            console.print("[green]Cache exported to watch_cache.xlsx[/green]")
            input("\nPress Enter to continue...")
        elif choice == "e":
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    menu()
