import cv2
import numpy as np
import os
from PIL import Image

videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
assets_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'assets')

frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
orig_path = os.path.join(assets_dir, 'char_aloo.jpg')

frame = cv2.imread(frame_path).astype(np.float32)
orig = cv2.imread(orig_path).astype(np.float32)
if orig.shape != frame.shape:
    orig = cv2.resize(orig, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LANCZOS4)

# 1. Compute watermark intensity delta from the top-left white background region
# In top-left (y: 0..150, x: 0..200), pristine bg is ~250
# Watermark letters are ~215-225 (difference of ~25-35)
bg_region_wm = frame[0:200, 0:200]
bg_region_orig = orig[0:200, 0:200]
bg_diff = bg_region_orig - bg_region_wm # positive values where watermark dimmed the pixels

# We can estimate the full-frame watermark pattern by repeating the lattice grid or using frequency notch / subtraction:
# Let's subtract the low frequencies to isolate the high-frequency watermark pattern
gray_frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
gray_orig = cv2.cvtColor(orig.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)

# High-pass filter to get texture/watermark layer
blur_frame = cv2.GaussianBlur(gray_frame, (15, 15), 0)
hp_frame = gray_frame - blur_frame

# High-pass of original
blur_orig = cv2.GaussianBlur(gray_orig, (15, 15), 0)
hp_orig = gray_orig - blur_orig

# The watermark signal is present in hp_frame but not hp_orig
wm_pattern = cv2.GaussianBlur(np.maximum(0, hp_orig - hp_frame), (3, 3), 0)

# Apply subtle brightness compensation where watermark darkened the image
cleaned_frame = frame.copy()
for c in range(3):
    cleaned_frame[:, :, c] = np.clip(cleaned_frame[:, :, c] + wm_pattern * 0.8, 0, 255)

# Load rembg RGBA image from previous step to composite with clean background
rgba_path = os.path.join(videos_dir, 'sample_rembg_composite.png')
# Also run bilateral filter on skin region
yuv = cv2.cvtColor(cleaned_frame.astype(np.uint8), cv2.COLOR_BGR2YUV)
y, u, v = cv2.split(yuv)
y_smooth = cv2.bilateralFilter(y, d=5, sigmaColor=15, sigmaSpace=15)
yuv_clean = cv2.merge([y_smooth, u, v])
final_face_clean = cv2.cvtColor(yuv_clean, cv2.COLOR_YUV2BGR)

# Composite clean face onto clean rembg background
rembg_res = cv2.imread(rgba_path)
out_path = os.path.join(videos_dir, 'sample_perfect_nowm.jpg')
cv2.imwrite(out_path, final_face_clean)
print("Saved clean test to:", out_path)
