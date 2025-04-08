import os
import json
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

# === CONFIG ===
BOOK_ID = 0
JSON_FILE = f"Data/{BOOK_ID}_0.json"
EXCEL_FILE = "Data/Story_0.xlsx"
OUTPUT_DIR = "graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === HELPERS ===
def generate_bright_color():
    h = random.random()
    s = 0.6 + random.random() * 0.4
    v = 0.7 + random.random() * 0.3
    return mcolors.to_hex(mcolors.hsv_to_rgb([h, s, v]))

node_type_to_color = {}
def get_node_color(node_type):
    if node_type not in node_type_to_color:
        node_type_to_color[node_type] = generate_bright_color()
    return node_type_to_color[node_type]

def get_node_labels(G):
    return {n: d.get("label", n) for n, d in G.nodes(data=True)}

# === GRAPH BUILDER ===
def build_graph_from_panel(panel, panel_idx_str, metadata):
    G = nx.DiGraph()

    # Anchors
    panel_visual = f"Panel_visual_{panel_idx_str}"
    panel_textual = f"Panel_textual_{panel_idx_str}"
    G.add_node(panel_visual, type="panel_visual", label="Panel Visual")
    G.add_node(panel_textual, type="panel_textual", label="Panel Textual")

    # Encoders
    for i, enc in enumerate(panel.get("visual", {}).get("encoders", [])):
        if enc:
            enc_node = f"encoder_{panel_idx_str}_{i}"
            G.add_node(enc_node, type="encoder", label=f"encoder_{i}")
            G.add_edge(enc_node, panel_visual, relation="encodes")

    # Scene (from Excel or default)
    scene_name = metadata.get("Scene")
    scene_id = f"Scene_{panel_idx_str}"
    G.add_node(scene_id, type="scene", label=scene_name if pd.notna(scene_name) else f"Scene {panel_idx_str}")
    G.add_edge(scene_id, panel_visual, relation="appears_in")

    # Scene objects
    for i, obj in enumerate(panel.get("scene", [])):
        if obj:
            obj_id = f"scene_obj_{panel_idx_str}_{i}"
            G.add_node(obj_id, type="scene_obj", label=obj)
            G.add_edge(obj_id, "Scene_objects", relation="is_a")
            G.add_edge(obj_id, scene_id, relation="located_in")
            visual_id = f"Visual_{obj_id}"
            G.add_node(visual_id, type="visual", label=f"Visual of {obj}")
            G.add_edge(visual_id, obj_id, relation="visual_of")

    # Characters
    for char in panel.get("characters", []):
        if char:
            G.add_node(char, type="character", label=char)
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_id, relation="located_in")
            visual_node = f"Visual_{char}"
            G.add_node(visual_node, type="visual", label=f"Visual of {char}")
            G.add_edge(visual_node, char, relation="visual_of")

    # Actions
    for a_idx, action in enumerate(panel.get("actions", [])):
        parts = action.split()
        if len(parts) >= 3:
            subject = parts[0]
            predicate = parts[1]
            obj = " ".join(parts[2:])
            action_node = f"Action_{panel_idx_str}_{a_idx}"
            G.add_node(action_node, type="action", label=predicate)
            G.add_edge(subject, action_node, relation="performs")
            G.add_edge(action_node, obj, relation="targets")

    # Dialogue and caption
    for j, dialogue in enumerate(panel.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_idx_str}_{j}"
        G.add_node(d_node, type="dialogue", label=f"Dialogue {j}")
        G.add_edge(d_node, panel_textual, relation="part_of")
        if dialogue:
            t_node = f"text_{panel_idx_str}_{j}"
            G.add_node(t_node, type="text", label=dialogue)
            G.add_edge(t_node, d_node, relation="content_of")

    caption = panel.get("caption")
    if caption:
        c_node = f"Caption_{panel_idx_str}_0"
        G.add_node(c_node, type="caption", label="Caption")
        G.add_edge(c_node, panel_textual, relation="part_of")
        text_node = f"text_caption_{panel_idx_str}"
        G.add_node(text_node, type="text", label=caption)
        G.add_edge(text_node, c_node, relation="content_of")

    # === Additional Metadata from Excel ===
    # Event
    event = metadata.get("Plot_2")
    if pd.notna(event):
        event_node = f"event_{hash(event)%10000}"  # hashed to reuse across panels
        G.add_node(event_node, type="event", label=event)
        G.add_edge(event_node, scene_id, relation="describes")

    # Shot
    shot = metadata.get("Shot")
    if pd.notna(shot):
        shot_node = f"shot_{panel_idx_str}"
        G.add_node(shot_node, type="shot", label=shot)
        G.add_edge(shot_node, panel_visual, relation="shot_type")

    return G

# === MAIN ===
def main():
    # Load metadata
    df = pd.read_excel(EXCEL_FILE)
    df.set_index("Index", inplace=True)

    # Load panels
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        panel_list = json.load(f)["panels"]

    for i, panel in enumerate(panel_list):
        panel_idx_str = f"{BOOK_ID}_0_{i}"
        metadata = df.loc[panel_idx_str] if panel_idx_str in df.index else {}
        G = build_graph_from_panel(panel, panel_idx_str, metadata)

        # Save
        graphml_path = os.path.join(OUTPUT_DIR, f"{panel_idx_str}.graphml")
        json_path = os.path.join(OUTPUT_DIR, f"{panel_idx_str}.json")
        nx.write_graphml(G, graphml_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_graph.node_link_data(G), f, indent=2)

        # Display
        print(f"\n=== Panel {panel_idx_str} ===")
        print(f"Nodes: {len(G.nodes)} | Edges: {len(G.edges)}")

        node_colors = [get_node_color(G.nodes[n].get("type", "")) for n in G.nodes()]
        node_labels = get_node_labels(G)
        edge_labels = nx.get_edge_attributes(G, 'relation')
        pos = nx.spring_layout(G, k=2.0, iterations=100)
        # pos = nx.spring_layout(G, k=3.0, iterations=100)
        # pos = nx.spring_layout(G, k=5.0, iterations=100)
        # pos = nx.kamada_kawai_layout(G)
        # pos = nx.shell_layout(G)
        # pos = nx.circular_layout(G)
        # pos = nx.spectral_layout(G)
        # pos = nx.planar_layout(G)
        # pos = nx.shell_layout(G)
        # # Manually spread positions
        # for key in pos:
        #     pos[key] *= 3

        plt.figure(figsize=(20, 14))
        # nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1800, edgecolors='black')

        # nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black')
        # nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold')
        # nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='-|>',arrowsize=15, connectionstyle='arc3,rad=0.1')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors='black')
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold')

        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=25,
            edge_color='black',
            width=1,
            connectionstyle='arc3,rad=0.1'
        )

        # Draw edge labels better positioned
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_color='red',
            label_pos=0.65,
            rotate=False
        )
                
        plt.title(f"Knowledge Graph: {panel_idx_str}")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()