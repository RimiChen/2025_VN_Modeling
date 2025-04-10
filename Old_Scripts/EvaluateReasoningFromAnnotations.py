import json
import pandas as pd
import numpy as np
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

# === Config ===
KG_PATH = "Data/KGs_Book_0/integrated_kg.json"
ANNOTATION_PATH = "Data/Annotation_Book_0/Story_0_with_IDs.xlsx"
OUTPUT_SUMMARY = "Data/KGs_Book_0/eval_summary_table.csv"
OUTPUT_DETAILS = "Data/KGs_Book_0/eval_detailed_queries.csv"
PRINT_RESULTS = True  # Set to False to silence screen output

# === Load data ===
with open(KG_PATH, "r", encoding="utf-8") as f:
    G = json_graph.node_link_graph(json.load(f))

df = pd.read_excel(ANNOTATION_PATH)
df_clean = df.dropna(subset=["Index", "Plot_0", "Plot_1_ID"])

# Ground truth: panel order (macro) and dialogue (event)
macro_events_gt = df_clean.groupby("Plot_0")["Index"].apply(list).to_dict()
events_gt = df_clean.groupby("Plot_1_ID")["Detailed Caption"].apply(list).to_dict()
events_gt = {k: [x for x in v if isinstance(x, str) and x.strip()] for k, v in events_gt.items()}

# === Reasoning logic ===
def get_ordered_panels_by_macro(G, macro):
    panels = []
    for ev in G.predecessors(macro):
        if G.nodes[ev].get("type") != "event": continue
        for seg in G.predecessors(ev):
            if G.nodes[seg].get("type") != "event_segment": continue
            for p in G.predecessors(seg):
                if G.nodes[p].get("type") == "panel":
                    panels.append(p)
    return panels

def evaluate_ordering_accuracy(predicted, gold):
    match = sum(p == g for p, g in zip(predicted, gold))
    return match / len(gold) if gold else 0.0

def get_dialogues_by_event(G, event_id):
    lines = set()
    for seg in G.predecessors(event_id):
        if G.nodes[seg].get("type") != "event_segment": continue
        for panel in G.predecessors(seg):
            if G.nodes[panel].get("type") != "panel": continue
            for d in G.successors(panel):
                if G.nodes[d].get("type") == "dialogue":
                    for t in G.successors(d):
                        if G.nodes[t].get("type") == "text":
                            lines.add(G.nodes[t]["label"])
    return list(lines)

# === Evaluate ===
ordering_scores, dialogue_scores = [], []
details = []

# Panel ordering (macro-level)
for macro, gold_order in macro_events_gt.items():
    pred_order = get_ordered_panels_by_macro(G, macro)
    score = evaluate_ordering_accuracy(pred_order[:len(gold_order)], gold_order)
    ordering_scores.append(score)
    details.append({
        "Query Type": "Panel Ordering",
        "Target": macro,
        "Score": round(score, 3),
        "Gold": gold_order,
        "Predicted": pred_order[:len(gold_order)]
    })
    if PRINT_RESULTS:
        print(f"[Panel Ordering] {macro}: {score:.2f}")

# Dialogue recall (event-level)
for event_id, gold_dialogues in events_gt.items():
    if not gold_dialogues:
        continue
    pred_dialogues = get_dialogues_by_event(G, event_id)
    correct = [line for line in pred_dialogues if line in gold_dialogues]
    recall = len(correct) / len(gold_dialogues) if gold_dialogues else 0.0
    dialogue_scores.append(recall)
    details.append({
        "Query Type": "Dialogue Recall",
        "Target": event_id,
        "Score": round(recall, 3),
        "Gold": gold_dialogues,
        "Predicted": pred_dialogues
    })
    if PRINT_RESULTS:
        print(f"[Dialogue Recall] {event_id}: {recall:.2f}")

# === Summary ===
summary_data = [
    {
        "Task": "Panel Ordering",
        "Mean Score": f"{np.mean(ordering_scores)*100:.1f}%",
        "Std Dev": f"{np.std(ordering_scores)*100:.1f}%"
    },
    {
        "Task": "Dialogue Recall",
        "Mean Score": f"{np.mean(dialogue_scores)*100:.1f}%",
        "Std Dev": f"{np.std(dialogue_scores)*100:.1f}%"
    }
]
summary_df = pd.DataFrame(summary_data)
details_df = pd.DataFrame(details)

# Save outputs
Path("./output").mkdir(parents=True, exist_ok=True)
summary_df.to_csv(OUTPUT_SUMMARY, index=False)
details_df.to_csv(OUTPUT_DETAILS, index=False)

if PRINT_RESULTS:
    print("\\n✅ Saved summary to:", OUTPUT_SUMMARY)
    print("✅ Saved detailed query results to:", OUTPUT_DETAILS)
