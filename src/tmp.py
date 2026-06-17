import time
import numpy as np
from utils import vegetation_map_to_grid, load_fire_start, save_grid_as_png
import random
from model import ForestFireModel as ModelOriginal
from model import ForestFireModel as ModelOptimized
from simulation_params import (
    DATA_DIR,
    BURNING_SPREAD_PROB,
    SMOLDERING_SPREAD_PROB,
    IGNITION_TIME,
    BURNING_TIME,
    SMOLDERING_TIME,
    BURNING_WIND_BONUS,
    SMOLDERING_WIND_BONUS,
    WIND_DIRECTION,
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

model_original = ModelOriginal(
    width=GRID_WIDTH,
    height=GRID_HEIGHT,
    grid=GRID,
    fire_start=FIRE_START,
    burning_spread_prob=BURNING_SPREAD_PROB,
    smoldering_spread_prob=SMOLDERING_SPREAD_PROB,
    ignition_time=IGNITION_TIME,
    burning_time=BURNING_TIME,
    smoldering_time=SMOLDERING_TIME,
    wind_direction=WIND_DIRECTION,
    burning_wind_bonus=BURNING_WIND_BONUS,
    smoldering_wind_bonus=SMOLDERING_WIND_BONUS
)

model_optimized = ModelOptimized(
    width=GRID_WIDTH,
    height=GRID_HEIGHT,
    grid=GRID,
    fire_start=FIRE_START,
    burning_spread_prob=BURNING_SPREAD_PROB,
    smoldering_spread_prob=SMOLDERING_SPREAD_PROB,
    ignition_time=IGNITION_TIME,
    burning_time=BURNING_TIME,
    smoldering_time=SMOLDERING_TIME,
    wind_direction=WIND_DIRECTION,
    burning_wind_bonus=BURNING_WIND_BONUS,
    smoldering_wind_bonus=SMOLDERING_WIND_BONUS
)

seed = 123

start_time = time.time()
random.seed(seed)
np.random.seed(seed)
while model_original.step():
    pass
result_orig = model_original.grid.copy()
end_time = time.time()

print(f"Original: {end_time - start_time} s")

start_time = time.time()
random.seed(seed)
np.random.seed(seed)
while model_optimized.step():
    pass
result_stack = model_optimized.grid.copy()
end_time = time.time()

print(f"Optimized: {end_time - start_time} s")

# porównanie
print(np.array_equal(result_orig, result_stack))

save_grid_as_png(result_orig, 'tmp_original.png')
save_grid_as_png(result_stack, 'tmp_stack.png')