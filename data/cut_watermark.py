from PIL import Image

img = Image.open(r"yacutz-uncut\vegetation_after_uncut.png")

width, height = img.size

top_cut = 66

cropped = img.crop((0, top_cut, width, height))
cropped.save(r"yacutz\vegetation_after.png")