import os
import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
import csv

# === Paths ===
EXCEL_PATH = "Data/Annotation_Book_1/Story_1_with_IDs.xlsx"
PANEL_JSON_DIR = "Data/Annotation_Book_1/"
OUTPUT_CSV_PATH = "Data/KGs_Book_1/ground_truth_task2_dialogues.csv"

# === Step 1: Load panel → event mapping from Excel ===
df = pd.read_excel(EXCEL_PATH)
df = df.dropna(subset=["Index", "Plot_1_ID"])

event_to_panels = defaultdict(list)
panel_to_event = {}

for _, row in df.iterrows():
    panel_id = str(row["Index"]).strip()
    event_id = str(row["Plot_1_ID"]).strip()
    event_to_panels[event_id].append(panel_id)
    panel_to_event[panel_id] = event_id

# === Step 2: Extract dialogues from panel JSONs ===
panel_to_dialogues = defaultdict(list)
json_files = sorted(Path(PANEL_JSON_DIR).glob("0_*.json"))

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    page_id = json_file.stem
    for i, panel in enumerate(data.get("panels", [])):
        panel_id = f"{page_id}_{i}"
        dialogues = panel.get("textual", {}).get("dialogues", [])
        for line in dialogues:
            if isinstance(line, str) and line.strip():
                panel_to_dialogues[panel_id].append(line.strip())

# === Step 3: Group dialogues by event ID ===
event_to_dialogues = defaultdict(set)
for panel_id, lines in panel_to_dialogues.items():
    event_id = panel_to_event.get(panel_id)
    if event_id:
        for line in lines:
            event_to_dialogues[event_id].add(line)

# === Step 4: Save to CSV ===
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Event", "Dialogues"])
    for event, lines in sorted(event_to_dialogues.items()):
        writer.writerow([event, " | ".join(sorted(lines))])

print(f"✅ Ground truth saved to: {OUTPUT_CSV_PATH}")
