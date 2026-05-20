import sys
import pygame
from pathlib import Path
from model import ForestFireModel, COLORS

from convert_to_grid import vegetation_map_to_grid, load_fire_start

# =========================
# Configuration
# =========================
CELL_SIZE = 2
FPS = 40
STEP_DELAY_MS = 0

OUTPUT_IMAGE_PATH = r"yacutz_simulation_result.png"

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

IGNITION_TIME = 5
BURNING_TIME = 2
SMOLDERING_TIME = 16

BURNING_WIND_BONUS = 0.03
SMOLDERING_WIND_BONUS = 0.004
WIND_DIRECTION = "E"

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