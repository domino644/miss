from PIL import Image
import numpy as np
import random

EMPTY = 0
TREE = 1
IGNITING = 2
BURNING = 3
SMOLDERING = 4
BURNED = 5
WATER = 6

COLOR_TO_STATE = {
    (0, 160, 0): TREE,        # #00a000
    (128, 128, 128): WATER,   # #808080
    (192, 192, 192): WATER,   # #c0c0c0
    (0, 0, 255): WATER,       # #0000ff
}

COLORS = {
    EMPTY: (161, 117, 73),
    TREE: (34, 105, 34),
    IGNITING: (232, 144, 86),
    BURNING: (255, 248, 141),
    SMOLDERING: (112, 14, 14),
    BURNED: (67,67,67),
    WATER: (9,55,100),
}

PIXEL_RATIOS = {
    'yacutz': (73, 3000),
    'rhodos': (33, 800)
}

def adjust_resolution(grid: np.ndarray, fire_name: str, m_per_pixel: int) -> np.ndarray:
    old_height, old_width = grid.shape

    pixel_ratio = PIXEL_RATIOS[fire_name]

    height_in_m = old_height * (pixel_ratio[1] / pixel_ratio[0])
    width_in_m = old_width * (pixel_ratio[1] / pixel_ratio[0])

    new_height = round(height_in_m / m_per_pixel)
    new_width = round(width_in_m / m_per_pixel)

    scale_y = old_height / new_height
    scale_x = old_width / new_width

    adjusted = np.zeros((new_height, new_width), dtype=np.uint8)

    for y in range(new_height):
        for x in range(new_width):
            y0 = int(scale_y * y)
            y1 = int(scale_y * (y + 1))
            x0 = int(scale_x * x)
            x1 = int(scale_x * (x + 1))

            block = grid[y0:y1, x0:x1].flatten()

            # Priorytet: jeśli gdziekolwiek jest TREE, wynik = TREE
            # if np.any(block == TREE):
            #     downsampled[y, x] = TREE
            #     continue

            if np.any(block == WATER):
                adjusted[y, x] = WATER
                continue

            values, counts = np.unique(block, return_counts=True)
            max_count = counts.max()
            candidates = values[counts == max_count]

            # Jeśli remis, losowo
            adjusted[y, x] = random.choice(candidates.tolist())

    return adjusted

def downsample_grid_by_n(grid: np.ndarray, n: int) -> np.ndarray:
    old_height, old_width = grid.shape

    new_height = old_height // n
    new_width = old_width // n

    downsampled = np.zeros((new_height, new_width), dtype=np.uint8)

    for y in range(new_height):
        for x in range(new_width):
            block = grid[n*y:n*y+n, n*x:n*x+n].flatten()

            # Priorytet: jeśli gdziekolwiek jest TREE, wynik = TREE
            # if np.any(block == TREE):
            #     downsampled[y, x] = TREE
            #     continue

            if np.any(block == WATER):
                downsampled[y, x] = WATER
                continue

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

    return adjust_resolution(grid, 'yacutz', 120)
    # return grid

def load_fire_start(image_path: str, width: int, height: int) -> np.ndarray:
    fire_start = np.array(Image.open(image_path).convert("L"))
    fire_start = (fire_start == 255).astype(np.uint8)
    fire_start_resized = np.array(
        Image.fromarray(fire_start).resize((width, height), resample=Image.NEAREST)
    )
    return fire_start_resized

def save_grid_as_png(grid: np.ndarray, output_path: str):
    height, width = grid.shape
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    for state, color in COLORS.items():
        img_array[grid == state] = color

    img = Image.fromarray(img_array, mode="RGB")
    img.save(output_path)

def empty_mask_iou(sim_grid: np.ndarray, sat_grid: np.ndarray, empty=0) -> float:
    if sim_grid.shape != sat_grid.shape:
        raise ValueError("sim_grid and sat_grid must have the same shape")

    sim_empty = sim_grid == empty
    sat_empty = sat_grid == empty

    intersection = np.sum(sim_empty & sat_empty)
    union = np.sum(sim_empty | sat_empty)

    if union == 0:
        return 1.0

    return float(intersection / union)