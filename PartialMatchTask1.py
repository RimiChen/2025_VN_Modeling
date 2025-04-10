import pandas as pd

# Load CSVs
df_gt = pd.read_csv("Data/KGs_Book_0/ground_truth_task1_actions.csv")
df_pred = pd.read_csv("Data/KGs_Book_0/reasoning_task1_actions.csv")

# Normalize column names
df_gt.columns = [c.strip().lower() for c in df_gt.columns]
df_pred.columns = [c.strip().lower() for c in df_pred.columns]

df_gt.rename(columns={"macro_event": "id"}, inplace=True)
df_pred.rename(columns={"macro_event": "id"}, inplace=True)

# Merge on event ID
df = pd.merge(df_gt, df_pred, on="id", how="inner")

results = []

def parse_action_string(s):
    if pd.isna(s):
        return []
    s = s.strip()
    s = s.strip("[]").replace("'", "").replace('"', '')
    return [a.strip() for a in s.replace("|", ";").split(";") if a.strip()]

def evaluate_match(gt_list, pred_list):
    gt_set = set(gt_list)
    pred_set = set(pred_list)
    intersection = gt_set & pred_set
    precision = len(intersection) / len(pred_set) if pred_set else 0
    recall = len(intersection) / len(gt_set) if gt_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1, list(intersection), list(gt_set - intersection), list(pred_set - intersection)

for _, row in df.iterrows():
    try:
        gt_list = parse_action_string(row["actions"])
        pred_list = parse_action_string(row["predicted_actions"])
        if not gt_list and not pred_list:
            continue
    except Exception as e:
        print(f"[WARN] Could not parse row {row['id']}: {e}")
        continue

    precision, recall, f1, match, missing, extra = evaluate_match(gt_list, pred_list)

    results.append({
        "ID": row["id"],
        "GT": gt_list,
        "PRED": pred_list,
        "Matched": match,
        "Missing": missing,
        "Extra": extra,
        "Precision": round(precision, 2),
        "Recall": round(recall, 2),
        "F1": round(f1, 2),
        "Task": "Task 1: Action Retrieval"
    })

# Output
if results:
    df_results = pd.DataFrame(results)
    df_results.to_csv("Data/KGs_Book_0/task1_partial_match_detailed.csv", index=False)
    print("\n=== Task 1 Partial Match Summary ===")
    print("Average Precision:", round(df_results["Precision"].mean(), 2))
    print("Average Recall   :", round(df_results["Recall"].mean(), 2))
    print("Average F1       :", round(df_results["F1"].mean(), 2))
    print("Saved to task1_partial_match_detailed.csv")
else:
    print("\n[ERROR] No valid rows parsed — please check input formatting.")
