import json
import networkx as nx
from networkx.readwrite import json_graph

# === Load the integrated graph ===
with open('Data/KGs_Book_0/integrated_kg.json', 'r', encoding='utf-8') as f:
    G = json_graph.node_link_graph(json.load(f))

# === Reasoning Functions ===

def get_panels_in_event_segment(G, segment_id):
    return [u for u, v, d in G.edges(data=True) if v == segment_id and d["relation"] == "instantiates"]

def get_event_segments_in_event(G, event_id):
    return [u for u, v, d in G.edges(data=True) if v == event_id and d["relation"] == "subevent_of"]

def get_events_in_macro_event(G, macro_id):
    return [u for u, v, d in G.edges(data=True) if v == macro_id and d["relation"] == "subevent_of"]

def get_all_actions_in_macro_event(G, macro_id):
    actions = []
    segments = []
    for event in get_events_in_macro_event(G, macro_id):
        segments += get_event_segments_in_event(G, event)
    for seg in segments:
        panels = get_panels_in_event_segment(G, seg)
        for p in panels:
            actions += [n for n in G.successors(p) if G.nodes[n].get("type") == "action"]
    return actions

def get_dialogues_in_event(G, event_id):
    dialogues = []
    for seg in get_event_segments_in_event(G, event_id):
        panels = get_panels_in_event_segment(G, seg)
        for panel in panels:
            for d in G.successors(panel):
                if G.nodes[d].get("type") == "dialogue":
                    for t in G.successors(d):
                        if G.nodes[t].get("type") == "text":
                            dialogues.append(G.nodes[t].get("label"))
    return dialogues

def get_character_appearance_map(G):
    appearances = {}
    for n, d in G.nodes(data=True):
        if d.get("type") == "character":
            panels = []
            for pred in G.predecessors(n):
                if G.nodes[pred].get("type") == "panel":
                    panels.append(pred)
            if panels:
                appearances[n] = panels
    return appearances

def get_panel_sequence_of_macro_event(G, macro_id):
    sequence = []
    for event in get_events_in_macro_event(G, macro_id):
        for seg in get_event_segments_in_event(G, event):
            sequence += get_panels_in_event_segment(G, seg)
    return sequence

# === Test Examples ===
print("🧠 Reasoning Examples:")

macro_event = "Think of family"
event = "Intro_1"

# All actions in macro-event
actions = get_all_actions_in_macro_event(G, macro_event)
print(f"Actions in macro-event '{macro_event}':")
for a in actions:
    print(" •", G.nodes[a].get("label"))

# Dialogues in an event
dialogues = get_dialogues_in_event(G, event)
print(f"Dialogues in event '{event}':")
for line in dialogues:
    print(" →", line)

# Character appearances
char_map = get_character_appearance_map(G)
for char, panels in char_map.items():
    print(f"Character '{char}' appears in panels:", panels)

# Panel sequence of macro-event
sequence = get_panel_sequence_of_macro_event(G, macro_event)
print(f"Panel sequence in macro-event '{macro_event}':", sequence)
