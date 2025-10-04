import json
import networkx as nx
import matplotlib.pyplot as plt

def load_partial_graph(json_path, max_nodes=12):
    with open(json_path, 'r') as f:
        data = json.load(f)

    G = nx.DiGraph()

    # Extract all valid nodes first
    node_list = [node for node in data['nodes'] if isinstance(node, dict)]
    node_id_set = set()
    for node in node_list[:max_nodes]:
        node_id = node['id']
        node_id_set.add(node_id)
        label = node.get('label', node_id)
        G.add_node(node_id, label=label)

    # Add edges if both ends are in selected node set
    for edge in data['links']:
        src = edge['source']
        tgt = edge['target']
        rel = edge.get('relation', '')
        if src in node_id_set and tgt in node_id_set:
            G.add_edge(src, tgt, label=rel)

    return G

def draw_graph(G, out_file=None):
    pos = nx.shell_layout(G)

    node_labels = nx.get_node_attributes(G, 'label')
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color="#AED6F1", node_size=1000)
    nx.draw_networkx_edges(G, pos, edge_color="#5D6D7E", arrows=True, arrowstyle='-|>', width=2)

    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=20, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='green', font_size=15, label_pos=0.55)

    plt.axis("off")
    if out_file:
        plt.tight_layout()
        plt.savefig(out_file)
        print(f"Graph saved to {out_file}")
    else:
        plt.show()

# ===== Usage =====
json_path = "Data/KGs_Book_0/sequence_kg/sequence_kg.json"  # Update path if needed
MAX_NODES = 12  # Change this number to control graph complexity
G = load_partial_graph(json_path, max_nodes=MAX_NODES)
draw_graph(G)
