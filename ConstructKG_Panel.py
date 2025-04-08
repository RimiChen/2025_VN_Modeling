import json
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from networkx.readwrite import json_graph

# === Load JSON ===
with open("Data/0_0.json", "r", encoding="utf-8") as f:
    panel_data = json.load(f)["panels"]

# === Node color mapping ===
def generate_bright_color():
    h = random.random()
    s = 0.5 + random.random() * 0.5
    v = 0.7 + random.random() * 0.3
    return mcolors.to_hex(mcolors.hsv_to_rgb([h, s, v]))

node_type_to_color = {}

def get_node_color(node_type):
    if node_type not in node_type_to_color:
        node_type_to_color[node_type] = generate_bright_color()
    return node_type_to_color[node_type]

def get_node_labels(graph):
    labels = {}
    for n, attrs in graph.nodes(data=True):
        labels[n] = attrs.get("label", n)
    return labels

# === Registry to merge action nodes ===
action_registry = {}

# === Graph builder ===
def build_panel_kg(panel, panel_index=0):
    G = nx.DiGraph()

    panel_visual = f"Panel_visual_{panel_index}"
    panel_textual = f"Panel_textual_{panel_index}"
    G.add_node(panel_visual, type="panel_visual", label="Panel Visual")
    G.add_node(panel_textual, type="panel_textual", label="Panel Textual")

    for i, enc in enumerate(panel.get("visual", {}).get("encoders", [])):
        if enc:
            enc_node = f"encoder_{panel_index}_{i}"
            G.add_node(enc_node, type="encoder", label=f"encoder_{i}")
            G.add_edge(enc_node, panel_visual, relation="encodes")

    scene_objs = panel.get("scene", [])
    scene_group = f"Scene_{panel_index}"
    G.add_node(scene_group, type="scene", label=f"Scene {panel_index}")
    G.add_edge(scene_group, panel_visual, relation="appears_in")
    for i, obj in enumerate(scene_objs):
        if obj:
            node_id = f"scene_obj_{panel_index}_{i}"
            G.add_node(node_id, type="scene_obj", label=obj)
            G.add_edge(node_id, scene_group, relation="part_of_scene")

    characters = panel.get("characters", [])
    for char in characters:
        if char:
            G.add_node(char, type="character", label=char)
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_group, relation="located_in")
            visual_node = f"Visual_{char}"
            G.add_node(visual_node, type="character_visual", label=f"Visual of {char}")
            G.add_edge(visual_node, char, relation="visual_of")

    for a_idx, action in enumerate(panel.get("actions", [])):
        parts = action.split()
        if len(parts) >= 3:
            subject = parts[0]
            predicate = parts[1]
            obj = " ".join(parts[2:])
            action_key = predicate.lower()
            if action_key not in action_registry:
                action_node = f"Action({predicate})"
                action_registry[action_key] = action_node
                G.add_node(action_node, type="action", label=predicate)
            else:
                action_node = action_registry[action_key]
            G.add_edge(subject, action_node, relation="performs")
            G.add_edge(action_node, obj, relation="targets")

    for j, dialogue in enumerate(panel.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_index}_{j}"
        G.add_node(d_node, type="dialogue", label=f"Dialogue {j}")
        G.add_edge(d_node, panel_textual, relation="part_of")
        if dialogue:
            text_node = f"text_{panel_index}_{j}"
            G.add_node(text_node, type="text", label=dialogue)
            G.add_edge(text_node, d_node, relation="content_of")

    caption = panel.get("caption")
    if caption:
        c_node = f"Caption_{panel_index}_0"
        G.add_node(c_node, type="caption", label="Caption")
        G.add_edge(c_node, panel_textual, relation="part_of")
        text_node = f"text_caption_{panel_index}"
        G.add_node(text_node, type="text", label=caption)
        G.add_edge(text_node, c_node, relation="content_of")

    return G

# === Build + visualize panel 0 ===
G0 = build_panel_kg(panel_data[0], panel_index=0)

# === Print node details ===


print("\n=== Nodes ===")

for node, data in G0.nodes(data=True):
    # print(f"{node:25s} | type: {data.get('type'):15s} | label: {data.get('label')}")
    node_type = data.get('type') or 'N/A'
    label = data.get('label') or 'N/A'
    print(f"{node:25s} | type: {node_type:15s} | label: {label}")


print("\n=== Edges ===")
for u, v, data in G0.edges(data=True):
    print(f"{u:25s} --[{data.get('relation')}]--> {v}")

# === Save to files ===
nx.write_graphml(G0, "panel_0_kg.graphml")
with open("panel_0_kg.json", "w", encoding="utf-8") as f:
    # json.dump(json_graph.node_link_data(G0), f, indent=2)
    json.dump(json_graph.node_link_data(G0, edges="links"), f, indent=2)

# === Visualize ===
node_colors = [get_node_color(G0.nodes[n].get("type", "")) for n in G0.nodes()]
node_labels = get_node_labels(G0)
# pos = nx.kamada_kawai_layout(G0)

# plt.figure(figsize=(16, 10))
# nx.draw(G0, pos, labels=node_labels, node_color=node_colors, node_size=2000, font_size=9)
# edge_labels = nx.get_edge_attributes(G0, 'relation')
# nx.draw_networkx_edge_labels(G0, pos, edge_labels=edge_labels, font_color='red')
# plt.title("Enhanced Panel 0 Knowledge Graph")
# plt.axis('off')
# plt.tight_layout()
# plt.show()

# Better layout with adjustable repulsion
pos = nx.spring_layout(G0, k=2.0, iterations=100)  # k = spacing between nodes

plt.figure(figsize=(20, 12))  # Larger figure
nx.draw(
    G0, pos,
    labels=node_labels,
    node_color=node_colors,
    node_size=2000,
    font_size=10,
    font_weight='bold',
    edgecolors='black'
)

edge_labels = nx.get_edge_attributes(G0, 'relation')
# nx.draw_networkx_edge_labels(G0, pos, edge_labels=edge_labels, font_color='red')

nx.draw_networkx_nodes(G0, pos, node_color=node_colors, node_size=2000, edgecolors='black')
nx.draw_networkx_labels(G0, pos, labels=node_labels, font_size=10, font_weight='bold')
nx.draw_networkx_edges(G0, pos, arrows=True, connectionstyle='arc3,rad=0.1')
nx.draw_networkx_edge_labels(G0, pos, edge_labels=edge_labels, font_color='red')

plt.title("Panel Knowledge Graph (Non-overlapping Layout)")
plt.axis('off')
plt.tight_layout()
plt.show()
