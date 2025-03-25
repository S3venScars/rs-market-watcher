from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from fetchers.osrs_api import fetch_latest, fetch_mapping
from models.item import ItemPrice
from storage import osrs_watchlist

console = Console()
mapping = fetch_mapping()


def show_watchlist():
    ids = watchlist.load_watchlist()

    if not ids:
        console.print("[yellow]Your watchlist is empty.[/yellow]")
        return

    table = Table(title="RS3 Market Watchlist")
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("High", justify="right", style="green")
    table.add_column("High Time", justify="center")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Low Time", justify="center")

    for item_id in ids:
        price_data = fetch_latest(item_id)
        entry = mapping.get(item_id)

        if not entry or not price_data:
            continue

        item = ItemPrice(
            item_id=item_id,
            name=entry["name"],
            high=price_data["high"],
            low=price_data["low"],
            high_time=price_data["highTime"],
            low_time=price_data["lowTime"],
        )

        table.add_row(*item.to_row())

    console.print(table)


def manual_add():
    item_name = input("Enter item name to add: ").lower()

    for item_id, entry in mapping.items():
        if item_name == entry["name"].lower():
            watchlist.add_item(item_id)
            console.print(f"[green]Added {entry['name']} (ID {item_id}) to watchlist.[/green]")
            return

    console.print("[red]Item not found.[/red]")


def search_items():
    term = input("Enter search term: ").lower()
    results = []

    for item_id, entry in mapping.items():
        if term in entry["name"].lower():
            results.append((item_id, entry["name"]))

    if not results:
        console.print("[yellow]No items found.[/yellow]")
        return

    results.sort(key=lambda x: x[1])  # Sort by name
    per_page = 20
    total_pages = (len(results) + per_page - 1) // per_page
    page = 0

    while True:
        start = page * per_page
        end = start + per_page
        page_results = results[start:end]

        table = Table(title=f"Search Results - Page {page + 1} of {total_pages}")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="bold")

        for item_id, name in page_results:
            table.add_row(str(item_id), name)

        console.print(table)
        console.print("[dim][N]ext, [P]rev, [A]dd <id|name>, [Q]uit[/dim]")

        cmd = input(">> ").strip().lower()

        if cmd == "n" and page < total_pages - 1:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd.startswith("a "):
            arg = cmd[2:].strip()
            if arg.isdigit():
                item_id = int(arg)
                if item_id in mapping:
                    watchlist.add_item(item_id)
                    console.print(f"[green]Added {mapping[item_id]['name']}[/green]")
                else:
                    console.print("[red]Invalid ID.[/red]")
            else:
                matches = [id for id, entry in mapping.items() if entry["name"].lower() == arg.lower()]
                if matches:
                    item_id = matches[0]
                    watchlist.add_item(item_id)
                    console.print(f"[green]Added {mapping[item_id]['name']}[/green]")
                else:
                    console.print("[red]Name not found.[/red]")
        elif cmd == "q":
            break
        else:
            console.print("[red]Unknown command.[/red]")


def simulate_profit():
    item_id_input = input("Enter item ID to simulate: ").strip()

    if not item_id_input.isdigit():
        console.print("[red]Invalid ID.[/red]")
        return

    item_id = int(item_id_input)
    mapping = fetch_mapping()
    item_entry = mapping.get(item_id)

    if not item_entry:
        console.print("[red]Item not found in mapping.[/red]")
        return

    data = fetch_latest(item_id)
    if not data:
        console.print("[red]Price data unavailable.[/red]")
        return

    try:
        quantity = int(input("Enter quantity: "))
    except ValueError:
        console.print("[red]Invalid quantity.[/red]")
        return

    high_price = data["high"]
    low_price = data["low"]

    buy_total = low_price * quantity
    sell_total = high_price * quantity
    profit_range = sell_total - buy_total

    high_alch = item_entry.get("highalch", 0)
    alch_profit = (high_alch - low_price) * quantity

    panel = Panel.fit(
        f"[bold cyan]{item_entry['name']}[/bold cyan] (ID {item_id})\n\n"
        f"[green]Buy (Low):[/green] {low_price} gp × {quantity} = {buy_total:,} gp\n"
        f"[green]Sell (High):[/green] {high_price} gp × {quantity} = {sell_total:,} gp\n"
        f"[yellow]Profit Range:[/yellow] {profit_range:,} gp\n\n"
        f"[magenta]High Alch:[/magenta] {high_alch} gp\n"
        f"[magenta]Alch Profit:[/magenta] {alch_profit:,} gp",
        title="Profit Simulation",
        border_style="blue"
    )

    console.print(panel)


def menu():
    while True:
        console.print("[1] Show watchlist")
        console.print("[2] Add item by name")
        console.print("[3] Remove item by ID")
        console.print("[4] Search items")
        console.print("[5] Simulate market profit")
        console.print("[E] Exit")

        choice = input("Select option: ").strip().lower()

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
        elif choice == "4":
            search_items()
        elif choice == "5":
            simulate_profit()
        elif choice == "e":
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


if __name__ == "__main__":
    menu()
