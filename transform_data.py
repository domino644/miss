import pandas as pd

filenames = [
    "data/raw/DL_FIRE_J1V-C2_740979/fire_archive_J1V-C2_740979.csv",
    "data/raw/DL_FIRE_SV-C2_740981/fire_archive_SV-C2_740981.csv",
]


dfs = [pd.read_csv(filename) for filename in filenames]

df = pd.concat(dfs, ignore_index=True)

df["timestamp"] = pd.to_datetime(
    df["acq_date"] + " " + df["acq_time"].astype(str).str.zfill(4),
    format="%Y-%m-%d %H%M",
)

df = df.sort_values("timestamp")

df.to_csv("data/dataset.csv")
