import json
import csv
from pathlib import Path
from networkx.readwrite import json_graph
from ReasoningQueries_updated_2 import get_actions_by_macro_event  # make sure this matches your script name

# === Paths ===
GROUND_TRUTH_PATH = "Data/KGs_Book_1/ground_truth_task1_actions.csv"

# KG_PATH = "Data/KGs_Book_1/integrated_kg.json"
# OUTPUT_CSV_PATH = "Data/KGs_Book_1/reasoning_task1_actions.csv"

KG_PATH = "Data/KGs_Book_1/integrated_kg_normalized.json"
OUTPUT_CSV_PATH = "Data/KGs_Book_1/reasoning_task1_actions_normalized.csv"

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
