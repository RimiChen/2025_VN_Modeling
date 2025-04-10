import os
import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt

# === CONFIG ===
PANEL_KG_DIR = "Data/KGs_Book_0/panel_graphs"
SEQUENCE_KG_FILE = "Data/KGs_Book_0/sequence_kg/sequence_kg.json"
EVENT_KG_FILE = "Data/KGs_Book_0/event_kg/event_kg.json"
OUTPUT_PATH = "Data/KGs_Book_0/integrated_kg.json"
VIS_PATH = "Data/KGs_Book_0/integrated_kg.png"

# === LOAD KGs ===
def load_graph_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json_graph.node_link_graph(json.load(f))

# Merge panel-level graphs
panel_graphs = {}
for fname in os.listdir(PANEL_KG_DIR):
    if fname.endswith(".json"):
        panel_id = fname.replace(".json", "")
        g = load_graph_json(os.path.join(PANEL_KG_DIR, fname))
        panel_graphs[panel_id] = g

# Load sequence and event KGs
G_seq = load_graph_json(SEQUENCE_KG_FILE)
G_event = load_graph_json(EVENT_KG_FILE)

# === MERGE INTO UNIFIED GRAPH ===
G_all = nx.DiGraph()
G_all.update(G_seq)
G_all.update(G_event)

# === Add panel-level content and cross-level edges ===
for panel_id, G_panel in panel_graphs.items():
    G_all.update(G_panel)

    # Find Plot_2_ID from panel graph (we stored it as 'event_segment' node)
    seg_nodes = [n for n, d in G_panel.nodes(data=True) if d.get("type") == "event_segment"]
    if seg_nodes:
        plot_2_id = seg_nodes[0]
        G_all.add_edge(panel_id, plot_2_id, relation="instantiates")

        # Link segment to parent event and macro (if available)
        for u, v, d in G_event.edges(data=True):
            if u == plot_2_id and d.get("relation") == "subevent_of":
                plot_1_id = v
                G_all.add_edge(plot_2_id, plot_1_id, relation="subevent_of")

                for uu, vv, dd in G_event.edges(data=True):
                    if uu == plot_1_id and dd.get("relation") == "subevent_of":
                        G_all.add_edge(plot_1_id, vv, relation="subevent_of")

# === SAVE INTEGRATED GRAPH ===
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(json_graph.node_link_data(G_all), f, indent=2, ensure_ascii=False)

print(f"✅ Unified graph saved to {OUTPUT_PATH}")

# === VISUALIZE (basic) ===
def visualize_graph(G, path, title="Integrated KG"):
    pos = nx.spring_layout(G, k=2.5, iterations=200)
    node_labels = {n: d.get("label", n) for n, d in G.nodes(data=True)}
    node_colors = []
    for _, d in G.nodes(data=True):
        t = d.get("type", "")
        if t == "panel": node_colors.append("skyblue")
        elif t == "event_segment": node_colors.append("lightgreen")
        elif t == "event": node_colors.append("orange")
        elif t == "macro_event": node_colors.append("gold")
        else: node_colors.append("gray")

    plt.figure(figsize=(24, 16))
    nx.draw(G, pos, with_labels=True, labels=node_labels,
            node_color=node_colors, edge_color="black", node_size=1800, font_size=8)
    edge_labels = nx.get_edge_attributes(G, "relation")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', label_pos=0.5)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

visualize_graph(G_all, VIS_PATH)
print(f"🖼️  Visualization saved to {VIS_PATH}")

# === Reasoning Examples (to implement) ===
# def get_all_actions_in_event(G, event_id):
#     # Traverse from event_id → Plot_2_IDs → panels → actions
#     pass

# def get_dialogue_from_macro_event(G, macro_id):
#     pass

# def get_character_paths_across_story(G, char_name):
#     pass


# === Reasoning Functions ===

# def get_panels_in_event_segment(G, segment_id):
#     return [u for u, v, d in G.edges(data=True) if v == segment_id and d["relation"] == "instantiates"]

# def get_event_segments_in_event(G, event_id):
#     return [u for u, v, d in G.edges(data=True) if v == event_id and d["relation"] == "subevent_of"]

# def get_events_in_macro_event(G, macro_id):
#     return [u for u, v, d in G.edges(data=True) if v == macro_id and d["relation"] == "subevent_of"]

# def get_all_actions_in_macro_event(G, macro_id):
#     segments = []
#     for event in get_events_in_macro_event(G, macro_id):
#         segments += get_event_segments_in_event(G, event)
    
#     panels = []
#     for seg in segments:
#         panels += get_panels_in_event_segment(G, seg)
    
#     actions = []
#     for p in panels:
#         actions += [n for n in G.successors(p) if G.nodes[n].get("type") == "action"]
    
#     return actions

# def get_dialogues_in_event(G, event_id):
#     panels = []
#     for seg in get_event_segments_in_event(G, event_id):
#         panels += get_panels_in_event_segment(G, seg)
    
#     dialogue_texts = []
#     for panel in panels:
#         for neighbor in G.successors(panel):
#             if G.nodes[neighbor].get("type") == "dialogue":
#                 for t in G.successors(neighbor):
#                     if G.nodes[t].get("type") == "text":
#                         dialogue_texts.append(G.nodes[t].get("label"))
#     return dialogue_texts

# def get_character_appearance_map(G):
#     appearances = {}
#     for n, d in G.nodes(data=True):
#         if d.get("type") == "character":
#             appearances.setdefault(n, [])
#             for pred in G.predecessors(n):
#                 if G.nodes[pred].get("type") == "panel":
#                     appearances[n].append(pred)
#     return appearances


# # === Example reasoning output ===
# print("🧠 Reasoning Examples:")
# macro_id = "Think of family"
# event_id = "Intro_1"

# actions = get_all_actions_in_macro_event(G_all, macro_id)
# print(f"All actions in macro-event '{macro_id}':", actions)

# dialogues = get_dialogues_in_event(G_all, event_id)
# print(f"Dialogues in event '{event_id}':")
# for line in dialogues:
#     print(" •", line)

# char_map = get_character_appearance_map(G_all)
# for char, panels in char_map.items():
#     print(f"Character '{char}' appears in panels: {panels}")