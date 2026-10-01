import cv2
import numpy as np
import os
from rembg import remove
from PIL import Image

videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
assets_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'assets')

frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
orig_path = os.path.join(assets_dir, 'char_aloo.jpg')

input_img = Image.open(frame_path)
orig_img = Image.open(orig_path).resize(input_img.size, Image.Resampling.LANCZOS)

# Remove background from animated frame (gives transparent RGBA character)
output_rgba = remove(input_img)

# Composite RGBA character onto pristine original background
clean_bg = orig_img.convert('RGBA')
final_img = Image.alpha_composite(clean_bg, output_rgba)

out_path = os.path.join(videos_dir, 'sample_rembg_composite.png')
final_img.convert('RGB').save(out_path, quality=95)
print("Saved rembg composite to:", out_path)
