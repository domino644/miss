import optuna
from model import ForestFireModel
from datetime import datetime
from utils import empty_mask_iou, vegetation_map_to_grid, load_fire_start
from simulation_params import (
    DATA_DIR,
)

SATELLITE_AFTER_GRID = vegetation_map_to_grid(
    DATA_DIR / "vegetation_river_after.png"
)

GRID = vegetation_map_to_grid(
    DATA_DIR / "vegetation_river_before.png"
)

GRID_HEIGHT = GRID.shape[0]
GRID_WIDTH = GRID.shape[1]

FIRE_START = load_fire_start(
    DATA_DIR / "fire_start_grid.png",
    GRID_WIDTH,
    GRID_HEIGHT,
)

RESULTS_FILE = "optuna_results.txt"

def objective(trial):
    burning_spread_prob = trial.suggest_float("burning_spread_prob", 0.01, 0.1)
    smoldering_spread_prob = trial.suggest_float("smoldering_spread_prob", 0.002, 0.02)

    ignition_time = trial.suggest_int("ignition_time", 1, 10)
    burning_time = trial.suggest_int("burning_time", 1, 5)
    smoldering_time = trial.suggest_int("smoldering_time", 1, 30)

    burning_wind_bonus = trial.suggest_float("burning_wind_bonus", 0.0, 0.1)
    smoldering_wind_bonus = trial.suggest_float("smoldering_wind_bonus", 0.0, 0.02)

    wind_direction = trial.suggest_categorical(
        "wind_direction",
        ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    )

    model = ForestFireModel(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        grid=GRID.copy(),
        fire_start=FIRE_START.copy(),
        burning_spread_prob=burning_spread_prob,
        smoldering_spread_prob=smoldering_spread_prob,
        ignition_time=ignition_time,
        burning_time=burning_time,
        smoldering_time=smoldering_time,
        wind_direction=wind_direction,
        burning_wind_bonus=burning_wind_bonus,
        smoldering_wind_bonus=smoldering_wind_bonus,
    )

    while model.step():
        pass

    score = empty_mask_iou(model.grid, SATELLITE_AFTER_GRID)
    return score


sampler = optuna.samplers.TPESampler()
study = optuna.create_study(direction="maximize", sampler=sampler)
study.optimize(objective, n_trials=20)

with open(RESULTS_FILE, "a", encoding="utf-8") as f:
    f.write(f"=== {datetime.now().isoformat()} ===\n")
    f.write(f"Best value: {study.best_value}\n")
    f.write("Best params:\n")
    for key, value in study.best_params.items():
        f.write(f"  {key}: {value}\n")
    f.write("\n")