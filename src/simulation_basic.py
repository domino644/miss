import sys
import random
import numpy as np
import pygame
from pathlib import Path

from convert_to_grid import vegetation_map_to_grid, load_fire_start

OUTPUT_IMAGE_PATH = r"yacutz_simulation_result.png"

# =========================
# Configuration
# =========================
CELL_SIZE = 3
FPS = 40
STEP_DELAY_MS = 0

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "yacutz"

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

BURNING_SPREAD_PROB = 0.07
SMOLDERING_SPREAD_PROB = 0.008

IGNITION_TIME = 4
BURNING_TIME = 2
SMOLDERING_TIME = 12

BURNING_WIND_BONUS = 0.02
SMOLDERING_WIND_BONUS = 0.002
WIND_DIRECTION = "E"

WIND_FORWARD_NEIGHBORS = {
    "N":  [(-1, -1), (-1, 0), (-1, 1)],
    "NE": [(-1, 0), (-1, 1), (0, 1)],
    "E":  [(-1, 1), (0, 1), (1, 1)],
    "SE": [(0, 1), (1, 1), (1, 0)],
    "S":  [(1, -1), (1, 0), (1, 1)],
    "SW": [(0, -1), (1, -1), (1, 0)],
    "W":  [(-1, -1), (0, -1), (1, -1)],
    "NW": [(-1, 0), (-1, -1), (0, -1)],
}

# =========================
# Cell states
# =========================
EMPTY = 0
TREE = 1
IGNITING = 2
BURNING = 3
SMOLDERING = 4
BURNED = 5
WATER = 6

COLORS = {
    EMPTY: (161, 117, 73),
    TREE: (34, 105, 34),
    IGNITING: (232, 144, 86),
    BURNING: (255, 248, 141),
    SMOLDERING: (112, 14, 14),
    BURNED: (67,67,67),
    WATER: (9,55,100),
}


class ForestFireModel:
    def __init__(
        self,
        width: int,
        height: int,
        grid: np.ndarray,
        fire_start: np.ndarray,
        burning_spread_prob: float = 1.0,
        smoldering_spread_prob: float = 1.0,
        ignition_time: int = 1,
        burning_time: int = 1,
        smoldering_time: int = 1,
        wind_direction: str | None = None,
        burning_wind_bonus: float = 0.0,
        smoldering_wind_bonus: float = 0.0
    ):
        self.width = width
        self.height = height
        self.base_grid = grid.copy()
        self.times = np.zeros((height, width), dtype=np.uint8)

        self.fire_start = fire_start

        self.burning_spread_prob = burning_spread_prob
        self.smoldering_spread_prob = smoldering_spread_prob

        self.ignition_time = ignition_time
        self.burning_time = burning_time
        self.smoldering_time = smoldering_time

        self.wind_direction = wind_direction
        self.burning_wind_bonus = burning_wind_bonus
        self.smoldering_wind_bonus = smoldering_wind_bonus

        self.grid = self.base_grid.copy()
        self.reset()

    def reset(self):
        self.grid = self.base_grid.copy()
        self.times = np.zeros((self.height, self.width), dtype=np.uint8)
        # self.fire_start = np.zeros((self.height, self.width), dtype=np.uint8)
        ignition_mask = (self.fire_start == 1) & (self.grid == TREE)
        self.grid[ignition_mask] = IGNITING
        self.times[ignition_mask] = self.ignition_time

    def neighbors(self, y: int, x: int):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue

                ny = y + dy
                nx = x + dx

                if 0 <= ny < self.height and 0 <= nx < self.width:
                    yield ny, nx, dy, dx

    def spread_probability_for_offset(self, dy: int, dx: int, prob:float, cell_state: int) -> float:
        if cell_state == BURNING:
            wind_bonus = self.burning_wind_bonus
        else:
            wind_bonus = self.smoldering_wind_bonus
        new_prob = prob
        if self.wind_direction is not None:
            boosted = WIND_FORWARD_NEIGHBORS.get(self.wind_direction, [])
            if (dy, dx) in boosted:
                new_prob = min(1.0, prob + wind_bonus)

        return new_prob

    def step(self) -> bool:
        new_grid = self.grid.copy()

        active_mask = (self.grid == IGNITING) | (self.grid == BURNING) | (self.grid == SMOLDERING)

        if not np.any(active_mask):
            return False

        for y, x in np.argwhere(active_mask):
            cell_state = self.grid[y, x]
            if cell_state == IGNITING:
                self.times[y, x] -= 1
                if self.times[y, x] == 0:
                    new_grid[y, x] = BURNING
                    self.times[y, x] = self.burning_time
            else:
                if cell_state == BURNING:
                    current_prob = self.burning_spread_prob
                    new_time = self.smoldering_time
                    new_state = SMOLDERING
                else:
                    current_prob = self.smoldering_spread_prob
                    new_time = 0
                    new_state = BURNED

                for ny, nx, dy, dx in self.neighbors(y, x):
                    if self.grid[ny, nx] == TREE:
                        adjusted_burning_spread_prob = self.spread_probability_for_offset(dy, dx, current_prob, cell_state)
                        if random.random() < adjusted_burning_spread_prob:
                            new_grid[ny, nx] = IGNITING
                            self.times[ny, nx] = self.ignition_time

                self.times[y, x] -= 1
                if self.times[y, x] == 0:
                    new_grid[y, x] = new_state
                    self.times[y, x] = new_time
        
        self.grid = new_grid

        return True


class SimulationApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Forest Fire Simulation")

        self.screen_width = GRID_WIDTH * CELL_SIZE
        self.screen_height = GRID_HEIGHT * CELL_SIZE

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.last_step_time = 0

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

        self.running = True

    def draw_grid(self):
        for y in range(self.model.height):
            for x in range(self.model.width):
                state = self.model.grid[y, x]
                color = COLORS[int(state)]
                rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(self.screen, color, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_step_time >= STEP_DELAY_MS:
            still_burning = self.model.step()
            self.last_step_time = now

            if not still_burning:
                self.render()
                pygame.image.save(self.screen, OUTPUT_IMAGE_PATH)
                print(f"Saved final state to: {OUTPUT_IMAGE_PATH}")
                self.running = False

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = SimulationApp()
    app.run()