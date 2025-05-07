import os
import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
import csv

# === Paths ===
EXCEL_PATH = "Data/Annotation_Book_1/Story_1_with_IDs.xlsx"
PANEL_JSON_DIR = "Data/Annotation_Book_1/"
OUTPUT_CSV_PATH = "Data/KGs_Book_1/ground_truth_task1_actions.csv"
BOOK_ID = 1

# === Step 1: Load macro_event → panel mapping from Excel ===
df = pd.read_excel(EXCEL_PATH)
df = df.dropna(subset=["Index", "Plot_0"])

macro_to_panels = defaultdict(list)
panel_to_macro = {}

for _, row in df.iterrows():
    panel_id = str(row["Index"]).strip()
    macro_event = str(row["Plot_0"]).strip()
    macro_to_panels[macro_event].append(panel_id)
    panel_to_macro[panel_id] = macro_event

# === Step 2: Read panel JSONs to extract action verbs ===
panel_to_actions = defaultdict(list)
json_files = sorted(Path(PANEL_JSON_DIR).glob(BOOK_ID + "_*.json"))

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    page_id = json_file.stem
    for i, panel in enumerate(data.get("panels", [])):
        panel_id = f"{page_id}_{i}"
        action_strs = panel.get("actions", [])
        for a in action_strs:
            if isinstance(a, str):
                parts = a.strip().split()
                if len(parts) == 3:
                    verb = parts[1]
                elif len(parts) == 1:
                    verb = parts[0]
                else:
                    continue
                if verb:
                    panel_to_actions[panel_id].append(verb)

# === Step 3: Group action verbs by macro-event ===
macro_to_actions = defaultdict(set)
for panel_id, verbs in panel_to_actions.items():
    macro = panel_to_macro.get(panel_id)
    if macro:
        for verb in verbs:
            macro_to_actions[macro].add(verb)

# === Step 4: Write to CSV ===
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Macro_event", "Actions"])
    for macro, actions in sorted(macro_to_actions.items()):
        writer.writerow([macro, "; ".join(sorted(actions))])

print(f"✅ Ground truth saved to: {OUTPUT_CSV_PATH}")
