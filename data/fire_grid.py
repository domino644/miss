import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

CELL_SIZE_METERS = 375
CSV_PATH = "dataset.csv"
OUTPUT_DIR = "rhodes_fire_outputs"


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


def latlon_to_local_xy(df: pd.DataFrame) -> pd.DataFrame:
    lat0 = math.radians(df["latitude"].mean())
    lon0 = math.radians(df["longitude"].mean())

    earth_radius = 6371000

    lat_rad = np.radians(df["latitude"].values)
    lon_rad = np.radians(df["longitude"].values)

    x = earth_radius * (lon_rad - lon0) * math.cos(lat0)
    y = earth_radius * (lat_rad - lat0)

    result = df.copy()
    result["x_m"] = x
    result["y_m"] = y

    result["x_m"] = result["x_m"] - result["x_m"].min()
    result["y_m"] = result["y_m"] - result["y_m"].min()

    return result


def assign_grid_cells(df: pd.DataFrame, cell_size: int = CELL_SIZE_METERS) -> pd.DataFrame:
    result = df.copy()
    result["col"] = (result["x_m"] // cell_size).astype(int)
    result["row"] = (result["y_m"] // cell_size).astype(int)
    return result


def get_global_grid_shape(df: pd.DataFrame) -> tuple[int, int]:
    rows = int(df["row"].max()) + 1
    cols = int(df["col"].max()) + 1
    return rows, cols


def build_binary_grid(df: pd.DataFrame, rows: int, cols: int) -> np.ndarray:
    grid = np.zeros((rows, cols), dtype=np.uint8)

    for _, row in df.iterrows():
        r = int(row["row"])
        c = int(row["col"])
        grid[r, c] = 1

    return grid


def build_frp_grid(df: pd.DataFrame, rows: int, cols: int) -> np.ndarray:
    grid = np.zeros((rows, cols), dtype=float)

    for _, row in df.iterrows():
        r = int(row["row"])
        c = int(row["col"])
        frp = float(row["frp"]) if pd.notna(row.get("frp", np.nan)) else 0.0
        grid[r, c] = max(grid[r, c], frp)

    return grid


def save_binary_grid_plot(grid: np.ndarray, output_path: str, title: str):
    plt.figure(figsize=(10, 8))
    plt.imshow(grid, origin="lower", interpolation="nearest")
    plt.colorbar(label="Fire presence")
    plt.xlabel("Grid column")
    plt.ylabel("Grid row")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_frp_grid_plot(grid: np.ndarray, output_path: str, title: str):
    plt.figure(figsize=(10, 8))
    plt.imshow(grid, origin="lower", interpolation="nearest")
    plt.colorbar(label="FRP")
    plt.xlabel("Grid column")
    plt.ylabel("Grid row")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_timestamp_grids(df: pd.DataFrame, rows: int, cols: int, output_dir: str):
    timestamps = sorted(df["timestamp"].dropna().unique())

    for i, ts in enumerate(timestamps, start=1):
        df_ts = df[df["timestamp"] == ts]
        if df_ts.empty:
            continue

        grid_ts = build_binary_grid(df_ts, rows, cols)
        ts_str = pd.Timestamp(ts).strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(output_dir, f"grid_{i:03d}_{ts_str}.png")
        title = f"Fire detections at {ts}"
        save_binary_grid_plot(grid_ts, filename, title)


def save_fire_animation(
    df: pd.DataFrame,
    rows: int,
    cols: int,
    output_path: str,
    cumulative: bool = True,
    interval_ms: int = 700,
):
    timestamps = sorted(df["timestamp"].dropna().unique())

    fig, ax = plt.subplots(figsize=(10, 8))
    grid0 = np.zeros((rows, cols), dtype=np.uint8)

    im = ax.imshow(
        grid0,
        origin="lower",
        interpolation="nearest",
        vmin=0,
        vmax=1,
        cmap="hot",
    )

    ax.set_xlabel("Grid column")
    ax.set_ylabel("Grid row")
    title = ax.set_title("Rhodes fire animation")

    def update(frame_idx):
        ts = timestamps[frame_idx]

        if cumulative:
            df_frame = df[df["timestamp"] <= ts]
        else:
            df_frame = df[df["timestamp"] == ts]

        grid = build_binary_grid(df_frame, rows, cols)
        im.set_data(grid)

        mode = "cumulative" if cumulative else "instant"
        title.set_text(f"Rhodes fire - {mode} - {pd.Timestamp(ts)}")

        return [im, title]

    anim = FuncAnimation(
        fig,
        update,
        frames=len(timestamps),
        interval=interval_ms,
        blit=False,
        repeat=True,
    )

    anim.save(output_path, writer=PillowWriter(fps=max(1, 1000 // interval_ms)))
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_data(CSV_PATH)
    df = latlon_to_local_xy(df)
    df = assign_grid_cells(df, CELL_SIZE_METERS)

    rows, cols = get_global_grid_shape(df)

    print(f"Loaded rows: {len(df)}")
    print(f"Global grid shape: {rows} x {cols}")

    binary_grid = build_binary_grid(df, rows, cols)
    save_binary_grid_plot(
        binary_grid,
        os.path.join(OUTPUT_DIR, "fire_binary_grid.png"),
        "Rhodes fire as 375m x 375m binary grid"
    )

    frp_grid = build_frp_grid(df, rows, cols)
    save_frp_grid_plot(
        frp_grid,
        os.path.join(OUTPUT_DIR, "fire_frp_grid.png"),
        "Rhodes fire as 375m x 375m FRP grid"
    )

    save_timestamp_grids(df, rows, cols, OUTPUT_DIR)

    save_fire_animation(
        df,
        rows,
        cols,
        os.path.join(OUTPUT_DIR, "fire_animation_cumulative.gif"),
        cumulative=True,
        interval_ms=700,
    )

    save_fire_animation(
        df,
        rows,
        cols,
        os.path.join(OUTPUT_DIR, "fire_animation_instant.gif"),
        cumulative=False,
        interval_ms=700,
    )

    df.to_csv(os.path.join(OUTPUT_DIR, "fire_points_with_grid_coords.csv"), index=False)

    print("Done.")
    print(f"Files saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()