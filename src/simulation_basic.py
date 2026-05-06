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

SPREAD_PROB = 1.0

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
    ):
        self.width = width
        self.height = height
        self.base_grid = grid.copy()
        self.fire_start = fire_start
        self.spread_prob = spread_prob

        self.grid = self.base_grid.copy()
        self.reset()

    def reset(self):
        self.grid = self.base_grid.copy()
        ignition_mask = (self.fire_start == 1) & (self.grid == TREE)
        self.grid[ignition_mask] = BURNING

    def neighbors(self, y: int, x: int):
        if y > 0:
            yield (y - 1, x)
        if y < self.height - 1:
            yield (y + 1, x)
        if x > 0:
            yield (y, x - 1)
        if x < self.width - 1:
            yield (y, x + 1)

    def step(self) -> bool:
        if not np.any(self.grid == BURNING):
            return False

        new_grid = self.grid.copy()

        for y, x in np.argwhere(self.grid == BURNING):
            for ny, nx in self.neighbors(y, x):
                if self.grid[ny, nx] == TREE and random.random() < self.spread_prob:
                    new_grid[ny, nx] = BURNING

            new_grid[y, x] = EMPTY

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
            spread_prob=SPREAD_PROB,
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