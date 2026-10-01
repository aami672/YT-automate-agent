import cv2
import numpy as np
import os

videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
frame = cv2.imread(frame_path)

# 1. Detect character mask (the potato / character in the center)
# The background is very light (value > 200) and character is in the center
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Find watermark pattern in the background:
# Background without watermark should be smooth gradient
bg_estimate = cv2.GaussianBlur(gray, (51, 51), 0)
diff_bg = cv2.absdiff(gray, bg_estimate)

# High-pass watermark strokes:
# The D-ID text has thin edges with contrast difference of ~15-30 against local background
_, wm_mask = cv2.threshold(diff_bg, 7, 255, cv2.THRESH_BINARY)

# Dilate watermark mask just enough to cover the thin letters (1-2 pixels)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
wm_mask_dilated = cv2.dilate(wm_mask, kernel, iterations=1)

# Inpaint ONLY the thin watermark lines using Navier-Stokes / Telea with small radius
cleaned_inpaint = cv2.inpaint(frame, wm_mask_dilated, inpaintRadius=2, flags=cv2.INPAINT_TELEA)

# Segment background: where original frame is close to pure white/light gray
# Create a smooth studio background to replace the background entirely:
h, w = frame.shape[:2]
clean_bg = np.zeros((h, w, 3), dtype=np.uint8)
for y in range(h):
    # subtle top-to-bottom studio lighting gradient matching original
    val = int(248 - (y / h) * 15)
    clean_bg[y, :] = [val, val, val]

# Character segmentation mask
# We can use grabcut or threshold + morphological clean to get character body
_, binary_bg = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)
# The character is dark compared to white bg
char_mask = (gray < 215).astype(np.uint8) * 255
# Fill holes inside character
contours, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    char_contour_mask = np.zeros_like(char_mask)
    cv2.drawContours(char_contour_mask, [largest_contour], -1, 255, -1)
    # Smooth edges with Gaussian
    char_alpha = cv2.GaussianBlur(char_contour_mask, (15, 15), 0).astype(np.float32) / 255.0
    char_alpha = np.expand_dims(char_alpha, axis=2)

    # Composite cleaned character on pure clean studio background
    final_cleaned = (cleaned_inpaint * char_alpha + clean_bg * (1.0 - char_alpha)).astype(np.uint8)
else:
    final_cleaned = cleaned_inpaint

out_path = os.path.join(videos_dir, 'sample_cleaned_perfect.jpg')
cv2.imwrite(out_path, final_cleaned)
print(f"Generated clean frame to: {out_path}")
