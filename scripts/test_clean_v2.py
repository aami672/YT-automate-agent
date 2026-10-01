import cv2
import numpy as np
import os

videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
assets_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'assets')

frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
orig_path = os.path.join(assets_dir, 'char_aloo.jpg')

frame = cv2.imread(frame_path)
orig = cv2.imread(orig_path)
if orig.shape != frame.shape:
    orig = cv2.resize(orig, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LANCZOS4)

# 1. Precise character mask from orig:
# In orig, background is pure studio white/gray gradient.
gray_orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
# Anything with brightness > 235 is pure background
char_mask = (gray_orig < 230).astype(np.uint8) * 255

# Morphological clean to get smooth outer boundary
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
char_mask = cv2.morphologyEx(char_mask, cv2.MORPH_CLOSE, kernel)

# Keep largest connected component (the potato)
contours, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
clean_contour_mask = np.zeros_like(char_mask)
if contours:
    largest = max(contours, key=cv2.contourArea)
    cv2.drawContours(clean_contour_mask, [largest], -1, 255, -1)

# 2. Filter out watermark on the character face:
# Watermark is high frequency on luminance channel
yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
y, u, v = cv2.split(yuv)

# Bilateral filter on Y channel preserves sharp edges (eyes, eyebrows, mouth) while smoothing faint watermark text
y_filtered = cv2.bilateralFilter(y, d=7, sigmaColor=25, sigmaSpace=25)

# Fast morphological blackhat / tophat to detect thin watermark stroke artifacts
kernel_wm = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
tophat = cv2.morphologyEx(y, cv2.MORPH_TOPHAT, kernel_wm)
blackhat = cv2.morphologyEx(y, cv2.MORPH_BLACKHAT, kernel_wm)
wm_stroke_mask = ((tophat > 8) | (blackhat > 8)).astype(np.uint8) * 255

# Apply selective median filter only where watermark strokes are detected on skin
y_cleaned = y.copy()
y_median = cv2.medianBlur(y, 3)
y_cleaned[wm_stroke_mask > 0] = y_median[wm_stroke_mask > 0]

# Blend back
yuv_cleaned = cv2.merge([y_cleaned, u, v])
frame_skin_cleaned = cv2.cvtColor(yuv_cleaned, cv2.COLOR_YUV2BGR)

# Soft feathering on character boundary
alpha = cv2.GaussianBlur(clean_contour_mask, (5, 5), 0).astype(np.float32) / 255.0
alpha = np.expand_dims(alpha, axis=2)

# Final composite
final = (frame_skin_cleaned * alpha + orig * (1.0 - alpha)).astype(np.uint8)

out_path = os.path.join(videos_dir, 'sample_cleaned_v2.jpg')
cv2.imwrite(out_path, final)
print("Saved clean v2 to:", out_path)
