
### self implemented classes
from Node import *
from Event import *
from Panel import *

# Create a big story event
big_event = BigStoryEvent("big_event", data="The whole plot")

# Create smaller story events
smaller_event1 = SmallerStoryEvent("smaller_event1", data="Act 1")
smaller_event2 = SmallerStoryEvent("smaller_event2", data="Act 2")

# Add smaller events to the big story event
big_event.add_child(smaller_event1)
big_event.add_child(smaller_event2)

# Create event segments
segment1 = EventSegment("segment1", data="Intro", knowledge_graph={"theme": "setup", "location": "village"})
segment2 = EventSegment("segment2", data="Conflict", knowledge_graph={"theme": "battle", "location": "forest"})

# Add event segments to a smaller story event
smaller_event1.add_child(segment1)
smaller_event1.add_child(segment2)

# Create panels for an event segment
panel1 = Panel("panel1", content_graph={"character": "hero", "action": "walking"})
panel2 = Panel("panel2", content_graph={"character": "villain", "action": "watching"})

# Add panels to an event segment
segment1.add_child(panel1)
segment1.add_child(panel2)

# Example of linking nodes (e.g., a panel links to another panel or event)
panel1.add_link(panel2)

# Visualizing the structure
print(big_event)
print(big_event.children)
print(smaller_event1.children)
print(segment1.children)