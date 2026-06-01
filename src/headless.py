from pathlib import Path
from model_optimized import ForestFireModel
from utils import vegetation_map_to_grid, load_fire_start, save_grid_as_png
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

OUTPUT_IMAGE_PATH = "rhodos_headless_result_optimized.png"

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

class HeadlessApp:
    def __init__(self):
        self.model = ForestFireModel(
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
        self.simulations_ran = 0

    def run(self, save_to_image):
        if self.simulations_ran > 0:
            self.model.reset()
        steps = 0
        while True:
            still_burning = self.model.step()
            steps += 1
            if not still_burning:
                self.simulations_ran += 1
                break
        
        if save_to_image:
            save_grid_as_png(self.model.grid, OUTPUT_IMAGE_PATH)
        
        return self.model.grid.copy(), steps
            

if __name__ == "__main__":
    app = HeadlessApp()
    _, steps = app.run(True)
    print(steps)