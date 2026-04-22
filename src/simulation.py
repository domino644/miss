import sys
import random
import numpy as np

EMPTY = 0
TREE = 1
BURNING = 2
BURNED = 3
OBSTACLE = 4

class ForestFire:
    def __init__(
            self,
            width,
            height,
            tree_density,
            growth_prob,
            lightning_prob,
            spread_prob

    ):
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.growth_prob = growth_prob
        self.lightning_prob = lightning_prob
        self.spread_prob = spread_prob

        self.grid = np.zeros((width, height), dtype=np.uint8)
        self.step_count = 0
    
    def initialize(self):
        r = random.random((self.width, self.height))
        self.grid[r < self.tree_density] = TREE