import sys
import random
import numpy as np
import pygame
import csv
from convert_to_grid import vegetation_map_to_grid, load_fire_start
from PIL import Image

# =========================
# Configuration
# =========================
CELL_SIZE = 1
SIDE_PANEL_WIDTH = 280
FPS = 60
STEP_DELAY_MS = 0

GRID = vegetation_map_to_grid(r"C:\Users\Lukasz\Documents\GitHub\miss\data\rhodos\vegetation_before.png")
GRID_WIDTH = GRID.shape[1]
GRID_HEIGHT = GRID.shape[0]

FIRE_START = load_fire_start(r"C:\Users\Lukasz\Documents\GitHub\miss\data\rhodes_fire_outputs\fire_start_grid.png", GRID_WIDTH, GRID_HEIGHT)

print(f"Grid shape: {GRID_WIDTH, GRID_HEIGHT}")

# Initial model parameters
TREE_DENSITY = 0.4
GROWTH_PROB = 0.0   # probability that empty/burned cell becomes a tree
LIGHTNING_PROB = 0.0   # probability of ignition attempt in a step
SPREAD_PROB = 0.5      # probability fire spreads to a neighboring tree

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
    WATER: (15,94,156),
}

# =========================
# Model
# =========================
class ForestFireModel:
    def __init__(
        self,
        width,
        height,
        grid = None,
        fire_start = None,
        tree_density=0.65,
        growth_prob=0.003,
        lightning_prob=0.01,
        spread_prob=0.35,
    ):
        self.width = width
        self.height = height

        self.tree_density = tree_density
        self.growth_prob = growth_prob
        self.lightning_prob = lightning_prob
        self.spread_prob = spread_prob

        self.grid_given = False
        if grid is None:
            self.grid = np.zeros((height, width), dtype=np.uint8)
        else:
            self.grid_given = True
            self.grid = grid
            self.fire_start = fire_start

        self.step_count = 0

        # Fire event tracking
        self.current_fire_size = 0
        self.fire_sizes = []

        self.reset()

    def reset(self):
        self.step_count = 0
        self.current_fire_size = 0
        self.fire_sizes = []

        if not self.grid_given:
            r = np.random.random((self.height, self.width))
            self.grid[:, :] = EMPTY
            self.grid[r < self.tree_density] = TREE
        else:
            ignition_mask = (self.fire_start == 1) & (self.grid == TREE)
            self.grid[ignition_mask] = BURNING

    def neighbors(self, y, x):
        # von Neumann neighborhood: up, down, left, right
        if y > 0:
            yield (y - 1, x)
        if y < self.height - 1:
            yield (y + 1, x)
        if x > 0:
            yield (y, x - 1)
        if x < self.width - 1:
            yield (y, x + 1)

    def count_cells(self):
        unique, counts = np.unique(self.grid, return_counts=True)
        result = {state: 0 for state in [EMPTY, TREE, BURNING]}
        for state, count in zip(unique, counts):
            result[int(state)] = int(count)
        return result

    def ignite_random_tree(self):
        trees = np.argwhere(self.grid == TREE)
        if len(trees) == 0:
            return False

        y, x = trees[np.random.randint(len(trees))]
        self.grid[y, x] = BURNING
        self.current_fire_size = 1
        return True
    
    def ignite_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y, x] == TREE:
                self.grid[y, x] = BURNING
                if self.current_fire_size == 0:
                    self.current_fire_size = 1
                return True
        return False

    def step(self):
        self.step_count += 1
        burning_exists = np.any(self.grid == BURNING)

        # If there is active fire, propagate it
        if burning_exists:
            new_grid = self.grid.copy()

            for y, x in np.argwhere(self.grid == BURNING):
                for ny, nx in self.neighbors(y, x):
                    if self.grid[ny, nx] == TREE and random.random() < self.spread_prob:
                        new_grid[ny, nx] = BURNING

                # current burning cell becomes burned
                new_grid[y, x] = EMPTY

            newly_ignited = np.sum((self.grid != BURNING) & (new_grid == BURNING))
            self.current_fire_size += int(newly_ignited)
            self.grid = new_grid

            # if fire ended, save its size
            if not np.any(self.grid == BURNING) and self.current_fire_size > 0:
                self.fire_sizes.append(self.current_fire_size)
                self.current_fire_size = 0

        else:
            # regrowth on empty or burned cells
            grow_mask = (self.grid == EMPTY) & (
                np.random.random((self.height, self.width)) < self.growth_prob
            )
            self.grid[grow_mask] = TREE

            # maybe lightning starts a new fire
            if random.random() < self.lightning_prob and not burning_exists:
                self.ignite_random_tree()

    def set_cell(self, x, y, state):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = state

    def save_fire_sizes_to_csv(self, filename="fire_sizes2.csv"):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["fire_id", "size"])
            for i, size in enumerate(self.fire_sizes, start=1):
                writer.writerow([i, size])


