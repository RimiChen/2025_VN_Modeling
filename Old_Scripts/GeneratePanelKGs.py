import os
import json
import pandas as pd
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

# === CONFIG ===
DATA_DIR = "Data/Annotation_Book_0/"
EXCEL_FILE = "Story_0.xlsx"

# === UTILS ===
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
def build_panel_graph(panel, panel_id, metadata_row):
    G = nx.DiGraph()

    # Panel anchors
    G.add_node(f"Panel_visual_{panel_id}", type="panel_visual", label="Panel Visual")
    G.add_node(f"Panel_textual_{panel_id}", type="panel_textual", label="Panel Textual")

    # Encoders
    for i, enc in enumerate(panel.get("visual", {}).get("encoders", [])):
        if enc:
            enc_node = f"encoder_{panel_id}_{i}"
            G.add_node(enc_node, type="encoder", label=f"encoder_{i}")
            G.add_edge(enc_node, f"Panel_visual_{panel_id}", relation="encodes")

    # Scene
    scene_name = metadata_row.get("Scene") if isinstance(metadata_row, dict) else metadata_row.Scene
    scene_id = f"Scene_{panel_id}"
    G.add_node(scene_id, type="scene", label=scene_name if pd.notna(scene_name) else f"Scene {panel_id}")
    G.add_edge(scene_id, f"Panel_visual_{panel_id}", relation="appears_in")

    for i, obj in enumerate(panel.get("scene", [])):
        if obj:
            obj_id = f"scene_obj_{panel_id}_{i}"
            G.add_node(obj_id, type="scene_obj", label=obj)
            G.add_edge(obj_id, "Scene_objects", relation="is_a")
            G.add_edge(obj_id, scene_id, relation="located_in")
            vis_id = f"Visual_{obj_id}"
            G.add_node(vis_id, type="visual", label=f"Visual of {obj}")
            G.add_edge(vis_id, obj_id, relation="visual_of")

    for char in panel.get("characters", []):
        if char:
            G.add_node(char, type="character", label=char)
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_id, relation="located_in")
            vis_id = f"Visual_{char}"
            G.add_node(vis_id, type="visual", label=f"Visual of {char}")
            G.add_edge(vis_id, char, relation="visual_of")

    for a_idx, action in enumerate(panel.get("actions", [])):
        parts = action.split()
        if len(parts) >= 3:
            subj, pred, obj = parts[0], parts[1], " ".join(parts[2:])
            act_id = f"Action_{panel_id}_{a_idx}"
            G.add_node(act_id, type="action", label=pred)
            G.add_edge(subj, act_id, relation="performs")
            G.add_edge(act_id, obj, relation="targets")

    for j, dialogue in enumerate(panel.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_id}_{j}"
        G.add_node(d_node, type="dialogue", label=f"Dialogue {j}")
        G.add_edge(d_node, f"Panel_textual_{panel_id}", relation="part_of")
        if dialogue:
            text_node = f"text_{panel_id}_{j}"
            G.add_node(text_node, type="text", label=dialogue)
            G.add_edge(text_node, d_node, relation="content_of")

    caption = panel.get("caption")
    if caption:
        c_node = f"Caption_{panel_id}_0"
        G.add_node(c_node, type="caption", label="Caption")
        G.add_edge(c_node, f"Panel_textual_{panel_id}", relation="part_of")
        text_node = f"text_caption_{panel_id}"
        G.add_node(text_node, type="text", label=caption)
        G.add_edge(text_node, c_node, relation="content_of")

    # Event from Excel
    if isinstance(metadata_row, dict):
        plot_2 = metadata_row.get("Plot_2")
        shot = metadata_row.get("Shot")
    else:
        plot_2 = metadata_row.Plot_2 if "Plot_2" in metadata_row else None
        shot = metadata_row.Shot if "Shot" in metadata_row else None

    if pd.notna(plot_2):
        event_id = f"event_{hash(plot_2)%10000}"
        G.add_node(event_id, type="event", label=plot_2)
        G.add_edge(event_id, scene_id, relation="describes")

    if pd.notna(shot):
        shot_id = f"shot_{panel_id}"
        G.add_node(shot_id, type="shot", label=shot)
        G.add_edge(shot_id, f"Panel_visual_{panel_id}", relation="shot_type")

    # Prepare output folder
    output_json_dir = os.path.join("output", "graph_json")
    os.makedirs(output_json_dir, exist_ok=True)

    # Convert to structured JSON
    graph_json = {
        "panel_id": panel_id,
        "nodes": [
            {"id": n, "type": G.nodes[n].get("type"), "label": G.nodes[n].get("label")}
            for n in G.nodes()
        ],
        "edges": [
            {"source": u, "target": v, "relation": d.get("relation")}
            for u, v, d in G.edges(data=True)
        ],
        "annotation": {
            "scene": scene_name if pd.notna(scene_name) else None,
            "event": plot_2 if pd.notna(plot_2) else None,
            "shot": shot if pd.notna(shot) else None,
            "caption": caption,
            "dialogues": panel.get("textual", {}).get("dialogues", []),
            "characters": panel.get("characters", []),
            "actions": panel.get("actions", []),
            "scene_objects": panel.get("scene", [])
        }
    }

    # Save to file
    json_path = os.path.join(output_json_dir, f"{panel_id}.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(graph_json, jf, indent=2, ensure_ascii=False)


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
                    row = metadata.loc[panel_id] if panel_id in metadata.index else {}
                    G = build_panel_graph(panel, panel_id, row)
                    graphs[panel_id] = G

                    # Prepare output folder
                    output_json_dir = os.path.join("output", "graph_json")
                    os.makedirs(output_json_dir, exist_ok=True)

                    # Visualize
                    print(f"Panel {panel_id} | Nodes: {len(G.nodes)} | Edges: {len(G.edges)}")
                    node_colors = [get_node_color(G.nodes[n].get("type", "")) for n in G.nodes()]
                    node_labels = get_node_labels(G)
                    pos = nx.spring_layout(G, k=2.0, iterations=100)

                    # plt.figure(figsize=(16, 12))
                    # nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors='black')
                    # nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)
                    # nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='-|>', arrowsize=20,
                    #                        edge_color='black', width=2, connectionstyle='arc3,rad=0.2')
                    # edge_labels = nx.get_edge_attributes(G, 'relation')
                    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', label_pos=0.6)
                    # plt.title(f"Knowledge Graph for Panel {panel_id}")
                    # plt.axis("off")
                    # plt.tight_layout()
                    # plt.show()

                    # Create output directory for images
                    output_img_dir = os.path.join("output", "visualizations")
                    os.makedirs(output_img_dir, exist_ok=True)

                    # Set up figure
                    plt.figure(figsize=(16, 12))
                    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, edgecolors='black')
                    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)
                    # nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='-|>', arrowsize=20,
                    #                     edge_color='black', width=1, connectionstyle='arc3,rad=0.2')

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

                    edge_labels = nx.get_edge_attributes(G, 'relation')
                    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', label_pos=0.6)

                    # Draw edge labels better positioned
                    nx.draw_networkx_edge_labels(
                        G, pos,
                        edge_labels=edge_labels,
                        font_color='red',
                        label_pos=0.65,
                        rotate=False
                    )
                                                                
                    plt.title(f"Knowledge Graph for Panel {panel_id}")
                    plt.axis("off")
                    plt.tight_layout()

                    # Save figure
                    img_path = os.path.join(output_img_dir, f"{panel_id}.png")
                    plt.savefig(img_path, dpi=300)
                    plt.close()  # Close the figure so it doesn't block





    print(f"\n✅ Stored {len(graphs)} panel-level knowledge graphs.")
    return graphs

# Run
if __name__ == "__main__":
    panel_graphs = main()


    # for pid, G in panel_graphs.items():
    # nx.write_graphml(G, f"{pid}.graphml")