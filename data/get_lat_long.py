import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    first_col = str(df.columns[0])
    if first_col.startswith("Unnamed") or first_col == "":
        df = df.drop(columns=df.columns[0])

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        df["timestamp"] = pd.to_datetime(
            df["acq_date"].astype(str) + " " + df["acq_time"].astype(str).str.zfill(4),
            format="%Y-%m-%d %H%M",
            errors="coerce",
        )

    df = df.dropna(subset=["latitude", "longitude"]).copy()
    return df



data = load_data("dataset.csv")

top_left = (data["latitude"].max(), data["longitude"].min())
bottom_right = (data["latitude"].min(), data["longitude"].max())

print(f"Top left: {top_left}")
print(f"Bottom right: {bottom_right}")