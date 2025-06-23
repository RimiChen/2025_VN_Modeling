import json
import networkx as nx
import matplotlib.pyplot as plt

# Load the JSON
with open("Data/KGs_Book_0/event_kg/event_kg_partial_33nodes.json", "r") as f:
    data = json.load(f)

# import json
# import networkx as nx
# import matplotlib.pyplot as plt

# # Load the JSON
# with open("event_kg_partial_33nodes.json", "r") as f:
    # data = json.load(f)

# Create a directed graph
G = nx.DiGraph()

# Add nodes
for node in data["nodes"]:
    node_id = node["id"]
    node_type = node.get("type", "")
    label = node.get("label", "")

    # Shorten labels for visualization
    if node_type == "macro_event":
        short_label = label
    elif node_type == "event":
        short_label = f"[E] {label.split('_')[0]}"
    elif node_type == "event_segment":
        short_label = f"[S] {label.split()[0]}"  # Take first word from segment label
    elif node_type == "panel":
        short_label = f"[P] {label}"
    else:
        short_label = label[:10]

    G.add_node(node_id, label=short_label, type=node_type)

# Add edges
for edge in data["links"]:
    G.add_edge(edge["source"], edge["target"], label=edge["relation"])

# === LAYOUT ===
def layered_layout(G):
    layers = {"macro_event": 0, "event": 1, "event_segment": 2, "panel": 3}
    spacing_x = 6
    spacing_y = 6
    pos = {}
    layer_counts = {k: 0 for k in layers}
    for n, d in G.nodes(data=True):
        layer = layers.get(d["type"], 4)
        x = layer_counts[d["type"]] * spacing_x
        y = -layer * spacing_y
        pos[n] = (x, y)
        layer_counts[d["type"]] += 1
    return pos

# Draw
pos = layered_layout(G)
plt.figure(figsize=(28, 20))
nx.draw(
    G, pos, with_labels=False, node_color="#D6EAF8", node_size=5000, edge_color="gray", arrows=True
)

# Draw node labels
node_labels = {n: d["label"] for n, d in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=11)

# Draw edge labels
edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

plt.title("Hierarchical Event Knowledge Graph (Short Labels)", fontsize=18)
plt.axis("off")
plt.tight_layout()
plt.savefig("event_kg_partial_33nodes_shortlabels.png", dpi=300)
plt.show()
