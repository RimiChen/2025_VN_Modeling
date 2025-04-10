import networkx as nx

def build_panel_kg(panel_data, panel_index=0):
    G = nx.DiGraph()
    
    # Panel-level nodes
    panel_visual = f"Panel_visual_{panel_index}"
    panel_textual = f"Panel_textual_{panel_index}"
    G.add_node(panel_visual, type="panel_visual")
    G.add_node(panel_textual, type="panel_textual")
    
    # Encoder nodes
    for i, enc in enumerate(panel_data.get("visual", {}).get("encoders", [])):
        if enc:
            enc_node = f"encoder_{panel_index}_{i}"
            G.add_node(enc_node, type="encoder")
            G.add_edge(enc_node, panel_visual, relation="encodes")
    
    # Scene objects and Scene grouping
    scene_objs = panel_data.get("scene", [])
    scene_group = f"Scene_{panel_index}"
    G.add_node(scene_group, type="scene")
    G.add_edge(scene_group, panel_visual, relation="appears_in")
    for i, obj in enumerate(scene_objs):
        if obj:
            obj_node = f"scene_obj_{i}({obj})"
            G.add_node(obj_node, type="scene_obj")
            G.add_edge(obj_node, scene_group, relation="part_of_scene")
    
    # Characters and actions
    characters = panel_data.get("characters", [])
    for char in characters:
        if char:
            G.add_node(char, type="character")
            G.add_edge(char, "Characters", relation="is_a")
            G.add_edge(char, scene_group, relation="located_in")
            visual_node = f"Visual_{char}"
            G.add_node(visual_node, type="character_visual")
            G.add_edge(visual_node, char, relation="visual_of")

    for a_idx, action in enumerate(panel_data.get("actions", [])):
        parts = action.split()
        if len(parts) >= 3:
            subject, predicate, obj = parts[0], parts[1], " ".join(parts[2:])
            action_node = f"Action_{panel_index}_{a_idx}({predicate})"
            G.add_node(action_node, type="action")
            G.add_edge(subject, action_node, relation="performs")
            G.add_edge(action_node, obj, relation="targets")
    
    # Text: Dialogues and Captions
    for j, dialogue in enumerate(panel_data.get("textual", {}).get("dialogues", [])):
        d_node = f"Dialogue_{panel_index}_{j}"
        G.add_node(d_node, type="dialogue")
        G.add_edge(d_node, panel_textual, relation="part_of")
        G.add_node(dialogue, type="text")
        G.add_edge(dialogue, d_node, relation="content_of")
    
    if panel_data.get("caption"):
        c_node = f"Caption_{panel_index}_0"
        G.add_node(c_node, type="caption")
        G.add_edge(c_node, panel_textual, relation="part_of")
        G.add_node(panel_data["caption"], type="text")
        G.add_edge(panel_data["caption"], c_node, relation="content_of")
    
    return G
