
import os
import pandas as pd
from collections import defaultdict
import csv

# === Paths ===
EXCEL_PATH = "Data/Annotation_Book_1/Story_1_with_IDs.xlsx"
OUTPUT_CSV_PATH = "Data/KGs_Book_1/ground_truth_task4_panels.csv"

# === Step 1: Load Excel annotations ===
df = pd.read_excel(EXCEL_PATH)
df = df.dropna(subset=["Index", "Plot_0"])

# === Step 2: Group panels by macro-event (Plot_0)
macro_to_panels = defaultdict(list)
for _, row in df.iterrows():
    panel_id = str(row["Index"]).strip()
    macro_id = str(row["Plot_0"]).strip()
    macro_to_panels[macro_id].append(panel_id)

# === Step 3: Sort panels within each macro-event (reading order)
for macro_id in macro_to_panels:
    macro_to_panels[macro_id] = sorted(macro_to_panels[macro_id])

# === Step 4: Write to CSV ===
os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Macro_event", "Panels"])
    for macro, panels in sorted(macro_to_panels.items()):
        writer.writerow([macro, " | ".join(panels)])

print(f"✅ Ground truth saved to: {OUTPUT_CSV_PATH}")
