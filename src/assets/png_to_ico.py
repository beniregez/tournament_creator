import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(BASE_DIR, "icon.png")

output_ico = os.path.join(BASE_DIR, "icon.ico")

img = Image.open(img_path)
img.save(output_ico, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

print(f"✅ ICO created: {output_ico}")