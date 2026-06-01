import random
import numpy as np

EMPTY = 0
TREE = 1
IGNITING = 2
BURNING = 3
SMOLDERING = 4
BURNED = 5
WATER = 6

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

class ForestFireModel:
    def __init__(
        self,
        width: int,
        height: int,
        grid: np.ndarray,
        max_steps: int,
        fire_start: np.ndarray,
        burning_spread_prob: float = 1.0,
        smoldering_spread_prob: float = 1.0,
        ignition_time: int = 1,
        burning_time: int = 1,
        smoldering_time: int = 1,
        wind_direction: str | None = None,
        burning_wind_bonus: float = 0.0,
        smoldering_wind_bonus: float = 0.0,
        rain_schedule: int = 0,
        rain_multiplier: float = 0.0,
        extinguish_probability: float = 0.0
    ):
        self.width = width
        self.height = height
        self.base_grid = grid.copy()
        self.max_steps = max_steps
        self.times = np.zeros((height, width), dtype=np.uint8)

        if fire_start is None:
            self.fire_start = np.zeros((self.height, self.width), dtype=np.uint8)
        else:
            self.fire_start = fire_start

        self.burning_spread_prob = burning_spread_prob
        self.smoldering_spread_prob = smoldering_spread_prob

        self.ignition_time = ignition_time
        self.burning_time = burning_time
        self.smoldering_time = smoldering_time

        self.wind_direction = wind_direction
        self.burning_wind_bonus = burning_wind_bonus
        self.smoldering_wind_bonus = smoldering_wind_bonus

        self.rain_schedule = [b == "1" for b in bin(rain_schedule)[2:]]
        self.rain_multiplier = rain_multiplier
        self.extinguish_probability = extinguish_probability

        self.incoming_cells = []
        self.reset()

    def reset(self):
        self.grid = self.base_grid.copy()
        self.times = np.zeros((self.height, self.width), dtype=np.uint8)
        ignition_mask = (self.fire_start == 1) & (self.grid == TREE)
        self.grid[ignition_mask] = IGNITING
        self.times[ignition_mask] = self.ignition_time
        self.active_cells = [(y, x) for y, x in np.argwhere(ignition_mask)]
        self.steps = 0

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
        
        if self.rain_active:
            new_prob *= self.rain_multiplier

        return new_prob

    def step(self) -> bool:
        if not self.active_cells:
            return False, self.steps
        
        self.rain_active = self.rain_schedule[min(int((self.steps * self.rain_intervals) / self.max_steps), self.rain_intervals - 1)]

        while self.active_cells:
            y, x = self.active_cells.pop()
            cell_state = self.grid[y, x]
            if cell_state == IGNITING:
                if self.rain_active and random.random() < self.extinguish_probability:
                    self.grid[y, x] = TREE
                    self.times[y, x] = 0
                    continue
                self.times[y, x] -= 1
                if self.times[y, x] == 0:
                    self.grid[y, x] = BURNING
                    self.times[y, x] = self.burning_time
                self.incoming_cells.append((y, x))
            else:
                if cell_state == BURNING:
                    current_prob = self.burning_spread_prob
                    new_time = self.smoldering_time
                    new_state = SMOLDERING
                else:
                    current_prob = self.smoldering_spread_prob
                    new_time = 0
                    new_state = EMPTY

                for ny, nx, dy, dx in self.neighbors(y, x):
                    if self.grid[ny, nx] == TREE:
                        adjusted_burning_spread_prob = self.spread_probability_for_offset(dy, dx, current_prob, cell_state)
                        if random.random() < adjusted_burning_spread_prob:
                            self.grid[ny, nx] = IGNITING
                            self.times[ny, nx] = self.ignition_time
                            self.incoming_cells.append((ny, nx))

                self.times[y, x] -= 1
                if self.times[y, x] == 0:
                    self.grid[y, x] = new_state
                    self.times[y, x] = new_time
                    if new_state != EMPTY:
                        self.incoming_cells.append((y, x))
                else:
                    self.incoming_cells.append((y, x))
        
        self.active_cells, self.incoming_cells = self.incoming_cells, self.active_cells
        self.steps += 1

        return True, None
