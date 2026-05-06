import sys
import random
import numpy as np
import pygame

from convert_to_grid import vegetation_map_to_grid, load_fire_start

OUTPUT_IMAGE_PATH = r"simulation_result.png"

# =========================
# Configuration
# =========================
CELL_SIZE = 2
FPS = 60
STEP_DELAY_MS = 0

GRID = vegetation_map_to_grid(
    r"C:\Users\Lukasz\Documents\GitHub\miss\data\rhodos\vegetation_before.png"
)
GRID_HEIGHT = GRID.shape[0]
GRID_WIDTH = GRID.shape[1]

FIRE_START = load_fire_start(
    r"C:\Users\Lukasz\Documents\GitHub\miss\data\rhodes_fire_outputs\fire_start_grid.png",
    GRID_WIDTH,
    GRID_HEIGHT,
)

SPREAD_PROB = 0.15
WIND_BONUS = 0.75
WIND_DIRECTION = "S"

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
BURNING = 2
WATER = 3

COLORS = {
    EMPTY: (196, 164, 132),
    TREE: (34, 105, 34),
    BURNING: (230, 80, 30),
    WATER: (15, 94, 156),
}


class ForestFireModel:
    def __init__(
        self,
        width: int,
        height: int,
        grid: np.ndarray,
        fire_start: np.ndarray,
        spread_prob: float = 1.0,
        wind_direction: str | None = None,
        wind_bonus: float = 0.0,
    ):
        self.width = width
        self.height = height
        self.base_grid = grid.copy()
        self.fire_start = fire_start
        self.spread_prob = spread_prob
        self.wind_direction = wind_direction
        self.wind_bonus = wind_bonus

        self.grid = self.base_grid.copy()
        self.reset()

    def reset(self):
        self.grid = self.base_grid.copy()
        # self.fire_start = np.zeros((self.height, self.width), dtype=np.uint8)
        ignition_mask = (self.fire_start == 1) & (self.grid == TREE)
        self.grid[ignition_mask] = BURNING

    def neighbors(self, y: int, x: int):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue

                ny = y + dy
                nx = x + dx

                if 0 <= ny < self.height and 0 <= nx < self.width:
                    yield ny, nx, dy, dx

    def spread_probability_for_offset(self, dy: int, dx: int) -> float:
        prob = self.spread_prob

        if self.wind_direction is not None:
            boosted = WIND_FORWARD_NEIGHBORS.get(self.wind_direction, [])
            if (dy, dx) in boosted:
                prob = min(1.0, prob + self.wind_bonus)

        return prob

    def step(self) -> bool:
        if not np.any(self.grid == BURNING):
            return False

        new_grid = self.grid.copy()

        for y, x in np.argwhere(self.grid == BURNING):
            for ny, nx, dy, dx in self.neighbors(y, x):
                if self.grid[ny, nx] == TREE:
                    spread_prob = self.spread_probability_for_offset(dy, dx)
                    if random.random() < spread_prob:
                        new_grid[ny, nx] = BURNING

            new_grid[y, x] = EMPTY

        self.grid = new_grid
        return np.any(self.grid == BURNING)


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
            spread_prob=SPREAD_PROB,
            wind_direction=WIND_DIRECTION,
            wind_bonus=WIND_BONUS,
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