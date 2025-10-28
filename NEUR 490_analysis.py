import pandas as pd
import numpy as np
# [JO] It's good that you are using `glob` and `os`.
#      You can also consider using `pathlib.Path`.
#      It's a more modern approach to handling filesystem paths
import glob
import os

"""
[JO] Organizing files and folders can help you with your workflow.
     Each folder name can be customized - if you think "TXT" or "CSV" is
     more meaningful to you, then those will be the folder names.

        NEUR490 (project folder)
        |-- RAW (.txt files saved / your "Neur 490 TXT")
        |   |-- TD13 (subject specific folder)
        |   |   |-- TD13M3A2_R1_CC_RE.txt
        |   |   |-- TD13M3A3_R1_CC_RE.txt
        |   |   |-- ...
        |   |-- TD14
        |   |-- ...
        |-- CODE (.py files saved)
        |   |-- NEUR_490_analysis.py
        |-- PROCESSED (.csv files saved / your "NEUR 490 CSV")
        |   |-- TD13 (matching the subject specific folder in ../RAW)
        |   |   |-- TD13M3A2_R1_CC_RE.csv
        |   |   |-- ...

     Saving the path to your project folder and reuse it
     everytime you access its subordinate folders is recommended.

     Currently you're opening up this script sitting in the folder ('NEUR-490')
     but if you save the path to a variable, you don't need to
     worry about where your script is opened. This addresses your question
     ('I cannot directly locate them and have to upload them to my Python environment')
"""

# [JO] Make it a habit of not including whitespace characters
#      when you name a file or a folder (ex. "Neur 490 TXT" -> "Neur_490_TXT")

# input and output folders
input_folder = "Neur 490 TXT"
output_folder = "NEUR 490 CSV"
"""
[JO] `Path.mkdir()` does the same job. For example, suppose you make a
     `Path` object using the **path to the project** folder and name it 'wd':
         `wd = Path('/Users/joh/Documents/NEUR-490')`

     A `Path` object can be expanded using '/'. For example:
         `output_folder = wd / "NEUR 490 CSV"`
     saves the following path to 'output_folder':
         "/Users/joh/Documents/NEUR-490/NEUR 490 CSV"

     Then you can use the `.mkdir()` method of a `Path` object by running this line:
         `output_folder.mkdir(exist_ok=True)`
"""
os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist
"""
[JO] This can also be done with `Path.glob()`.
     First run:
         `input_folder = wd / "Neur 490 TXT"`
     then run:
         `txt_files = input_folder.glob("*.txt")`

     If you have subject specific folders, you want to do
     recursive glob, or `rglob`:
         `txt_files = input_folder.rglob("*.txt")`
"""
# find all TXT files in the input folder
txt_files = glob.glob(os.path.join(input_folder, "*.txt"))

print(f"Found {len(txt_files)} files.")

# loop through each file
for file_path in txt_files:

    # load the file
    names = ['Tier', 'start_ms', 'end_ms', 'duration_ms', 'label']
    codes = pd.read_csv(file_path, sep=r'\s+', header=None, names=names)

    # tier 'R'
    subset = (
        codes.loc[codes['Tier'] == 'R', ['start_ms', 'end_ms', 'label']]
        .dropna()
        .reset_index(drop=True)
    )
    # [JO] Using `.empty` is enough, because `.dropna()` already removed
    #      any missing rows, so `end_ms.isna().all()` will never be True.
    if subset.empty or subset['end_ms'].isna().all():
        print(f"Skipping {os.path.basename(file_path)} — no valid 'R' tier or missing end_ms.")
        continue

    # sample grid
    interval = 100  # ms
    """
    [JO] Rounding up the is not necessary, because `np.arange` already
         excludes the `stop` value.

         Suppose the value is not a multiple of 100 (ex. 60972.3).
         In `t = np.arange(0, end_time + interval, interval)`, 
         `end_time + interval` is the `stop` value.

         The sequence `t` covers a range [start, stop) where each value
         is greater than the previous one by 100 (ex. 0, 100, 200, ...).
         It stops at a multiple of 100 smaller than 60972 + 100 = 61072,
         which will be 61000.

         Your use of `np.ceil()` and `int()` is harmless - it simply makes
         the `stop` value 61000 + 100 = 61100, so the final multiple of 100
         smaller than that is again 61000.

         For readability, though, the line below is good enough: 
             `end_time = subset['end_ms'].max()
    """
    end_time = int(np.ceil(subset['end_ms'].max() / interval) * interval)
    t = np.arange(0, end_time + interval, interval, dtype=int)
    centers = t[:-1] + interval // 2

    # series
    series = np.zeros(len(centers), dtype=int)
    for _, row in subset.iterrows():
        mask = (centers >= row.start_ms) & (centers < row.end_ms)
        label = str(row.label).strip().upper()
        series[mask] = 1 if label == 'P' else 0

    # df
    binary_df = pd.DataFrame({
        'time_ms': t[:-1],
        'center_ms': centers,
        'binary_value': series
    })
    """
    [JO] Again, if you use `pathlib.Path()`, it has useful attributes:
         - `.stem`: returns the final path component, minus its last suffix.
                    (ex. `file_path.stem` -> 'TD13_M3A2_R1_CC_RE')
         - `.name`: returns the final path component with its last suffix.
                    (ex. `file_path.name` -> 'TD13_M3A2_R1_CC_RE.txt')
         - `.parent`: returns the folder that contains a file
                      (if the Path object is a file name)
                      or a folder one level above.
                      (if the Path object is a folder name)

         So you can prepare your output_path with the following:
             `output_path = output_folder / f"{file_path.stem}_binary.csv"`

         If your folders are similar to what I described above:
         (Top most project folder -> INPUT or OUTPUT folder -> Subject specific folder -> File)
             `output_path = output_folder / file_path.parent.stem / f"{file_path.stem}_binary.csv"
         will do the trick, because `file_path.parent.stem` will get
         the name of a subject specific folder (ex. TD13)
    """
    # save to CSV
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_binary.csv")
    binary_df.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")

print("All files processed successfully.")
