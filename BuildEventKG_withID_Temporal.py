import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

# === CONFIG ===
# EXCEL_FILE = "Story_0_sub_with_IDs.xlsx"
# DATA_DIR = "Data/Annotation_Book_0/SubForPaperVisual/"
# OUTPUT_DIR = "./output/event_kg_full"
EXCEL_FILE = "Story_0_with_IDs.xlsx"
DATA_DIR = "Data/Annotation_Book_0/"
OUTPUT_DIR = "./output/event_kg_full"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === LAYOUT ===
def layered_layout(G):
    layers = {"macro_event": 0, "event": 1, "event_segment": 2, "panel": 3}
    spacing = 5
    pos = {}
    layer_counts = {k: 0 for k in layers}
    for n, d in G.nodes(data=True):
        layer = layers.get(d["type"], 4)
        x = layer_counts[d["type"]] * spacing
        y = -layer * 4  # top-down
        pos[n] = (x, y)
        layer_counts[d["type"]] += 1
    return pos

# === LOAD & PREPARE ===
df = pd.read_excel(os.path.join(DATA_DIR, EXCEL_FILE))
df = df.dropna(subset=["Index"]).reset_index(drop=True)

G = nx.DiGraph()

# === ADD STRUCTURE ===
for _, row in df.iterrows():
    panel_id = str(row["Index"])
    plot_0 = str(row["Plot_0"])
    plot_1 = str(row["Plot_1"])
    plot_2 = str(row["Plot_2"])
    plot_1_id = str(row["Plot_1_ID"])
    plot_2_id = str(row["Plot_2_ID"])

    G.add_node(plot_0, type="macro_event", label=plot_0)
    G.add_node(plot_1_id, type="event", label=plot_1)
    G.add_node(plot_2_id, type="event_segment", label=plot_2)
    G.add_node(panel_id, type="panel", label=panel_id)

    G.add_edge(plot_1_id, plot_0, relation="subevent_of")
    G.add_edge(plot_2_id, plot_1_id, relation="subevent_of")
    G.add_edge(panel_id, plot_2_id, relation="instantiates")

# === ADD TEMPORAL: READING ORDER ===

## A. Between panels
panel_ids = df["Index"].astype(str).tolist()
for i in range(len(panel_ids) - 1):
    G.add_edge(panel_ids[i], panel_ids[i+1], relation="precedes_reading")

## B. Between segments
first_segment_ids = df.drop_duplicates("Plot_2_ID")["Plot_2_ID"].tolist()
for i in range(len(first_segment_ids) - 1):
    src, tgt = first_segment_ids[i], first_segment_ids[i+1]
    if src != tgt and src in G.nodes and tgt in G.nodes:
        G.add_edge(src, tgt, relation="precedes_reading")

## C. Between events
first_event_ids = df.drop_duplicates("Plot_1_ID")["Plot_1_ID"].tolist()
for i in range(len(first_event_ids) - 1):
    src, tgt = first_event_ids[i], first_event_ids[i+1]
    if src != tgt and src in G.nodes and tgt in G.nodes:
        G.add_edge(src, tgt, relation="precedes_reading")

# === ADD MANUAL STORYTIME TEMPORAL EDGES (override)
story_order = [
    ("Intro_1", "Get new rice_cooker_1"),
    ("Think of family_1", "Message from family_1")
]
for src, tgt in story_order:
    if src in G.nodes and tgt in G.nodes:
        G.add_edge(src, tgt, relation="precedes_storytime")

# === EXPORT JSON ===
with open(os.path.join(OUTPUT_DIR, "event_kg.json"), "w", encoding="utf-8") as f:
    json.dump(json_graph.node_link_data(G), f, indent=2, ensure_ascii=False)

# === VISUALIZE ===
pos = layered_layout(G)
node_labels = {n: d["label"] for n, d in G.nodes(data=True)}

node_colors = []
for _, d in G.nodes(data=True):
    if d["type"] == "macro_event":
        node_colors.append("gold")
    elif d["type"] == "event":
        node_colors.append("orange")
    elif d["type"] == "event_segment":
        node_colors.append("lightgreen")
    elif d["type"] == "panel":
        node_colors.append("skyblue")
    else:
        node_colors.append("gray")

plt.figure(figsize=(30, 18))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors="black")
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)

edge_labels = nx.get_edge_attributes(G, "relation")
edge_styles = {
    "subevent_of": {"color": "black", "style": "solid"},
    "instantiates": {"color": "gray", "style": "dashed"},
    "precedes_storytime": {"color": "red", "style": "solid"},
    "precedes_reading": {"color": "blue", "style": "dashed"},
}

for rel_type, style in edge_styles.items():
    edges = [(u, v) for u, v, d in G.edges(data=True) if d["relation"] == rel_type]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=style["color"],
                           arrows=True, arrowstyle="-|>", arrowsize=25,
                           connectionstyle='arc3,rad=0.2', width=1, style=style["style"])
    nx.draw_networkx_edge_labels(G, pos,
        edge_labels={k: v for k, v in edge_labels.items() if k in edges},
        font_color=style["color"], label_pos=0.6)#, font_size=18)

plt.title("Hierarchical Event KG with Reading & Narrative Time", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "event_kg_full.png"), dpi=300)
plt.close()

print("✅ Saved: JSON + PNG with full temporal structure.")