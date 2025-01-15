from Node import *
class Event(Node):
    def __init__(self, node_id: str, data: Any = None):
        super().__init__(node_id, data)

class BigStoryEvent(Event):
    pass

class SmallerStoryEvent(Event):
    pass

class EventSegment(Event):
    def __init__(self, node_id: str, data: Any = None, knowledge_graph: Dict[str, Any] = None):
        """
        Event segment contains a knowledge graph for the comic panel sequence.
        :param knowledge_graph: A dictionary representing the knowledge graph.
        """
        super().__init__(node_id, data)
        self.knowledge_graph = knowledge_graph or {}
