from Node import *

class Panel(Node):
    def __init__(self, node_id: str, content_graph: Dict[str, Any] = None):
        """
        Panel node contains a small knowledge graph describing its content.
        :param content_graph: A dictionary representing the panel's knowledge graph.
        """
        super().__init__(node_id)
        self.content_graph = content_graph or {}
