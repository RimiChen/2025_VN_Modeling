import pandas as pd

# Load CSVs
df_gt = pd.read_csv("Data/KGs_Book_0/ground_truth_task4_panels.csv")
df_pred = pd.read_csv("Data/KGs_Book_0/reasoning_task4_panels.csv")

# Normalize columns
df_gt.columns = [c.strip().lower() for c in df_gt.columns]
df_pred.columns = [c.strip().lower() for c in df_pred.columns]

df_gt.rename(columns={"macro_event": "id"}, inplace=True)
df_pred.rename(columns={"macro_event": "id"}, inplace=True)

# Detect panel columns
gt_col = [c for c in df_gt.columns if "panel" in c][0]
pred_col = [c for c in df_pred.columns if "panel" in c][0]

# Merge
df = pd.merge(df_gt[["id", gt_col]], df_pred[["id", pred_col]], on="id", how="inner")

results = []

def parse_panels(s):
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

# Evaluate each row
for _, row in df.iterrows():
    try:
        gt_panels = parse_panels(row[gt_col])
        pred_panels = parse_panels(row[pred_col])
        if not gt_panels and not pred_panels:
            continue
    except Exception as e:
        print(f"[WARN] Could not parse row {row['id']}: {e}")
        continue

    precision, recall, f1, match, missing, extra = evaluate(gt_panels, pred_panels)

    results.append({
        "ID": row["id"],
        "GT": gt_panels,
        "PRED": pred_panels,
        "Matched": match,
        "Missing": missing,
        "Extra": extra,
        "Precision": round(precision, 2),
        "Recall": round(recall, 2),
        "F1": round(f1, 2),
        "Task": "Task 4: Panel Timeline"
    })

# Output
if results:
    df_results = pd.DataFrame(results)
    df_results.to_csv("Data/KGs_Book_0/task4_partial_match_detailed.csv", index=False)
    print("\n=== Task 4 Partial Match Summary ===")
    print("Average Precision:", round(df_results["Precision"].mean(), 2))
    print("Average Recall   :", round(df_results["Recall"].mean(), 2))
    print("Average F1       :", round(df_results["F1"].mean(), 2))
    print("Saved to task4_partial_match_detailed.csv")
else:
    print("\n[ERROR] No valid rows parsed — check panel formatting in the CSV.")
