import matplotlib.pyplot as plt

# Data for Crypto, Forex, and Stock markets (BDT time)
markets = {
    "Crypto Market": [("Open", "24/7"), ("Close", "No Close")],
    "Forex Market": [("Open", "Monday 3 AM"), ("Close", "Saturday 3 AM")],
    "Stock Market (Examples)": [
        ("NYSE / NASDAQ Open", "8:30 PM"),
        ("NYSE / NASDAQ Close", "3 AM"),
        ("London Stock Exchange Open", "1 PM"),
        ("London Stock Exchange Close", "9:30 PM")
    ]
}

# Create figure
fig, ax = plt.subplots(figsize=(9, 6))
ax.axis("off")

# Title
ax.text(0.5, 1.05, "📊 Crypto, Forex & Stock Market Times (BDT)",
        ha="center", va="center", fontsize=14, weight="bold")

# Prepare table data
table_data = [["Market", "Event", "Time"]]
for market, events in markets.items():
    for i, (event, time) in enumerate(events):
        if i == 0:
            table_data.append([market, event, time])
        else:
            table_data.append(["", event, time])

# Create table
table = ax.table(cellText=table_data, colLabels=None, loc="center", cellLoc="center")

# Style table
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.2)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight="bold", color="white")
        cell.set_facecolor("#4B72FA")
    else:
        cell.set_facecolor("#F5F5F5" if row % 2 == 0 else "#FFFFFF")

plt.tight_layout()
plt.show()
plt.savefig("1.png")