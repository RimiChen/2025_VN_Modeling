from typing import List, Dict, Any

class Node:
    def __init__(self, node_id: str, data: Any = None):
        """
        Base node class for events or entities.
        :param node_id: A unique identifier for the node.
        :param data: Additional data associated with the node.
        """
        self.node_id = node_id
        self.data = data
        self.children: List['Node'] = []
        self.links: List['Node'] = []  # Links to other nodes (non-hierarchical relationships)

    def add_child(self, child: 'Node'):
        """Add a child node (hierarchical relationship)."""
        self.children.append(child)

    def add_link(self, other: 'Node'):
        """Add a link to another node (non-hierarchical relationship)."""
        self.links.append(other)

    def __repr__(self):
        return f"Node(id={self.node_id}, data={self.data}, children={len(self.children)}, links={len(self.links)})"
