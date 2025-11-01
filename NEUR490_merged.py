import pandas as pd
import os
import re
import glob

# input and output folders
ra_folder = "NEUR490_RA_CSV"
la_folder = "NEUR490_LA_CSV"
out_folder = "NEUR490_MERGED_CSV"
os.makedirs(out_folder, exist_ok=True)

def merge_ra_la(ra_csv, la_csv, out_csv):
    ra = pd.read_csv(ra_csv)
    la = pd.read_csv(la_csv)

    # rename for clarity
    ra = ra.rename(columns={"binary_value": "binary_value_RA"})
    la = la.rename(columns={"binary_value": "binary_value_LA"})

    # merge on time and center columns
    merged = pd.merge(
        ra[["time_ms", "center_ms", "binary_value_RA"]],
        la[["time_ms", "center_ms", "binary_value_LA"]],
        on=["time_ms", "center_ms"],
        how="outer").sort_values(["time_ms", "center_ms"], kind="mergesort")

    # handle NaNs and convert to int
    merged["binary_value_RA"] = merged["binary_value_RA"].fillna(0).astype(int)
    merged["binary_value_LA"] = merged["binary_value_LA"].fillna(0).astype(int)

    # merge rule: 1 overrides 0
    merged["binary_value"] = 0
    merged.loc[merged["binary_value_RA"] == 1, "binary_value"] = 1
    merged.loc[merged["binary_value_LA"] == 1, "binary_value"] = 1

    # tier column: identify which side took over
    merged["tier"] = "None"
    merged.loc[(merged["binary_value_RA"] == 1) & (merged["binary_value_LA"] == 0), "tier"] = "RA"
    merged.loc[(merged["binary_value_RA"] == 0) & (merged["binary_value_LA"] == 1), "tier"] = "LA"
    merged.loc[(merged["binary_value_RA"] == 1) & (merged["binary_value_LA"] == 1), "tier"] = "Both"

    # save in requested format
    out = merged[["tier", "time_ms", "center_ms", "binary_value"]]
    out.to_csv(out_csv, index=False)
    print(f"Saved merged file: {out_csv} ({len(out)} rows)")

def batch_merge(ra_folder, la_folder, out_folder):
    ra_files = glob.glob(os.path.join(ra_folder, "*.csv"))
    la_files = glob.glob(os.path.join(la_folder, "*.csv"))

    subject_map = {}

    for f in ra_files:
        base = os.path.basename(f)
        key = re.sub(r"_RA_binary\.csv$", "", base, flags=re.IGNORECASE)
        subject_map.setdefault(key, {})["RA"] = f

    for f in la_files:
        base = os.path.basename(f)
        key = re.sub(r"_LA_binary\.csv$", "", base, flags=re.IGNORECASE)
        subject_map.setdefault(key, {})["LA"] = f

    # merge all pairs
    for subject, paths in subject_map.items():
        if "RA" in paths and "LA" in paths:
            out_csv = os.path.join(out_folder, f"{subject}_MERGED.csv")
            merge_ra_la(paths["RA"], paths["LA"], out_csv)
        else:
            print(f"skipped {subject}: missing RA or LA file.")


batch_merge(ra_folder, la_folder, out_folder)
