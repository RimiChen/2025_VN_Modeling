import json
import networkx as nx
import matplotlib.pyplot as plt

def load_graph_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    G = nx.DiGraph()

    nodes = data.get("nodes", [])
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        label = node.get("label", "")
        if node_id:
            G.add_node(node_id, label=label)

    links = data.get("links", [])
    for link in links:
        if not isinstance(link, dict):
            continue
        source = link.get("source")
        target = link.get("target")
        relation = link.get("relation", "")
        if source and target:
            G.add_edge(source, target, label=relation)

    return G

def draw_graph(G, title="Knowledge Graph", out_file=None):
    pos = nx.shell_layout(G)

    node_labels = nx.get_node_attributes(G, 'label')
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, labels=node_labels,
            node_color="#A0CBE2", node_size=3000,
            font_size=12, font_weight='bold',
            edge_color="gray", width=1.5, arrows=True)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_color='darkred', font_size=11)

    plt.title(title, fontsize=16)
    plt.axis('off')
    if out_file:
        plt.savefig(out_file, bbox_inches='tight', dpi=300)
        print(f"Saved to {out_file}")
    else:
        plt.show()

if __name__ == "__main__":
    json_path = "Data/KGs_Book_0/panel_graphs/0_0_4.json"  # Adjust path if needed
    G = load_graph_from_json(json_path)
    draw_graph(G, out_file="Data/KGs_Book_0/panel_kg_example.png")


# if __name__ == "__main__":
#     json_path = "Data/KGs_Book_0/panel_graphs/0_0_1.json"  # update path if needed
#     G = load_graph_from_json(json_path)
#     draw_graph(G, out_file="Data/KGs_Book_0/panel_kg_example.png")


