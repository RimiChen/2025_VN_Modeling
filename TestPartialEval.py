# Sample inputs
gt_list = ['ask_question', 'clean', 'fall_to', 'hold', 'look', 'look_at', 'spit_on', 'stomp_on', 'talk', 'tear', 'walk_on']
pred_string = 'ask_question | clean | fall_to | give | hold | look | look_at | spit_on | stomp_on | talk | tear | walk_on'
pred_list = [item.strip() for item in pred_string.split('|')]

# Convert to sets
gt_set = set(gt_list)
pred_set = set(pred_list)

# Calculate intersection, precision, recall, F1
intersection = gt_set & pred_set
precision = len(intersection) / len(pred_set) if pred_set else 0
recall = len(intersection) / len(gt_set) if gt_set else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
jaccard = len(intersection) / len(gt_set | pred_set) if (gt_set | pred_set) else 0

# Output
print("=== Word-level Similarity Metrics ===")
print("Ground Truth:", gt_list)
print("Prediction  :", pred_list)
print("Matched     :", sorted(list(intersection)))
print("Precision   :", round(precision, 2))
print("Recall      :", round(recall, 2))
print("F1 Score    :", round(f1, 2))
print("Jaccard Sim :", round(jaccard, 2))
