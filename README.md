📈 RuneScape Market Watch Suite
A terminal-based, extendable price tracking suite for RuneScape 3 (RS3) and Old School RuneScape (OSRS).

Monitor item prices, simulate profits, calculate alching margins, and export your tracked data to Excel — all with a clean, minimal interface optimized for fast trading decisions.

⚙️ Features
🧠 RS3 Watcher
✅ Add any tradable item to your watchlist

🔍 Live lookup from the RuneScape Wiki

📉 View GE price, high/low alch value, buy limits, and volume

💰 Simulate alching or flipping profits by quantity

📁 Export data to .xlsx

♻️ Auto-refresh cache every 4 hours or manually on-demand

🔎 Search with fuzzy matching (rune → Air Rune, Death Rune, etc.)

🧠 Smart name parsing (Elder Rune Pickaxe +5 → valid wiki lookup)

🧠 OSRS Watcher (Coming Soon)
🔍 Lookup OSRS item prices via the OSRS GE API

🧾 Daily price and volume tracking

📁 Extendable to support flipping, high alch margins, or historical analysis

🚀 Installation
bash
Copy
Edit
git clone https://github.com/S3venScars/runescape-market-watcher.git
cd runescape-market-watcher
python -m venv .venv
source .venv/bin/activate   # or `.venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
▶️ Usage
RS3 Watcher
bash
Copy
Edit
python rs3_watch.py
You'll see a menu:

pgsql
Copy
Edit
[1] Show watchlist
[2] Add item by name
[3] Remove item by ID
[4] Search items
[5] Simulate market profit
[6] Search wiki item by name
[7] Refresh search cache
[8] Export cache to Excel
[E] Exit
Example: Simulate Profit
yaml
Copy
Edit
Enter item ID: 824
Enter quantity: 5000

Buy (GE): 360 gp × 5000 = 1,800,000 gp
High Alch: 720 gp
Alch Profit: 1,800,000 gp
📤 Exporting to Excel
Use Option [8] to generate a file: watch_cache.xlsx
Includes all cached price data (name, ID, price, alch value, profit, URL, last updated).

📦 Folder Structure
bash
Copy
Edit
.
├── fetchers/
│   ├── rs3_search.py
│   ├── rs3_scraper.py
│   └── rs3_index.py
├── storage/
│   └── rs3_watchlist.py
├── rs3_watch.py
├── osrs_watch.py            # Coming soon
├── watch_cache.xlsx         # Output file
├── data/
│   └── rs3_search_cache.json
└── requirements.txt
📚 Requirements
Python 3.9+

BeautifulSoup4

requests

openpyxl

rich

Install with:

bash
Copy
Edit
pip install -r requirements.txt
📜 License
This project is licensed under the MIT License.

✨ Credits
Built with ❤️ by S3venScars
Wiki data courtesy of the RuneScape Wiki
