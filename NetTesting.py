import networkx as nx
import matplotlib.pyplot as plt

### self implemented classes
from Node import *
from Event import *
from Panel import *

# Example function to create a graph using NetworkX
def build_hierarchical_graph(root_event):
    """
    Build a NetworkX graph from a hierarchical event structure.
    :param root_event: Root node of the hierarchical event structure.
    :return: A NetworkX graph.
    """
    graph = nx.DiGraph()  # Directed graph for hierarchical structure

    def add_to_graph(node, parent=None):
        graph.add_node(node.node_id, data=node.data)
        if parent:
            graph.add_edge(parent.node_id, node.node_id)  # Add edge to parent
        for child in node.children:
            add_to_graph(child, node)

    add_to_graph(root_event)
    return graph

# Visualization function
def visualize_graph(graph, title="Hierarchical Event Graph"):
    pos = nx.spring_layout(graph)  # Layout for nodes
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10)
    labels = nx.get_node_attributes(graph, 'data')
    nx.draw_networkx_labels(graph, pos, labels=labels, font_color="black")
    plt.title(title)
    plt.show()

# Example usage with previously defined classes
big_event = BigStoryEvent("big_event", data="The whole plot")
smaller_event1 = SmallerStoryEvent("smaller_event1", data="Act 1")
smaller_event2 = SmallerStoryEvent("smaller_event2", data="Act 2")
big_event.add_child(smaller_event1)
big_event.add_child(smaller_event2)

segment1 = EventSegment("segment1", data="Intro", knowledge_graph={"theme": "setup", "location": "village"})
smaller_event1.add_child(segment1)

# Build and visualize the graph
graph = build_hierarchical_graph(big_event)
visualize_graph(graph)