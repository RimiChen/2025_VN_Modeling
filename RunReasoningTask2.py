import json
import csv
from pathlib import Path
from networkx.readwrite import json_graph
from ReasoningQueries_updated_2 import get_dialogues_by_event  # Update if needed

# === Paths ===
KG_PATH = "Data/KGs_Book_0/integrated_kg.json"
GROUND_TRUTH_PATH = "Data/KGs_Book_0/ground_truth_task2_dialogues.csv"
OUTPUT_CSV_PATH = "Data/KGs_Book_0/reasoning_task2_dialogues.csv"

# === Load KG ===
with open(KG_PATH, "r", encoding="utf-8") as f:
    kg_data = json.load(f)
G = json_graph.node_link_graph(kg_data)

# === Load ground-truth event list ===
event_ids = []
with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        event_ids.append(row["Event"])

# === Run reasoning for each event
results = []
for event_id in event_ids:
    predicted = get_dialogues_by_event(G, event_id)
    results.append({
        "Event": event_id,
        "Predicted_Dialogues": " | ".join(sorted(predicted))
    })

# === Save results to CSV
Path(OUTPUT_CSV_PATH).parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Event", "Predicted_Dialogues"])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"✅ Reasoning predictions saved to: {OUTPUT_CSV_PATH}")
