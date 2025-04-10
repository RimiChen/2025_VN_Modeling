import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from pathlib import Path

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

# === Evaluation helpers ===
def safe_div(a, b):
    return a / b if b != 0 else 0

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

    precision_list, recall_list, f1_list = [], [], []

    for item_id, gt_str in gt_dict.items():
        gt_items = set(s.strip() for s in gt_str.split("|") if s.strip())
        pred_items = set(s.strip() for s in pred_dict.get(item_id, "").split("|") if s.strip())

        tp = len(gt_items & pred_items)
        fp = len(pred_items - gt_items)
        fn = len(gt_items - pred_items)

        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall) if (precision + recall) else 0

        precision_list.append(precision)
        recall_list.append(recall)
        f1_list.append(f1)

        if f1 < 1.0:
            failures[task_name].append({
                "ID": item_id,
                "GT": sorted(gt_items),
                "PRED": sorted(pred_items),
                "Missing": sorted(gt_items - pred_items),
                "Extra": sorted(pred_items - gt_items),
                "Precision": round(precision, 2),
                "Recall": round(recall, 2),
                "F1": round(f1, 2)
            })

    summary_rows.append({
        "Task": task_name,
        "F1": round(sum(f1_list) / len(f1_list), 4),
        "Precision": round(sum(precision_list) / len(precision_list), 4),
        "Recall": round(sum(recall_list) / len(recall_list), 4)
    })

# === Save summary and failure tables ===
Path("./output").mkdir(parents=True, exist_ok=True)
df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv("Data/KGs_Book_0/reasoning_evaluation_summary_full.csv", index=False)

df_fails = pd.concat(
    [pd.DataFrame(rows).assign(Task=task) for task, rows in failures.items()],
    ignore_index=True
)
df_fails.to_csv("Data/KGs_Book_0/reasoning_evaluation_failures_full.csv", index=False)

print("✅ Evaluation complete.")
print("📄 Summary: Data/KGs_Book_0/reasoning_evaluation_summary_full.csv")
print("📄 Failures: Data/KGs_Book_0/reasoning_evaluation_failures_full.csv")

# === Plotting (Matplotlib bar chart) ===
plt.figure(figsize=(10, 5))
x = df_summary["Task"]
plt.bar(x, df_summary["F1"], label="F1", color="skyblue")
plt.bar(x, df_summary["Precision"], label="Precision", alpha=0.7, color="orange")
plt.bar(x, df_summary["Recall"], label="Recall", alpha=0.7, color="green")
plt.ylabel("Score")
plt.ylim(0, 1.05)
plt.xticks(rotation=15, ha='right')
plt.title("Reasoning Task Evaluation Metrics")
plt.legend()
plt.tight_layout()
plt.savefig("Data/KGs_Book_0/reasoning_metrics_plot.png", dpi=300)
plt.show()
