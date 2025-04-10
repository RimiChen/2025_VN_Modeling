import json
import networkx as nx
from networkx.readwrite import json_graph

# Load the integrated knowledge graph
with open('Data/KGs_Book_0/integrated_kg.json', 'r', encoding='utf-8') as f:
    G = json_graph.node_link_graph(json.load(f))

# === Reasoning Functions from previous reasoning_queries ===
def get_panels_in_event_segment(G, segment_id):
    return [u for u, v, d in G.edges(data=True) if v == segment_id and d["relation"] == "instantiates"]

def get_event_segments_in_event(G, event_id):
    return [u for u, v, d in G.edges(data=True) if v == event_id and d["relation"] == "subevent_of"]

def get_events_in_macro_event(G, macro_id):
    return [u for u, v, d in G.edges(data=True) if v == macro_id and d["relation"] == "subevent_of"]

def get_all_actions_in_macro_event(G, macro_id):
    actions = []
    for event in get_events_in_macro_event(G, macro_id):
        for seg in get_event_segments_in_event(G, event):
            for panel in get_panels_in_event_segment(G, seg):
                actions += [n for n in G.successors(panel) if G.nodes[n].get("type") == "action"]
    return actions

def get_dialogues_in_event(G, event_id):
    dialogues = []
    for seg in get_event_segments_in_event(G, event_id):
        for panel in get_panels_in_event_segment(G, seg):
            for d in G.successors(panel):
                if G.nodes[d].get("type") == "dialogue":
                    for t in G.successors(d):
                        if G.nodes[t].get("type") == "text":
                            dialogues.append(G.nodes[t].get("label"))
    return dialogues

def get_ordered_panels_by_macro(G, macro_id):
    panels = []
    for event in get_events_in_macro_event(G, macro_id):
        for seg in get_event_segments_in_event(G, event):
            panels += get_panels_in_event_segment(G, seg)
    return panels

# === Evaluation Metrics ===
def evaluate_action_retrieval(G, macro_id, ground_truth_actions):
    retrieved = get_all_actions_in_macro_event(G, macro_id)
    retrieved_labels = [G.nodes[a].get("label") for a in retrieved]
    correct = [a for a in retrieved_labels if a in ground_truth_actions]
    coverage = len(correct) / len(ground_truth_actions) if ground_truth_actions else 0.0
    return coverage, correct, retrieved_labels

def evaluate_dialogue_recall(G, event_id, ground_truth_dialogues):
    retrieved = get_dialogues_in_event(G, event_id)
    correct = [line for line in retrieved if line in ground_truth_dialogues]
    recall = len(correct) / len(ground_truth_dialogues) if ground_truth_dialogues else 0.0
    return recall, correct, retrieved

def evaluate_ordering_accuracy(predicted_order, gold_order):
    match = sum(p == g for p, g in zip(predicted_order, gold_order))
    return match / len(gold_order) if gold_order else 0.0

# === Example Evaluation ===
macro_event = "Think of family"
event = "Intro_1"

ground_truth_actions = ["hold_hand", "look_at_letter", "cook_rice", "walk_away"]
ground_truth_dialogues = [
    "Before I knew it, it was May, the season when young leaves are the most beautiful.",
    "I had just started living on my own."
]
gold_panel_order = ["0_0_0", "0_0_1", "0_0_2", "0_0_3", "0_0_4", "0_0_5", "0_1_0"]

print("🧪 Evaluating action retrieval:")
score, correct, predicted = evaluate_action_retrieval(G, macro_event, ground_truth_actions)
print(f"  Coverage: {score:.2f}")
print("  Correct:", correct)
print("  Retrieved:", predicted)

print("\n🧪 Evaluating dialogue recall:")
recall, correct_lines, predicted_lines = evaluate_dialogue_recall(G, event, ground_truth_dialogues)
print(f"  Recall: {recall:.2f}")
print("  Correct:", correct_lines)
print("  Retrieved:", predicted_lines)

print("\n🧪 Evaluating panel ordering:")
predicted_order = get_ordered_panels_by_macro(G, macro_event)
ordering_acc = evaluate_ordering_accuracy(predicted_order[:len(gold_panel_order)], gold_panel_order)
print(f"  Ordering Accuracy: {ordering_acc:.2f}")
print("  Predicted Order:", predicted_order[:len(gold_panel_order)])
