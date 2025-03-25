from fetchers.rs3_scraper import get_exchange_info
from rich import print
from rich.panel import Panel

item_name = input("Enter RS3 item name: ").strip()

try:
    data = get_exchange_info(item_name)
    panel_text = "\n".join([f"[bold]{k.replace('_', ' ').title()}:[/bold] {v}" for k, v in data.items()])
    print(Panel(panel_text, title=f"[green]{data['name']}[/green]"))
except Exception as e:
    print(f"[red]Error:[/red] {e}")
