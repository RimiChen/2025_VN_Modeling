import json
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

# === File paths ===
KG_PATH = "Data/KGs_Book_0/integrated_kg.json"
ANNOTATION_PATH = "Data/Annotation_Book_0/Story_0_with_IDs.xlsx"
OUTPUT_PATH = "Data/KGs_Book_0/flexible_reasoning_results.csv"

# === Load integrated knowledge graph ===
with open(KG_PATH, "r", encoding="utf-8") as f:
    G = json_graph.node_link_graph(json.load(f))

# === Load annotation file ===
df = pd.read_excel(ANNOTATION_PATH)
macro_events = df["Plot_0"].dropna().unique().tolist()
events = df["Plot_1_ID"].dropna().unique().tolist()

# === Reasoning functions ===
def get_actions_by_macro_event(G, macro):
    actions = set()
    for ev in G.predecessors(macro):
        if G.nodes[ev].get("type") != "event": continue
        for seg in G.predecessors(ev):
            if G.nodes[seg].get("type") != "event_segment": continue
            for panel in G.predecessors(seg):
                if G.nodes[panel].get("type") != "panel": continue
                for a in G.successors(panel):
                    if G.nodes[a].get("type") == "action":
                        actions.add(G.nodes[a]["label"])
    return list(actions)

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

# === Run all queries ===
query_results = []

for macro in macro_events:
    actions = get_actions_by_macro_event(G, macro)
    for a in actions:
        query_results.append({"Query Type": "Action Retrieval", "Target": macro, "Result": a})

for event in events:
    dialogues = get_dialogues_by_event(G, event)
    for d in dialogues:
        query_results.append({"Query Type": "Dialogue Retrieval", "Target": event, "Result": d})

for macro in macro_events:
    panels = get_ordered_panels_by_macro(G, macro)
    for p in panels:
        query_results.append({"Query Type": "Panel Timeline", "Target": macro, "Result": p})

# === Save to CSV ===
Path("./output").mkdir(parents=True, exist_ok=True)
pd.DataFrame(query_results).to_csv(OUTPUT_PATH, index=False)
print(f"✅ Query results saved to: {OUTPUT_PATH}")
