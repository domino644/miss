# from PIL import Image
# import numpy as np

# MAP_PATH = r"C:\Users\Lukasz\Documents\GitHub\miss\data\yacutz\vegetation_after.png"
# MASK_PATH = r"C:\Users\Lukasz\Documents\GitHub\miss\data\yacutz\river_binary_mask.npy"
# OUTPUT_PATH = r"C:\Users\Lukasz\Documents\GitHub\miss\data\yacutz\vegetation_river_after.png"

# # wczytanie mapy
# map_img = Image.open(MAP_PATH).convert("RGB")
# map_arr = np.array(map_img)

# # wczytanie maski 0/1 z pliku .npy
# mask_arr = np.load(MASK_PATH)

# # zamiana na True/False
# river_mask = mask_arr > 0

# # kontrola wymiarów
# if river_mask.shape != map_arr.shape[:2]:
#     raise ValueError(
#         f"Maska ma rozmiar {river_mask.shape}, a mapa ma rozmiar {map_arr.shape[:2]}"
#     )

# # ustawienie rzeki na #0000ff
# map_arr[river_mask] = [0, 0, 255]

# # zapis wyniku
# Image.fromarray(map_arr).save(OUTPUT_PATH)