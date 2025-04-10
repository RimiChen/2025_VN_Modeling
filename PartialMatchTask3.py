import pandas as pd

# Load CSVs
df_gt = pd.read_csv("Data/KGs_Book_0/ground_truth_task3_characters.csv")
df_pred = pd.read_csv("Data/KGs_Book_0/reasoning_task3_characters.csv")

# Normalize column names
df_gt.columns = [c.strip().lower() for c in df_gt.columns]
df_pred.columns = [c.strip().lower() for c in df_pred.columns]

df_gt.rename(columns={"event": "id"}, inplace=True)
df_pred.rename(columns={"event": "id"}, inplace=True)

# Detect character list columns
gt_col = [c for c in df_gt.columns if "character" in c][0]
pred_col = [c for c in df_pred.columns if "character" in c][0]

# Merge
df = pd.merge(df_gt[["id", gt_col]], df_pred[["id", pred_col]], on="id", how="inner")

results = []

def parse_characters(s):
    if pd.isna(s):
        return []
    s = s.strip("[]").replace("'", "").replace('"', '')
    return [x.strip() for x in s.replace("|", ";").split(";") if x.strip()]

def evaluate(gt_list, pred_list):
    gt_set = set(gt_list)
    pred_set = set(pred_list)
    matched = gt_set & pred_set
    precision = len(matched) / len(pred_set) if pred_set else 0
    recall = len(matched) / len(gt_set) if gt_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1, list(matched), list(gt_set - matched), list(pred_set - matched)

# Per-row evaluation
for _, row in df.iterrows():
    try:
        gt_chars = parse_characters(row[gt_col])
        pred_chars = parse_characters(row[pred_col])
        if not gt_chars and not pred_chars:
            continue
    except Exception as e:
        print(f"[WARN] Could not parse row {row['id']}: {e}")
        continue

    precision, recall, f1, match, missing, extra = evaluate(gt_chars, pred_chars)

    results.append({
        "ID": row["id"],
        "GT": gt_chars,
        "PRED": pred_chars,
        "Matched": match,
        "Missing": missing,
        "Extra": extra,
        "Precision": round(precision, 2),
        "Recall": round(recall, 2),
        "F1": round(f1, 2),
        "Task": "Task 3: Character Appearance"
    })

# Output
if results:
    df_results = pd.DataFrame(results)
    df_results.to_csv("Data/KGs_Book_0/task3_partial_match_detailed.csv", index=False)
    print("\n=== Task 3 Partial Match Summary ===")
    print("Average Precision:", round(df_results["Precision"].mean(), 2))
    print("Average Recall   :", round(df_results["Recall"].mean(), 2))
    print("Average F1       :", round(df_results["F1"].mean(), 2))
    print("Saved to task3_partial_match_detailed.csv")
else:
    print("\n[ERROR] No valid rows parsed — check data format.")
