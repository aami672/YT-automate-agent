import cv2
import numpy as np
import os

assets_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'assets')
videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')

orig_path = os.path.join(assets_dir, 'char_aloo.jpg')
frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
clean_test_out = os.path.join(videos_dir, 'sample_cleaned_aloo.jpg')
mask_out = os.path.join(videos_dir, 'watermark_mask.jpg')

orig = cv2.imread(orig_path)
frame = cv2.imread(frame_path)

if orig.shape != frame.shape:
    orig = cv2.resize(orig, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LANCZOS4)

# Calculate difference
diff = cv2.absdiff(frame, orig)
gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

# Threshold to get watermark mask
_, mask = cv2.threshold(gray_diff, 8, 255, cv2.THRESH_BINARY)

# Dilate mask slightly to cover watermark boundaries
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
dilated_mask = cv2.dilate(mask, kernel, iterations=1)

cv2.imwrite(mask_out, dilated_mask)
print(f"Mask written to {mask_out}, non-zero pixels: {np.count_nonzero(dilated_mask)}")

# Method 1: Inpaint using Fast Marching (Telea)
cleaned_telea = cv2.inpaint(frame, dilated_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

# Method 2: In the background regions where motion is near 0, restore directly from pristine original!
# Where the video frame hasn't moved relative to original (background), use pristine original.
# Where it has moved (mouth/eyes/face), use inpainting on the watermark pixels.
# Segment character vs background:
bg_mask = (orig > 230).all(axis=2) # white/off-white background
cleaned_hybrid = cleaned_telea.copy()
cleaned_hybrid[bg_mask] = orig[bg_mask]

cv2.imwrite(clean_test_out, cleaned_hybrid)
print(f"Cleaned frame written to {clean_test_out}")
