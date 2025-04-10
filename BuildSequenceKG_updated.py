import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

# === CONFIG ===
DATA_DIR = "Data/Annotation_Book_0/"
EXCEL_FILE = "Story_0_with_IDs.xlsx"
OUTPUT_DIR = "./output/sequence_kg"
SUBGRAPH_DIR = os.path.join(OUTPUT_DIR, "subgraphs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUBGRAPH_DIR, exist_ok=True)

# === LOAD DATA ===
df = pd.read_excel(os.path.join(DATA_DIR, EXCEL_FILE))
df = df.dropna(subset=["Index", "Plot_1_ID"]).reset_index(drop=True)
df["Narrative_Time"] = df["Narrative_Time"].fillna(method="ffill")

# === CREATE GRAPH ===
G = nx.DiGraph()
event_panels = {}

for _, row in df.iterrows():
    panel_id = row["Index"]
    plot1 = row["Plot_1_ID"]
    plot1_label = row["Plot_1"]

    G.add_node(panel_id, type="panel", label=panel_id)
    G.add_node(plot1, type="event_segment", label=plot1_label)
    G.add_edge(panel_id, plot1, relation="belongs_to")
    event_panels.setdefault(plot1, []).append(panel_id)

# === ADD INTRA-EVENT PANEL SEQUENCES ===
for panels in event_panels.values():
    for i in range(len(panels) - 1):
        G.add_edge(panels[i], panels[i + 1], relation="next")

# === ADD INTER-EVENT READING ORDER (BY PANEL OCCURRENCE) ===
event_sequence = list(df.drop_duplicates("Plot_1_ID")["Plot_1_ID"])
for i in range(len(event_sequence) - 1):
    G.add_edge(event_sequence[i], event_sequence[i + 1], relation="precedes_reading")

# === ADD INTER-EVENT STORYTIME ORDER (FROM NARRATIVE_TIME) ===
narrative_order = (
    df.drop_duplicates("Plot_1_ID")[["Plot_1_ID", "Narrative_Time"]]
    .sort_values(by="Narrative_Time")
)["Plot_1_ID"].tolist()

for i in range(len(narrative_order) - 1):
    src = narrative_order[i]
    tgt = narrative_order[i + 1]
    if src != tgt:
        G.add_edge(src, tgt, relation="precedes_storytime")

# === SAVE FULL GRAPH ===
with open(os.path.join(OUTPUT_DIR, "sequence_kg.json"), "w", encoding="utf-8") as f:
    json.dump(json_graph.node_link_data(G), f, indent=2, ensure_ascii=False)

# === VISUALIZATION FUNCTION ===
def visualize_graph(graph, file_path, title=""):
    pos = nx.spring_layout(graph, k=2.0, iterations=100)
    node_labels = {n: d["label"] for n, d in graph.nodes(data=True)}
    node_colors = ["skyblue" if d["type"] == "panel" else "orange" for _, d in graph.nodes(data=True)]

    plt.figure(figsize=(20, 14))
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1200, edgecolors="black")
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=9)

    edge_labels = nx.get_edge_attributes(graph, "relation")
    edge_styles = {
        "belongs_to": {"color": "gray", "style": "dashed"},
        "next": {"color": "black", "style": "solid"},
        "precedes_reading": {"color": "blue", "style": "dashed"},
        "precedes_storytime": {"color": "red", "style": "solid"},
    }

    for rel_type, style in edge_styles.items():
        edges = [(u, v) for u, v, d in graph.edges(data=True) if d["relation"] == rel_type]
        nx.draw_networkx_edges(graph, pos, edgelist=edges,
                               edge_color=style["color"], style=style["style"],
                               arrows=True, arrowstyle="-|>", arrowsize=25,
                               connectionstyle="arc3,rad=0.2", width=2)
        nx.draw_networkx_edge_labels(graph, pos,
                                     edge_labels={k: v for k, v in edge_labels.items() if k in edges},
                                     font_color=style["color"], label_pos=0.6)

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()

# === VISUALIZE FULL GRAPH ===
visualize_graph(G, os.path.join(OUTPUT_DIR, "sequence_kg.png"), "Full Sequence KG")

# === EXPORT PER-EVENT SUBGRAPHS ===
for idx, (event, panels) in enumerate(event_panels.items(), start=1):
    sub_nodes = panels + [event]
    G_sub = G.subgraph(sub_nodes).copy()
    prefix = f"{idx:02d}_{event}"

    with open(os.path.join(SUBGRAPH_DIR, f"{prefix}.json"), "w", encoding="utf-8") as f:
        json.dump(json_graph.node_link_data(G_sub), f, indent=2, ensure_ascii=False)

    visualize_graph(G_sub, os.path.join(SUBGRAPH_DIR, f"{prefix}.png"), f"Subgraph: {event}")

print("✅ Sequence KG + subgraphs saved.")
