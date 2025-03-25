from rich.console import Console
from rich.table import Table
from fetchers.rs3_api import fetch_latest, fetch_mapping
from models.item import ItemPrice

console = Console()
item_id = 560  # Death rune

mapping = fetch_mapping()
entry = mapping.get(item_id)

if entry:
    price_data = fetch_latest(item_id)

    if price_data:
        item = ItemPrice(
            item_id=item_id,
            name=entry["name"],
            high=price_data["high"],
            low=price_data["low"],
            high_time=price_data["highTime"],
            low_time=price_data["lowTime"],
        )

        table = Table(title="RS3 Market Watch - Single Item")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("High", justify="right", style="green")
        table.add_column("High Time", justify="center")
        table.add_column("Low", justify="right", style="red")
        table.add_column("Low Time", justify="center")

        table.add_row(*item.to_row())
        console.print(table)
    else:
        console.print("[red]Could not retrieve item price data.[/red]")
else:
    console.print(f"[red]Item ID {item_id} not found in mapping.[/red]")
