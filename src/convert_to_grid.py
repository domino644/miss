from PIL import Image
import numpy as np
import random

EMPTY = 0
TREE = 1
BURNING = 2
WATER = 3

COLOR_TO_STATE = {
    (0, 160, 0): TREE,        # #00a000
    (128, 128, 128): WATER,   # #808080
    (192, 192, 192): WATER,   # #c0c0c0
    (0, 0, 255): WATER,       # #0000ff
}

def downsample_grid_by_2(grid: np.ndarray) -> np.ndarray:
    old_height, old_width = grid.shape

    new_height = old_height // 2
    new_width = old_width // 2

    downsampled = np.zeros((new_height, new_width), dtype=np.uint8)

    for y in range(new_height):
        for x in range(new_width):
            block = grid[2*y:2*y+2, 2*x:2*x+2].flatten()

            # Priorytet: jeśli gdziekolwiek jest TREE, wynik = TREE
            # if np.any(block == TREE):
            #     downsampled[y, x] = TREE
            #     continue

            values, counts = np.unique(block, return_counts=True)
            max_count = counts.max()
            candidates = values[counts == max_count]

            # Jeśli remis, losowo
            downsampled[y, x] = random.choice(candidates.tolist())

    return downsampled

def vegetation_map_to_grid(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)  # shape: (height, width, 3)

    height, width, _ = pixels.shape
    grid = np.full((height, width), EMPTY, dtype=np.uint8)

    for color, state in COLOR_TO_STATE.items():
        mask = np.all(pixels == color, axis=2)
        grid[mask] = state

    return downsample_grid_by_2(grid)
    # return grid

def load_fire_start(image_path: str, width: int, height: int) -> np.ndarray:
    fire_start = np.array(Image.open(image_path).convert("L"))
    fire_start = (fire_start == 255).astype(np.uint8)
    fire_start_resized = np.array(
        Image.fromarray(fire_start).resize((width, height), resample=Image.NEAREST)
    )
    return fire_start_resized