# =========================
# UI / App
# =========================
class SimulationApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Forest Fire Simulation")

        self.screen_width = GRID_WIDTH * CELL_SIZE + SIDE_PANEL_WIDTH
        self.screen_height = GRID_HEIGHT * CELL_SIZE

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.last_step_time = 0

        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.model = ForestFireModel(
            GRID_WIDTH,
            GRID_HEIGHT,
            grid=GRID,
            tree_density=TREE_DENSITY,
            growth_prob=GROWTH_PROB,
            lightning_prob=LIGHTNING_PROB,
            spread_prob=SPREAD_PROB,
        )

        self.running = True
        self.paused = False

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

    def draw_panel(self):
        panel_x = GRID_WIDTH * CELL_SIZE
        panel_rect = pygame.Rect(panel_x, 0, SIDE_PANEL_WIDTH, self.screen_height)
        pygame.draw.rect(self.screen, (25, 25, 25), panel_rect)

        counts = self.model.count_cells()
        total_fires = len(self.model.fire_sizes)
        avg_fire_size = (
            sum(self.model.fire_sizes) / total_fires if total_fires > 0 else 0.0
        )
        max_fire_size = max(self.model.fire_sizes) if total_fires > 0 else 0

        lines = [
            "Forest Fire Simulation",
            "",
            f"Step: {self.model.step_count}",
            f"Paused: {'YES' if self.paused else 'NO'}",
            "",
            f"Trees: {counts[TREE]}",
            f"Burning: {counts[BURNING]}",
            f"Empty: {counts[EMPTY]}",
            "",
            f"Recorded fires: {total_fires}",
            f"Avg fire size: {avg_fire_size:.2f}",
            f"Max fire size: {max_fire_size}",
            "",
            f"Spread prob: {self.model.spread_prob:.2f}",
            f"Lightning prob: {self.model.lightning_prob:.3f}",
            f"Growth prob: {self.model.growth_prob:.3f}",
            "",
            "Controls:",
            "SPACE - pause/resume",
            "N - single step",
            "R - reset",
            "UP/DOWN - spread +/-",
            "LEFT/RIGHT - lightning +/-",
            "W/S - growth +/-",
            "P - save fire sizes to csv"
            "",
            "Mouse when paused:",
            "LMB - ignite tree"
        ]

        y = 20
        for i, line in enumerate(lines):
            font = self.font if i == 0 else self.small_font
            text = font.render(line, True, (230, 230, 230))
            self.screen.blit(text, (panel_x + 15, y))
            y += 24 if i == 0 else 20

    def handle_mouse_edit(self, event):
        if not self.paused:
            return

        if event.button != 1:
            return

        mx, my = pygame.mouse.get_pos()
        if mx >= GRID_WIDTH * CELL_SIZE or my >= GRID_HEIGHT * CELL_SIZE:
            return

        x = mx // CELL_SIZE
        y = my // CELL_SIZE

        self.model.ignite_cell(x, y)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                elif event.key == pygame.K_n:
                    if self.paused:
                        self.model.step()

                elif event.key == pygame.K_r:
                    self.model.reset()

                elif event.key == pygame.K_UP:
                    self.model.spread_prob = min(1.0, self.model.spread_prob + 0.02)

                elif event.key == pygame.K_DOWN:
                    self.model.spread_prob = max(0.0, self.model.spread_prob - 0.02)

                elif event.key == pygame.K_RIGHT:
                    self.model.lightning_prob = min(1.0, self.model.lightning_prob + 0.002)

                elif event.key == pygame.K_LEFT:
                    self.model.lightning_prob = max(0.0, self.model.lightning_prob - 0.002)

                elif event.key == pygame.K_w:
                    self.model.growth_prob = min(1.0, self.model.growth_prob + 0.001)

                elif event.key == pygame.K_s:
                    self.model.growth_prob = max(0.0, self.model.growth_prob - 0.001)

                elif event.key == pygame.K_p:
                    self.model.save_fire_sizes_to_csv()
                    print("Saved fire sizes to fire_sizes.csv")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_edit(event)

    def update(self):
        now = pygame.time.get_ticks()
        if not self.paused and now - self.last_step_time >= STEP_DELAY_MS:
            self.model.step()
            self.last_step_time = now

    # def update(self):
    #     if not self.paused:
    #         self.model.step()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_panel()
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