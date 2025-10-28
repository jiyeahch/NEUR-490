import pandas as pd
import numpy as np

# I exported timestamps, durations, like everything.
# You may adapt your code according to how you export your ELAN coding.

names = ['Tier', 'start_ms', 'end_ms', 'duration_ms', 'label']

codes = pd.read_csv(
    'Neur 490 TXT/TD13-M3_A2R1_CC_RE.txt',
    sep=r'\s+',
    header=None,
    names=names
)

subset = (codes.loc[codes['Tier'] == 'R', ['start_ms', 'end_ms', 'label']].dropna().reset_index(drop=True))

# Example: Tier 'R'
# 'subset' will look like this:
#
# start_s | end_s | label
# 0.00    | 3.72  | NP
# 3.72    | 7.21  | P
# 7.21    | 35.70 | NP
# ...

# Sampling grid
interval = 100
end_time = int(np.ceil(subset['end_ms'].max() / interval) * interval)
t = np.arange(0, end_time + interval, interval, dtype=int)   # 0, 100, 200, ...
centers = t[:-1] + interval // 2

# Vector to fill
series = np.zeros(len(centers), dtype=int)

# Fill according to event active at each bin center
for _, row in subset.iterrows():
    mask = (centers >= row.start_ms) & (centers < row.end_ms)
    label = str(row.label).strip().upper()
    series[mask] = 1 if label == 'P' else 0

print(f"Total bins: {len(series)}  (~{len(series)/20:.1f} seconds)")

# binary sequence numerically aligned with time
binary_df = pd.DataFrame({
    'time_ms': t[:-1],
    'center_ms': centers,
    'binary_value': series
})
print(binary_df)

binary_df.to_csv('NEUR 490 CSV (binary)/TD13-M3_A2R1_CC_RE_binary.csv', index=False)