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

# Build a clean character silhouette mask from orig and frame
# In both images, background is white (RGB > 225)
gray_orig = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Character mask: where original is not pure white background
# Dilate slightly to ensure full character boundary is captured
is_char = (gray_orig < 235).astype(np.uint8) * 255

# Fill holes
contours, _ = cv2.findContours(is_char, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
char_mask = np.zeros_like(is_char)
if contours:
    largest = max(contours, key=cv2.contourArea)
    cv2.drawContours(char_mask, [largest], -1, 255, -1)

# Feather the edge with 5px blur for seamless alpha blending
alpha = cv2.GaussianBlur(char_mask, (7, 7), 0).astype(np.float32) / 255.0
alpha = np.expand_dims(alpha, axis=2)

# Composite: Take animated video character, and clean pristine original background
cleaned = (frame * alpha + orig * (1.0 - alpha)).astype(np.uint8)

out_path = os.path.join(videos_dir, 'sample_cleaned_bg_composite.jpg')
cv2.imwrite(out_path, cleaned)
print("Saved clean composite to:", out_path)
