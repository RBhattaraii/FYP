import os
import pandas as pd

data_dir = r"C:\Users\NITOR 5\Desktop\FYP\Data"
platforms = []
total_products = 0

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith(".csv"):
            platform_name = os.path.basename(root)
            path = os.path.join(root, file)
            try:
                df = pd.read_csv(path)
                count = len(df)
                total_products += count
                platforms.append({"platform": platform_name, "file": file, "count": count})
            except Exception as e:
                print(f"Error reading {file}: {e}")

print(f"Total Platforms: {len(platforms)}")
for p in platforms:
    print(f"- {p['platform']} ({p['file']}): {p['count']} rows")
print(f"Total Products across all CSVs: {total_products}")
