import optuna
from model import ForestFireModel
from datetime import datetime
from utils import empty_mask_iou, vegetation_map_to_grid, load_fire_start
from simulation_params import (
    FIRE_NAME,
    DATA_DIR,
    EXPECTED_STEPS
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

RESULTS_FILE = f"{FIRE_NAME}_optuna_results.txt"

def objective(trial):
    n = 4
    rain_schedule = [
        trial.suggest_int(f"rain_schedule_{i}", 0, 1)
        for i in range(n)
    ]
    k = 3
    wind_schedule = [
        trial.suggest_categorical(f"wind_schedule_{i}", ["N", "NE", "E", "SE", "S", "SW", "W", "NW", False])
        for i in range(k)
    ]
    burning_spread_prob = trial.suggest_float("burning_spread_prob", 0.01, 0.4)
    smoldering_spread_prob = trial.suggest_float("smoldering_spread_prob", 0.002, 0.15)

    ignition_time = trial.suggest_int("ignition_time", 1, 10)
    burning_time = trial.suggest_int("burning_time", 1, 5)
    smoldering_time = trial.suggest_int("smoldering_time", 1, 30)

    burning_wind_bonus = trial.suggest_float("burning_wind_bonus", 0.0, 0.1)
    smoldering_wind_bonus = trial.suggest_float("smoldering_wind_bonus", 0.0, 0.05)

    rain_multiplier = trial.suggest_float("rain_multiplier", 0.0, 1.0)
    extinguish_probability = trial.suggest_float("extinguish_probability", 0.0, 1.0)

    model = ForestFireModel(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        grid=GRID.copy(),
        expected_steps=EXPECTED_STEPS,
        fire_start=FIRE_START.copy(),
        rain_schedule=rain_schedule,
        burning_spread_prob=burning_spread_prob,
        smoldering_spread_prob=smoldering_spread_prob,
        ignition_time=ignition_time,
        burning_time=burning_time,
        smoldering_time=smoldering_time,
        wind_schedule=wind_schedule,
        burning_wind_bonus=burning_wind_bonus,
        smoldering_wind_bonus=smoldering_wind_bonus,
        rain_multiplier=rain_multiplier,
        extinguish_probability=extinguish_probability
    )

    while True:
        still_burning, steps = model.step()
        if not still_burning:
            break

    score = empty_mask_iou(model.grid, SATELLITE_AFTER_GRID, steps, EXPECTED_STEPS)
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