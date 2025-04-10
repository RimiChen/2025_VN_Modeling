import json
import networkx as nx
from networkx.readwrite import json_graph

# === Load the KG ===
def load_kg(path="Data/KGs_Book_0/integrated_kg.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # G = json_graph.node_link_graph(data, directed=True, multigraph=False, edges="edges")
    G = json_graph.node_link_graph(data, directed=True, multigraph=False)
    return G

# === Helper: Traverse successors via labeled edges
def get_successors_by_relation(G, node, relation, target_type=None):
    results = []
    for succ in G.successors(node):
        edge_data = G.get_edge_data(node, succ)
        if edge_data:
            if isinstance(edge_data, dict):
                # Multi-edge case (dict of dicts)
                if all(isinstance(v, dict) for v in edge_data.values()):
                    for d in edge_data.values():
                        if d.get("relation") == relation:
                            if not target_type or G.nodes[succ].get("type") == target_type:
                                results.append(succ)
                else:
                    # Single edge as dict
                    if edge_data.get("relation") == relation:
                        if not target_type or G.nodes[succ].get("type") == target_type:
                            results.append(succ)
    return results

# === Helper: Traverse predecessors via labeled edges
def get_predecessors_by_relation(G, node, relation, source_type=None):
    results = []
    for pred in G.predecessors(node):
        edge_data = G.get_edge_data(pred, node)
        if edge_data:
            if isinstance(edge_data, dict):
                if all(isinstance(v, dict) for v in edge_data.values()):
                    for d in edge_data.values():
                        if d.get("relation") == relation:
                            if not source_type or G.nodes[pred].get("type") == source_type:
                                results.append(pred)
                else:
                    if edge_data.get("relation") == relation:
                        if not source_type or G.nodes[pred].get("type") == source_type:
                            results.append(pred)
    return results


# === TASK 1: Action Retrieval by Macro-event
# def get_actions_by_macro_event(G, macro_event_id):
#     actions = set()
#     for event in get_predecessors_by_relation(G, macro_event_id, "subevent_of", "event"):
#         for segment in get_predecessors_by_relation(G, event, "subevent_of", "event_segment"):
#             for panel in get_predecessors_by_relation(G, segment, "instantiates", "panel"):
#                 pv = f"Panel_visual_{panel}"
#                 if pv in G:
#                     for act in get_successors_by_relation(G, pv, "has_action", "action"):
#                         actions.add(G.nodes[act].get("label"))
#     print(f"[DEBUG] Actions found for macro-event '{macro_event_id}': {actions}")
#     return sorted(actions)

def get_actions_by_macro_event(G, macro_event_id):
    """
    Traverse:
    macro_event ←subevent_of← event ←subevent_of← event_segment ←instantiates← panel
    panel → Panel_visual_<panel> →has_action→ action
    """
    actions = set()

    for event in get_predecessors_by_relation(G, macro_event_id, "subevent_of", "event"):
        for segment in get_predecessors_by_relation(G, event, "subevent_of", "event_segment"):
            for panel in get_predecessors_by_relation(G, segment, "instantiates", "panel"):
                panel_visual = f"Panel_visual_{panel}"
                if panel_visual in G:
                    for act in get_successors_by_relation(G, panel_visual, "has_action", "action"):
                        label = G.nodes[act].get("label")
                        if label:
                            actions.add(label)

    print(f"[DEBUG] Actions found for macro-event '{macro_event_id}': {actions}")
    return sorted(actions)


# === TASK 2: Dialogue Trace by Event
# def get_dialogues_by_event(G, event_id):
#     lines = set()
#     for segment in get_predecessors_by_relation(G, event_id, "subevent_of", "event_segment"):
#         for panel in get_predecessors_by_relation(G, segment, "instantiates", "panel"):
#             for pt in get_successors_by_relation(G, panel, "has_textual", "panel_textual"):
#                 for dlg in get_successors_by_relation(G, pt, "has_dialogue", "dialogue"):
#                     for t in get_successors_by_relation(G, dlg, "content_of", "text"):
#                         label = G.nodes[t].get("label")
#                         if label:
#                             lines.add(label)
#     print(f"[DEBUG] Dialogue lines for event '{event_id}': {lines}")
#     return sorted(lines)
def get_dialogues_by_event(G, event_id):
    """
    For each panel in the event, construct panel_textual_<panel_id>
    then find dialogue nodes that point to it via 'part_of',
    and collect text nodes linked via 'content_of'
    """
    lines = set()
    for segment in get_predecessors_by_relation(G, event_id, "subevent_of", "event_segment"):
        for panel in get_predecessors_by_relation(G, segment, "instantiates", "panel"):
            pt_node = f"Panel_textual_{panel}"
            if pt_node not in G:
                continue
            for node in G.nodes:
                if G.nodes[node].get("type") != "dialogue":
                    continue
                for src, tgt, data in G.out_edges(node, data=True):
                    if tgt == pt_node and data.get("relation") == "part_of":
                        for pred in G.predecessors(node):
                            if G.nodes[pred].get("type") == "text":
                                label = G.nodes[pred].get("label")
                                if label:
                                    lines.add(label)
    print(f"[DEBUG] Dialogue lines for event '{event_id}': {lines}")
    return sorted(lines)


# === TASK 3: Character Appearance Mapping
# def get_character_appearances(G):
#     appearances = {}
#     for node in G.nodes:
#         if G.nodes[node].get("type") != "character":
#             continue
#         char_label = G.nodes[node].get("label", node)
#         for pv, _, d in G.in_edges(node, data=True):
#             if d.get("relation") == "has_character" and G.nodes[pv].get("type") == "panel_visual":
#                 for panel in G.predecessors(pv):
#                     if G.nodes[panel].get("type") == "panel":
#                         appearances.setdefault(char_label, []).append(panel)
#     print(f"[DEBUG] Character appearances: {appearances}")
#     return appearances
def get_character_appearances(G):
    """
    Traverse edges: Panel_visual_X --has_character--> Character
    Derive the panel ID from the Panel_visual node name.
    """
    appearances = {}

    for u, v, d in G.edges(data=True):
        if d.get("relation") != "has_character":
            continue
        if G.nodes[u].get("type") != "panel_visual":
            continue
        if G.nodes[v].get("type") != "character":
            continue

        # Derive panel ID from panel_visual ID
        if u.startswith("Panel_visual_"):
            panel_id = u.replace("Panel_visual_", "")
        else:
            continue

        # Get character label
        label = G.nodes[v].get("label", v).strip()
        appearances.setdefault(label, []).append(panel_id)

    print(f"[DEBUG] Character appearances: {appearances}")
    return appearances

# === TASK 4: Panel Timeline by Macro-event
def get_panels_by_macro_event(G, macro_event_id):
    panels = []
    for event in get_predecessors_by_relation(G, macro_event_id, "subevent_of", "event"):
        for segment in get_predecessors_by_relation(G, event, "subevent_of", "event_segment"):
            for panel in get_predecessors_by_relation(G, segment, "instantiates", "panel"):
                panels.append(panel)
    print(f"[DEBUG] Panels for macro-event '{macro_event_id}': {panels}")
    return sorted(panels)

# === MAIN TESTING ===
if __name__ == "__main__":
    G = load_kg()

    print("\n=== ACTIONS for macro-event 'Think of family' ===")
    print(get_actions_by_macro_event(G, "Think of family"))

    print("\n=== DIALOGUES for event 'Intro_1' ===")
    print(get_dialogues_by_event(G, "Intro_1"))

    print("\n=== CHARACTER APPEARANCES ===")
    char_map = get_character_appearances(G)
    for char, panels in char_map.items():
        print(f"{char}: {sorted(panels)}")

    print("\n=== PANELS for macro-event 'Think of family' ===")
    print(get_panels_by_macro_event(G, "Think of family"))
