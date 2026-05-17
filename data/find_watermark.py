from PIL import Image
import numpy as np

img = Image.open("yacutz/vegetation_after.png").convert("RGB")
width, height = img.size
print(width, height)
arr = np.zeros((height, width), dtype=np.uint8)

arr[390:410, 1190:1210] = 1
arr[780:800, 1505:1525] = 1
arr[930:950, 1645:1665] = 1
arr[1120:1140, 720:740] = 1

img_array = (arr * 255).astype(np.uint8)
img_to_save = Image.fromarray(img_array, mode="L")
img_to_save.save('fire_start_grid.png')

# # średnia jasność każdego wiersza
# gray = arr.mean(axis=2)
# row_brightness = gray.mean(axis=1)

# # różnice jasności między kolejnymi wierszami
# diff = np.abs(np.diff(row_brightness))

# # największy skok jasności blisko góry = granica paska
# search_limit = 300
# border_y = np.argmax(diff[:search_limit]) + 1

# print("Granica paska:", border_y, "px")