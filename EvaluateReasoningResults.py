import pandas as pd
from collections import defaultdict
from pathlib import Path
import csv

# === File Paths ===
TASK_FILES = {
    "Task 1: Action Retrieval": {
        "gt": "Data/KGs_Book_0/ground_truth_task1_actions.csv",
        "pred": "Data/KGs_Book_0/reasoning_task1_actions.csv",
        "id_col": "Macro_event",
        "label": "Actions"
    },
    "Task 2: Dialogue Trace": {
        "gt": "Data/KGs_Book_0/ground_truth_task2_dialogues.csv",
        "pred": "Data/KGs_Book_0/reasoning_task2_dialogues.csv",
        "id_col": "Event",
        "label": "Dialogues"
    },
    "Task 3: Character Appearance": {
        "gt": "Data/KGs_Book_0/ground_truth_task3_characters.csv",
        "pred": "Data/KGs_Book_0/reasoning_task3_characters.csv",
        "id_col": "Event",
        "label": "Characters"
    },
    "Task 4: Panel Timeline": {
        "gt": "Data/KGs_Book_0/ground_truth_task4_panels.csv",
        "pred": "Data/KGs_Book_0/reasoning_task4_panels.csv",
        "id_col": "Macro_event",
        "label": "Panels"
    }
}

# === Evaluation helper ===
def evaluate_list_match(gt_list, pred_list):
    gt_set = set(gt_list)
    pred_set = set(pred_list)
    if not gt_set:
        return 1.0 if not pred_set else 0.0
    return len(gt_set & pred_set) / len(gt_set)

# === Evaluation Process ===
summary_rows = []
failures = defaultdict(list)

for task_name, files in TASK_FILES.items():
    df_gt = pd.read_csv(files["gt"])
    df_pred = pd.read_csv(files["pred"])
    id_col = files["id_col"]
    label_col = files["label"]
    pred_col = f"Predicted_{label_col}"

    gt_dict = dict(zip(df_gt[id_col], df_gt[label_col].fillna("").astype(str)))
    pred_dict = dict(zip(df_pred[id_col], df_pred[pred_col].fillna("").astype(str)))

    scores = []

    for item_id, gt_str in gt_dict.items():
        gt_items = [s.strip() for s in gt_str.split("|") if s.strip()]
        pred_items = [s.strip() for s in pred_dict.get(item_id, "").split("|") if s.strip()]
        score = evaluate_list_match(gt_items, pred_items)
        scores.append(score)

        if score < 1.0:
            failures[task_name].append({
                "ID": item_id,
                "GT": gt_items,
                "PRED": pred_items,
                "Recall": round(score, 2)
            })

    metric = "Coverage" if "Action" in task_name or "Character" in task_name else "Recall" if "Dialogue" in task_name else "Ordering Accuracy"
    summary_rows.append({
        "Task": task_name,
        "Metric": metric,
        "Avg_Score": round(sum(scores) / len(scores), 4)
    })

# === Save Summary CSV ===
Path("Data/KGs_Book_0/").mkdir(parents=True, exist_ok=True)
summary_path = "Data/KGs_Book_0/reasoning_evaluation_summary.csv"
pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

# === Save Detailed Failures CSV ===
failures_path = "Data/KGs_Book_0/reasoning_evaluation_failures.csv"
df_fails = pd.concat(
    [pd.DataFrame(rows).assign(Task=task) for task, rows in failures.items()],
    ignore_index=True
)
df_fails.to_csv(failures_path, index=False)

print("✅ Evaluation complete.")
print(f"Summary saved to: {summary_path}")
print(f"Failure cases saved to: {failures_path}")
