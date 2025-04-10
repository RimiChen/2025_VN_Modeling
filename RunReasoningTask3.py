import json
import csv
import pandas as pd
from pathlib import Path
from networkx.readwrite import json_graph
from ReasoningQueries_updated_2 import get_character_appearances  # Update if needed

# === Paths ===
KG_PATH = "Data/KGs_Book_0/integrated_kg.json"
ANNOTATION_XLSX = "Data/Annotation_Book_0/Story_0_with_IDs.xlsx"
OUTPUT_CSV_PATH = "Data/KGs_Book_0/reasoning_task3_characters.csv"

# === Load KG ===
with open(KG_PATH, "r", encoding="utf-8") as f:
    kg_data = json.load(f)
G = json_graph.node_link_graph(kg_data)

# === Load panel → event mapping from Excel ===
df = pd.read_excel(ANNOTATION_XLSX)
df = df.dropna(subset=["Index", "Plot_1_ID"])

panel_to_event = {}
for _, row in df.iterrows():
    panel_id = str(row["Index"]).strip()
    event_id = str(row["Plot_1_ID"]).strip()
    panel_to_event[panel_id] = event_id

# === Run character appearance reasoning
char_to_panels = get_character_appearances(G)

# === Aggregate character appearances by event
event_to_characters = {}
for char, panels in char_to_panels.items():
    for panel in panels:
        event_id = panel_to_event.get(panel)
        if event_id:
            event_to_characters.setdefault(event_id, set()).add(char)

# === Write to CSV
Path(OUTPUT_CSV_PATH).parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSV_PATH, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Event", "Predicted_Characters"])
    for event, chars in sorted(event_to_characters.items()):
        writer.writerow([event, " | ".join(sorted(chars))])

print(f"✅ Reasoning predictions saved to: {OUTPUT_CSV_PATH}")
