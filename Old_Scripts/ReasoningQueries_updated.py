# === Load Integrated Knowledge Graph ===
# def load_kg(kg_path="Data/Annotation_Book_0/integrated_kg.json"):
# def load_kg(kg_path="Data/KGs_Book_0/integrated_kg.json"):
import json
import networkx as nx
from networkx.readwrite import json_graph

# === Load the integrated knowledge graph ===
def load_kg(path="Data/KGs_Book_0/integrated_kg.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    G = json_graph.node_link_graph(data)  # No extra attrs to avoid compatibility issues
    return G

# === 1. Action Retrieval by Macro-event ===
def get_actions_by_macro_event(G, macro_event_id):
    """Retrieve all actions that occur under a given macro-event."""
    actions = set()
    for u, v, d in G.edges(data=True):
        if d.get("relation") == "subevent_of" and v == macro_event_id:
            event = u
            for uu, vv, dd in G.edges(data=True):
                if dd.get("relation") == "subevent_of" and vv == event:
                    segment = uu
                    for p, s, rel in G.edges(data=True):
                        if rel.get("relation") == "instantiates" and s == segment:
                            panel = p
                            for a in G.successors(panel):
                                if G.nodes[a].get("type") == "action":
                                    actions.add(G.nodes[a].get("label"))
    return sorted(actions)

# === 2. Dialogue Trace by Event ===
def get_dialogues_by_event(G, event_id):
    """Retrieve all dialogue lines under a specific mid-level event."""
    lines = set()
    for u, v, d in G.edges(data=True):
        if d.get("relation") == "subevent_of" and v == event_id:
            segment = u
            for p, s, rel in G.edges(data=True):
                if rel.get("relation") == "instantiates" and s == segment:
                    panel = p
                    for d_node in G.successors(panel):
                        if G.nodes[d_node].get("type") == "dialogue":
                            for t in G.successors(d_node):
                                if G.nodes[t].get("type") == "text":
                                    lines.add(G.nodes[t]["label"])
    return sorted(lines)

# === 3. Character Appearance Mapping ===
def get_character_appearances(G):
    """Return a mapping of character names to the panels they appear in."""
    appearances = {}
    for node in G.nodes:
        if G.nodes[node].get("type") == "character":
            label = G.nodes[node].get("label", node)
            panels = []
            for u, v, d in G.edges(data=True):
                if u == node and G.nodes[v].get("type") == "panel":
                    panels.append(v)
            if panels:
                appearances[label] = sorted(panels)
    return appearances

# === 4. Panel Timeline by Macro-event ===
def get_panels_by_macro_event(G, macro_event_id):
    """Retrieve the panel IDs that belong to a macro-event, preserving reading order."""
    panels = []
    for u, v, d in G.edges(data=True):
        if d.get("relation") == "subevent_of" and v == macro_event_id:
            event = u
            for uu, vv, dd in G.edges(data=True):
                if dd.get("relation") == "subevent_of" and vv == event:
                    segment = uu
                    for p, s, rel in G.edges(data=True):
                        if rel.get("relation") == "instantiates" and s == segment:
                            panels.append(p)
    return sorted(panels)

# === Sample test run ===
if __name__ == "__main__":
    G = load_kg()

    print("=== ACTIONS for macro-event 'Think of family' ===")
    print(get_actions_by_macro_event(G, "Think of family"))

    print("\n=== DIALOGUES for event 'Intro_1' ===")
    print(get_dialogues_by_event(G, "Intro_1"))

    print("\n=== CHARACTER APPEARANCES ===")
    char_map = get_character_appearances(G)
    for char, panels in char_map.items():
        print(f"{char}: {panels}")

    print("\n=== PANELS for macro-event 'Think of family' ===")
    print(get_panels_by_macro_event(G, "Think of family"))

###================ Debuging
    # print("\n=== DEBUG: Nodes connected to panel '0_0_0' ===")
    # for succ in G.successors("0_0_0"):
    #     print(f"  {succ} — {G.nodes[succ].get('type')} — label: {G.nodes[succ].get('label')}")
    # print("\n=== DEBUG: Actions in graph ===")
    # for node in G.nodes:
    #     if "action" in G.nodes[node].get("type", "").lower():
    #         print(f"{node}: {G.nodes[node]}")
    # print("\n=== DEBUG: Dialogue → Text chain ===")
    # for node in G.nodes:
    #     if G.nodes[node].get("type") == "dialogue":
    #         print(f"\nDialogue node: {node}")
    #         for t in G.successors(node):
    #             print(f"  Text node: {t}, content: {G.nodes[t].get('label')}")
    