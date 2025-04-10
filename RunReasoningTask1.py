import json
import csv
from pathlib import Path
from networkx.readwrite import json_graph
from ReasoningQueries_updated_2 import get_actions_by_macro_event  # make sure this matches your script name

# === Paths ===
KG_PATH = "Data/KGs_Book_0/integrated_kg.json"
GROUND_TRUTH_PATH = "Data/KGs_Book_0/ground_truth_task1_actions.csv"
OUTPUT_CSV_PATH = "Data/KGs_Book_0/reasoning_task1_actions.csv"

# === Load KG ===
with open(KG_PATH, "r", encoding="utf-8") as f:
    kg_data = json.load(f)
G = json_graph.node_link_graph(kg_data)

# === Load ground-truth macro-event list ===
macro_events = []
with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        macro_events.append(row["Macro_event"])

# === Run reasoning for each macro-event
results = []
for macro in macro_events:
    predicted = get_actions_by_macro_event(G, macro)
    results.append({
        "Macro_event": macro,
        "Predicted_Actions": " | ".join(sorted(predicted))
    })

# === Save results to CSV
Path(OUTPUT_CSV_PATH).parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Macro_event", "Predicted_Actions"])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"✅ Reasoning predictions saved to: {OUTPUT_CSV_PATH}")
