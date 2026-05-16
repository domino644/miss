from PIL import Image
import numpy as np

img = Image.open("vegetation_after.png").convert("RGB")
arr = np.array(img)

# średnia jasność każdego wiersza
gray = arr.mean(axis=2)
row_brightness = gray.mean(axis=1)

# różnice jasności między kolejnymi wierszami
diff = np.abs(np.diff(row_brightness))

# największy skok jasności blisko góry = granica paska
search_limit = 300
border_y = np.argmax(diff[:search_limit]) + 1

print("Granica paska:", border_y, "px")