import pandas as pd
import numpy as np
import glob
import os

# input and output folders
input_folder = "NEUR490_TXT"
output_folder = "NEUR490_RA_CSV"
os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

# find all TXT files in the input folder
txt_files = sorted(glob.glob(os.path.join(input_folder, "*.txt")))

print(f"Found {len(txt_files)} files.")

# loop through each file
for file_path in txt_files:

    # load the file
    names = ['Tier', 'participant', 'start_ms', 'end_ms', 'duration_ms', 'label']
    codes = pd.read_csv(file_path, sep=r'\s+', header=None, names=names)

    # tier 'R'
    subset = (
        codes.loc[codes['Tier'] == 'RA', ['start_ms', 'end_ms', 'label']]
        .dropna()
        .reset_index(drop=True)
    )

    if subset.empty or subset['end_ms'].isna().all():
        print(f"Skipping {os.path.basename(file_path)} — no valid 'RA' tier or missing end_ms.")
        continue

    # sample grid
    interval = 100  # ms
    end_time = int(np.ceil(subset['end_ms'].max() / interval) * interval)
    t = np.arange(0, end_time + interval, interval, dtype=int)
    centers = t[:-1] + interval // 2

    # series
    series = np.zeros(len(centers), dtype=int)
    for _, row in subset.iterrows():
        mask = (centers >= row.start_ms) & (centers < row.end_ms)
        label = str(row.label).strip().upper()
        series[mask] = 1 if (label == 'MDG' or label == 'MDT') else 0

    # df
    binary_df = pd.DataFrame({
        'time_ms': t[:-1],
        'center_ms': centers,
        'binary_value': series
    })

    # save to CSV
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_RA_binary.csv")
    binary_df.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")

print("All files processed successfully.")
