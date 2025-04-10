import pandas as pd

# Load original file
input_path = "Data/Annotation_Book_0/Story_0.xlsx"
output_path = "Data/Annotation_Book_0/Story_0_with_IDs.xlsx"

df = pd.read_excel(input_path)
df = df.dropna(subset=["Index"]).reset_index(drop=True)

# Forward fill macro-level event
df["Plot_0"] = df["Plot_0"].fillna(method="ffill")
df["Plot_1"] = df["Plot_1"].fillna(method="ffill")
df["Plot_2"] = df["Plot_2"].fillna(method="ffill")

# === Assign unique IDs for Plot_1 (sub-events) ===
plot1_ids = []
prev = None
counter = {}
for i, row in df.iterrows():
    curr = row["Plot_1"]
    if curr != prev:
        counter[curr] = counter.get(curr, 0) + 1
    plot1_ids.append(f"{curr}_{counter[curr]}")
    prev = curr
df["Plot_1_ID"] = plot1_ids

# === Assign unique IDs for Plot_2 (event segments) ===
plot2_ids = []
prev = None
counter2 = {}
for i, row in df.iterrows():
    curr = row["Plot_2"]
    if curr != prev:
        counter2[curr] = counter2.get(curr, 0) + 1
    plot2_ids.append(f"seg{len(counter2):03d}")
    prev = curr
df["Plot_2_ID"] = plot2_ids

# Save to new Excel file
df.to_excel(output_path, index=False)
print(f"✅ Updated Excel saved to {output_path}")
