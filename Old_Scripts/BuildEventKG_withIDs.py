import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

# === CONFIG ===
EXCEL_FILE = "Story_0_sub_with_IDs.xlsx"
DATA_DIR = "Data/Annotation_Book_0/SubForPaperVisual/"
OUTPUT_DIR = "./output/event_kg"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === LAYERED LAYOUT FUNCTION ===
def layered_layout(G):
    layers = {
        "macro_event": 0,
        "event": 1,
        "event_segment": 2,
        "panel": 3,
    }
    spacing = 5
    pos = {}
    layer_counts = {k: 0 for k in layers}

    for n, data in G.nodes(data=True):
        layer = layers.get(data["type"], 4)
        x = layer_counts[data["type"]] * spacing
        y = -layer * 4  # Top-down layout
        pos[n] = (x, y)
        layer_counts[data["type"]] += 1

    return pos

# === LOAD & PREPROCESS DATA ===
df = pd.read_excel(os.path.join(DATA_DIR, EXCEL_FILE))
df = df.dropna(subset=["Index"]).reset_index(drop=True)

# === BUILD GRAPH ===
G = nx.DiGraph()

for _, row in df.iterrows():
    panel_id = str(row["Index"])
    plot_0 = str(row["Plot_0"])
    plot_1 = str(row["Plot_1"])
    plot_2 = str(row["Plot_2"])
    plot_1_id = str(row["Plot_1_ID"])
    plot_2_id = str(row["Plot_2_ID"])

    # Add nodes
    G.add_node(plot_0, type="macro_event", label=plot_0)
    G.add_node(plot_1_id, type="event", label=plot_1)
    G.add_node(plot_2_id, type="event_segment", label=plot_2)
    G.add_node(panel_id, type="panel", label=panel_id)

    # Add edges
    G.add_edge(plot_1_id, plot_0, relation="subevent_of")
    G.add_edge(plot_2_id, plot_1_id, relation="subevent_of")
    G.add_edge(panel_id, plot_2_id, relation="instantiates")

# OPTIONAL: add storytime order between Plot_1_IDs
story_order = [
    ("Intro_1", "Get new rice_cooker_1"),
    ("Think of family_1", "Message from family_1")
]
for src, tgt in story_order:
    if src in G.nodes and tgt in G.nodes:
        G.add_edge(src, tgt, relation="precedes_storytime")

# === EXPORT GRAPH ===
json_path = os.path.join(OUTPUT_DIR, "event_kg.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_graph.node_link_data(G), f, indent=2, ensure_ascii=False)

# === VISUALIZE ===
pos = layered_layout(G)
node_labels = {n: d["label"] for n, d in G.nodes(data=True)}

# Color by node type
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

plt.figure(figsize=(24, 16))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800, edgecolors="black")
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)

edge_labels = nx.get_edge_attributes(G, "relation")
for rel_type, color, style in [
    ("subevent_of", "black", "solid"),
    ("instantiates", "gray", "dashed"),
    ("precedes_storytime", "red", "solid")
]:
    edges = [(u, v) for u, v, d in G.edges(data=True) if d["relation"] == rel_type]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color,
                           arrows=True, arrowstyle="-|>", arrowsize=20,
                           connectionstyle='arc3,rad=0.2', width=2, style=style)
    nx.draw_networkx_edge_labels(G, pos,
                                 edge_labels={k: v for k, v in edge_labels.items() if k in edges},
                                 font_color='red', label_pos=0.6)

plt.title("Hierarchical Event KG with Disambiguated IDs", fontsize=14)
plt.axis("off")
plt.tight_layout()
img_path = os.path.join(OUTPUT_DIR, "event_kg.png")
plt.savefig(img_path, dpi=300)
plt.close()

print(f"✅ Event KG saved to {json_path}")
print(f"🖼️  Visualization saved to {img_path}")