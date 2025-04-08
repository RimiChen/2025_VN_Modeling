import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import random
import matplotlib.colors as mcolors

# === CONFIG ===
INPUT_JSON = "Data/0_0.json"         # Input panel annotation
PANEL_INDEX = 0                 # Panel to process
GRAPHML_OUT = "panel_0_kg.graphml"
JSON_OUT = "panel_0_kg.json"

# === UTILITIES ===
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
def build_clean_panel_kg(panel, panel_index=0):
    G = nx.DiGraph()

    # Panel anchors
    panel_visual = f"Panel_visual_{panel_index}"
    panel_textual = f"Panel_textual_{panel_index}"
    G.add_node(panel_visual, type="panel_visual", label="Panel Visual")
    G.add_node(panel_textual, type="panel_textual", label="Panel Textual")

    # Encoders
    for i, enc in enumerate(panel.get("visual", {}).get("encoders", [])):
        if enc:
            encoder_node = f"encoder_{panel_index}_{i}"
            G.add_node(encoder_node, type="encoder", label=f"encoder_{i}")
            G.add_edge(encoder_node, panel_visual, relation="encodes")

    # Scene container
    scene_node = f"Scene_{panel_index}"
    G.add_node(scene_node, type="scene", label=f"Scene {panel_index}")
    G.add_edge(scene_node, panel_visual, relation="appears_in")

    # Scene objects
    for i, obj in enumerate(panel.get("scene", [])):
        if obj:
            obj_id = f"scene_obj_{panel_index}_{i}"
            G.add_node(obj_id, type="scene_obj", label=obj)
            G.add_edge(obj_id, "Scene_objects", relation="is_a")
            G.add_edge(obj_id, scene_node, relation="located_in")
            visual_obj = f"Visual_{obj_id}"
            G.add_node(visual_obj, type="visual", label=f"Visual of {obj}")
            G.add_edge(visual_obj, obj_id, relation="visual_of")

    # Characters
    for char in panel.get("characters", []):
        if char:
            G.add_node(char, type="character", label=char)
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_node, relation="located_in")
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
            action_node = f"Action_{panel_index}_{a_idx}"
            G.add_node(action_node, type="action", label=predicate)
            G.add_edge(subject, action_node, relation="performs")
            G.add_edge(action_node, obj, relation="targets")

    # Dialogues
    for j, dialogue in enumerate(panel.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_index}_{j}"
        G.add_node(d_node, type="dialogue", label=f"Dialogue {j}")
        G.add_edge(d_node, panel_textual, relation="part_of")
        if dialogue:
            text_node = f"text_{panel_index}_{j}"
            G.add_node(text_node, type="text", label=dialogue)
            G.add_edge(text_node, d_node, relation="content_of")

    # Caption
    caption = panel.get("caption")
    if caption:
        c_node = f"Caption_{panel_index}_0"
        G.add_node(c_node, type="caption", label="Caption")
        G.add_edge(c_node, panel_textual, relation="part_of")
        text_node = f"text_caption_{panel_index}"
        G.add_node(text_node, type="text", label=caption)
        G.add_edge(text_node, c_node, relation="content_of")

    return G

# === MAIN ===
if __name__ == "__main__":
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        panel_data = json.load(f)["panels"]

    G = build_clean_panel_kg(panel_data[PANEL_INDEX], panel_index=PANEL_INDEX)

    # Save files
    nx.write_graphml(G, GRAPHML_OUT)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(json_graph.node_link_data(G), f, indent=2)

    # Print basic info
    print(f"Saved graph to {GRAPHML_OUT} and {JSON_OUT}")
    print(f"Total nodes: {len(G.nodes)} | Total edges: {len(G.edges)}")

    # Optional: visualize
    node_colors = [get_node_color(G.nodes[n].get("type", "")) for n in G.nodes()]
    node_labels = get_node_labels(G)
    # pos = nx.kamada_kawai_layout(G)

    # plt.figure(figsize=(16, 10))
    # nx.draw(G, pos, labels=node_labels, node_color=node_colors, node_size=2000, font_size=9)
    # edge_labels = nx.get_edge_attributes(G, 'relation')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    # plt.title("Panel Knowledge Graph")
    # plt.axis('off')
    # plt.show()

    # Better layout with adjustable repulsion
    pos = nx.spring_layout(G, k=2.0, iterations=100)  # k = spacing between nodes

    plt.figure(figsize=(20, 12))  # Larger figure
    nx.draw(
        G, pos,
        labels=node_labels,
        node_color=node_colors,
        node_size=2000,
        font_size=10,
        font_weight='bold',
        edgecolors='black'
    )

    edge_labels = nx.get_edge_attributes(G, 'relation')
    # nx.draw_networkx_edge_labels(G0, pos, edge_labels=edge_labels, font_color='red')

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, edgecolors='black')
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G, pos, arrows=True, connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Panel Knowledge Graph (Non-overlapping Layout)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
