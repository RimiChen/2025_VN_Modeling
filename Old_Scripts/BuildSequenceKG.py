import os
import json
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt

# === CONFIG ===
DATA_DIR = "Data/Annotation_Book_0/"
EXCEL_FILE = "Story_0.xlsx"
OUTPUT_DIR = "output"
SUBGRAPH_DIR = os.path.join(OUTPUT_DIR, "subgraphs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUBGRAPH_DIR, exist_ok=True)

# === LAYOUT FUNCTION ===
def linear_layout(G, panel_order):
    pos = {}
    x_spacing = 3
    y_level = 0

    for i, node in enumerate(panel_order):
        pos[node] = (i * x_spacing, y_level)

    for node in G.nodes:
        if G.nodes[node].get('type') == 'event_segment':
            linked = [u for u, v, d in G.in_edges(node, data=True) if d.get("relation") == "belongs_to"]
            if linked:
                x_avg = sum(pos[p][0] for p in linked if p in pos) / len(linked)
                pos[node] = (x_avg, y_level - 3)
            else:
                pos[node] = ((len(pos)) * x_spacing, y_level - 3)

    return pos

# === VISUALIZATION FUNCTION ===
def visualize_graph(G, file_path, title=""):
    panel_order = [n for n in G.nodes if G.nodes[n].get("type") == "panel"]
    pos = linear_layout(G, panel_order)
    node_labels = {n: d.get("label", n) for n, d in G.nodes(data=True)}

    node_colors = []
    for n, d in G.nodes(data=True):
        if d["type"] == "panel":
            node_colors.append("skyblue")
        elif d["type"] == "event_segment":
            node_colors.append("orange")
        else:
            node_colors.append("gray")

    plt.figure(figsize=(22, 12))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors="black")
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)

    # Draw edges by type
    edge_labels = nx.get_edge_attributes(G, 'relation')
    for rel_type, color, style in [
        ("next", "black", "solid"),
        ("belongs_to", "gray", "dashed"),
        ("precedes_storytime", "red", "solid")
    ]:
        edges = [(u, v) for u, v, d in G.edges(data=True) if d["relation"] == rel_type]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color,
                               arrows=True, arrowstyle="-|>", arrowsize=25, width=1,
                               connectionstyle='arc3,rad=0.2', style=style)
        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels={k: v for k, v in edge_labels.items() if k in edges},
                                     font_color=color, label_pos=0.6)

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()

# === MAIN FUNCTION ===
def main():
    df = pd.read_excel(os.path.join(DATA_DIR, EXCEL_FILE))
    df = df.dropna(subset=["Index"]).reset_index(drop=True)

    # Inherit missing Plot_1 and Narrative_Time
    df["Plot_1"] = df["Plot_1"].fillna(method="ffill")
    df["Narrative_Time"] = df["Narrative_Time"].fillna(method="ffill")

    # Sort panels by reading order
    df = df.sort_values(by="Index", key=lambda col: col.map(lambda x: tuple(map(int, x.split("_")))))

    G = nx.DiGraph()
    event_panels = {}
    event_narrative_time = {}

    for _, row in df.iterrows():
        panel_id = row["Index"]
        plot1 = row["Plot_1"]
        narrative_time = row["Narrative_Time"]

        # Add panel node
        G.add_node(panel_id, type="panel", label=panel_id)

        # Add event node if not exists
        if plot1 not in G:
            # G.add_node(plot1, type="event_segment", label=plot1)
            # event_narrative_time[plot1] = narrative_time
            G.add_node(plot1, type="event_segment", label=plot1, narrative_time=narrative_time)
            event_narrative_time[plot1] = narrative_time


        # Link panel to event
        G.add_edge(panel_id, plot1, relation="belongs_to")
        event_panels.setdefault(plot1, []).append(panel_id)

    # Add next edges within each event
    for panel_list in event_panels.values():
        for i in range(len(panel_list) - 1):
            G.add_edge(panel_list[i], panel_list[i+1], relation="next")

    # Add inter-event sequence by reading order (for visualization)
    ordered_events = list(event_panels.keys())
    for i in range(len(ordered_events) - 1):
        G.add_edge(ordered_events[i], ordered_events[i+1], relation="reading_order")

    # Add inter-event storytime order
    sorted_events = sorted(event_narrative_time.items(), key=lambda x: str(x[1]))
    for i in range(len(sorted_events) - 1):
        e1, e2 = sorted_events[i][0], sorted_events[i+1][0]
        if e1 != e2:
            G.add_edge(e1, e2, relation="precedes_storytime")

    # Save full graph
    full_json = os.path.join(OUTPUT_DIR, "temporal_kg.json")
    with open(full_json, "w", encoding="utf-8") as f:
        json.dump(json_graph.node_link_data(G), f, indent=2, ensure_ascii=False)

    full_img = os.path.join(OUTPUT_DIR, "temporal_kg.png")
    visualize_graph(G, full_img, title="Unified Temporal Knowledge Graph (Dual Flow)")

    print(f"✅ Unified KG saved to: {full_json}")
    print(f"🖼️  Visualization saved to: {full_img}")

    # Save each subgraph with ordered filenames
    for idx, (event, panels) in enumerate(event_panels.items(), start=1):
        sub_nodes = panels + [event]
        G_sub = G.subgraph(sub_nodes).copy()
        prefix = f"{idx:02d}_{event}"

        sub_json = os.path.join(SUBGRAPH_DIR, f"{prefix}.json")
        with open(sub_json, "w", encoding="utf-8") as f:
            json.dump(json_graph.node_link_data(G_sub), f, indent=2, ensure_ascii=False)

        sub_img = os.path.join(SUBGRAPH_DIR, f"{prefix}.png")
        visualize_graph(G_sub, sub_img, title=f"Subgraph: {event} (Storytime: {event_narrative_time[event]})")

    print(f"🗂️  All subgraphs saved to {SUBGRAPH_DIR}")

if __name__ == "__main__":
    main()