import json
import networkx as nx
from networkx.readwrite import json_graph
import pandas as pd
from pathlib import Path

# === Load Integrated Graph ===
with open("Data/KGs_Book_0/integrated_kg.json", "r", encoding="utf-8") as f:
    G = json_graph.node_link_graph(json.load(f))

# === Full List of Macro-events and Events ===
macro_events = [
    "Think of family", "Message from family", 
    "Shock by message - financial problem", "Ask advices"
]
events = [
    "Intro_1", "Get new rice_cooker_1", "Test new rice_cooker_1", "Eat and think family_1",
    "Intro_2", "Saw a friend is taking letter_1", "Saw a friend tear letter_1", "Say hi and ask reasons_1",
    "Get own letter_1", "Read letter_1", "Shocked by content_1", "Describe and explain content_1",
    "Understand the family decision_1", "Thiank about situation_1", "Discuss about situation and ask suggestions_1",
    "Give surprised suggestions_1", "shocked by the suggestion_1", "Intro to pointing out personality_1"
]

# === Reasoning Functions ===
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

# === Run Queries and Store Results ===
query_results = []

# Action Retrieval
for m in macro_events:
    results = get_actions_by_macro_event(G, m)
    for r in results:
        query_results.append({"Query Type": "Action Retrieval", "Target": m, "Result": r})

# Dialogue Retrieval
for e in events:
    results = get_dialogues_by_event(G, e)
    for r in results:
        query_results.append({"Query Type": "Dialogue Retrieval", "Target": e, "Result": r})

# Panel Timeline
for m in macro_events:
    results = get_ordered_panels_by_macro(G, m)
    for r in results:
        query_results.append({"Query Type": "Panel Timeline", "Target": m, "Result": r})

# === Export as CSV ===
df = pd.DataFrame(query_results)
Path("./output").mkdir(parents=True, exist_ok=True)
df.to_csv("./output/full_reasoning_queries.csv", index=False)

print("✅ Finished running all queries. Results saved to './output/full_reasoning_queries.csv'")
