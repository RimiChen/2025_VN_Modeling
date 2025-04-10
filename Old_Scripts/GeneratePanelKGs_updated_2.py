import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
from networkx.readwrite import json_graph

# === CONFIG ===
DATA_DIR = "Data/Annotation_Book_0/"
EXCEL_FILE = "Story_0_with_IDs.xlsx"
OUTPUT_DIR = "./output/graphs"
IMG_DIR = "./output/visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# === COLOR UTILS ===
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

def get_node_labels(graph):
    return {n: d.get("label", n) for n, d in graph.nodes(data=True)}

# === GRAPH BUILDER ===
def build_panel_graph(panel, panel_id, metadata_row):
    G = nx.DiGraph()

    panel_visual = f"Panel_visual_{panel_id}"
    panel_textual = f"Panel_textual_{panel_id}"
    G.add_node(panel_visual, type="panel_visual", label="Panel Visual")
    G.add_node(panel_textual, type="panel_textual", label="Panel Textual")

    for i, enc in enumerate(panel.get("visual", {}).get("encoders", [])):
        if enc:
            enc_node = f"encoder_{panel_id}_{i}"
            G.add_node(enc_node, type="encoder", label=f"encoder_{i}")
            G.add_edge(enc_node, panel_visual, relation="encodes")

    scene_node = f"Scene_{panel_id}"
    G.add_node(scene_node, type="scene", label=f"Scene {panel_id}")
    G.add_edge(scene_node, panel_visual, relation="appears_in")

    for i, obj in enumerate(panel.get("scene", [])):
        if obj:
            obj_id = f"scene_obj_{panel_id}_{i}"
            G.add_node(obj_id, type="scene_obj", label=obj)
            G.add_edge(obj_id, "Scene_objects", relation="is_a")
            G.add_edge(obj_id, scene_node, relation="located_in")
            visual_obj = f"Visual_{obj_id}"
            G.add_node(visual_obj, type="visual", label=f"Visual of {obj}")
            G.add_edge(visual_obj, obj_id, relation="visual_of")

    for char in panel.get("characters", []):
        if char:
            G.add_node(char, type="character", label=char)
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_node, relation="located_in")
            visual_node = f"Visual_{char}"
            G.add_node(visual_node, type="visual", label=f"Visual of {char}")
            G.add_edge(visual_node, char, relation="visual_of")

    for a_idx, action in enumerate(panel.get("actions", [])):
        parts = action.split()
        if len(parts) >= 3:
            subject = parts[0]
            predicate = parts[1]
            obj = " ".join(parts[2:])
            action_node = f"Action_{panel_id}_{a_idx}"
            G.add_node(action_node, type="action", label=predicate)
            G.add_edge(subject, action_node, relation="performs")
            G.add_edge(action_node, obj, relation="targets")

    for j, dialogue in enumerate(panel.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_id}_{j}"
        G.add_node(d_node, type="dialogue", label=f"Dialogue {j}")
        G.add_edge(d_node, panel_textual, relation="part_of")
        if dialogue:
            t_node = f"text_{panel_id}_{j}"
            G.add_node(t_node, type="text", label=dialogue)
            G.add_edge(t_node, d_node, relation="content_of")

    caption = panel.get("caption")
    if caption:
        c_node = f"Caption_{panel_id}_0"
        G.add_node(c_node, type="caption", label="Caption")
        G.add_edge(c_node, panel_textual, relation="part_of")
        text_node = f"text_caption_{panel_id}"
        G.add_node(text_node, type="text", label=caption)
        G.add_edge(text_node, c_node, relation="content_of")

    # === ADD Plot_2_ID as event_segment node ===
    if isinstance(metadata_row, dict):
        plot_2_id = metadata_row.get("Plot_2_ID")
        plot_2_label = metadata_row.get("Plot_2")
        shot = metadata_row.get("Shot")
    else:
        plot_2_id = metadata_row.Plot_2_ID if "Plot_2_ID" in metadata_row else None
        plot_2_label = metadata_row.Plot_2 if "Plot_2" in metadata_row else None
        shot = metadata_row.Shot if "Shot" in metadata_row else None

    if pd.notna(plot_2_id):
        G.add_node(plot_2_id, type="event_segment", label=plot_2_label)
        G.add_edge(plot_2_id, scene_node, relation="describes")

    if pd.notna(shot):
        shot_node = f"shot_{panel_id}"
        G.add_node(shot_node, type="shot", label=shot)
        G.add_edge(shot_node, panel_visual, relation="shot_type")

    return G

# === MAIN ===
def main():
    metadata = pd.read_excel(os.path.join(DATA_DIR, EXCEL_FILE))
    metadata.set_index("Index", inplace=True)

    graphs = {}
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".json"):
            book_id, page_id = fname.split(".")[0].split("_")
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                panels = data["panels"]
                for i, panel in enumerate(panels):
                    panel_id = f"{book_id}_{page_id}_{i}"
                    metadata_row = metadata.loc[panel_id] if panel_id in metadata.index else {}
                    G = build_panel_graph(panel, panel_id, metadata_row)
                    graphs[panel_id] = G

                    # Save files
                    nx.write_graphml(G, os.path.join(OUTPUT_DIR, f"{panel_id}.graphml"))
                    with open(os.path.join(OUTPUT_DIR, f"{panel_id}.json"), "w", encoding="utf-8") as f:
                        json.dump(json_graph.node_link_data(G), f, indent=2)

                    # Visualize
                    node_colors = [get_node_color(G.nodes[n].get("type", "")) for n in G.nodes()]
                    node_labels = get_node_labels(G)
                    pos = nx.spring_layout(G, k=2.0, iterations=100)

                    plt.figure(figsize=(16, 10))
                    nx.draw(G, pos, labels=node_labels, node_color=node_colors, node_size=2000, font_size=9)
                    edge_labels = nx.get_edge_attributes(G, 'relation')
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
                    plt.title(f"Knowledge Graph for Panel {panel_id}")
                    plt.axis("off")
                    plt.tight_layout()
                    plt.savefig(os.path.join(IMG_DIR, f"{panel_id}.png"), dpi=300)
                    plt.close()

    print(f"✅ Saved {len(graphs)} panel-level graphs.")
    return graphs

# Run it
if __name__ == "__main__":
    panel_graphs = main()
