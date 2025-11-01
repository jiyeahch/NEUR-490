import pandas as pd
from pathlib import Path
import re

# file paths
r_folder = Path("NEUR490_R_CSV")
merged_folder = Path("NEUR490_MERGED_CSV")
out_folder = Path("NEUR490_FINAL_MERGED")
out_folder.mkdir(exist_ok=True)

def and_merge(r_csv: Path, merged_csv: Path, out_csv: Path):
    r = pd.read_csv(r_csv)
    merged = pd.read_csv(merged_csv)

    # keep only matching rows
    combined = pd.merge(
        r[["time_ms", "center_ms", "binary_value"]],
        merged[["tier", "time_ms", "center_ms", "binary_value"]],
        on=["time_ms", "center_ms"],
        how="inner",
        suffixes=("_R", "_MERGED")
    )

    # apply AND logic: 1 only if both are 1
    combined["binary_value"] = ((combined["binary_value_R"] == 1) & (combined["binary_value_MERGED"] == 1)).astype(int)

    # keep only tier, time, center, and the new value
    trimmed = combined[["time_ms", "center_ms", "binary_value"]]

    trimmed.to_csv(out_csv, index=False)
    print(f"✅ Saved: {out_csv.name} ({len(trimmed)} rows)")

# across all files
def batch_and_merge(r_folder: Path, merged_folder: Path, out_folder: Path):
    # find all files
    r_files = list(r_folder.glob("*.csv"))
    merged_files = list(merged_folder.glob("*_MERGED.csv"))

    # make a dictionary of subject → R file
    r_map = {}
    for f in r_files:
        stem = f.stem  # e.g., TD13-M3_A2R1_CC_RE_binary
        subject = stem[:-len("_RE_binary")] if stem.endswith("_RE_binary") else stem
        r_map[subject] = f

    # Loop merged files
    for merged_path in merged_files:
        stem = merged_path.stem  # e.g., TD13-M3_A2R1_CC_RE_MERGED
        subject = stem[:-len("_RE_MERGED")] if stem.endswith("_RE_MERGED") else stem

        if subject in r_map:
            r_path = r_map[subject]
            out_path = out_folder / f"{subject}_FINAL_MERGED.csv"
            and_merge(r_path, merged_path, out_path)
        else:
            print(f"skipped {subject}: no matching R file found.")

    print(f"\n✅ Done. Saved all results to {out_folder}")

if __name__ == "__main__":
    batch_and_merge(r_folder, merged_folder, out_folder)
