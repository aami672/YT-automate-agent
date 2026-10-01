import cv2
import numpy as np
import os

videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
frame_path = os.path.join(videos_dir, 'sample_aloo_frame.jpg')
frame = cv2.imread(frame_path)

# Let's inspect a crop of the watermark in the top-left background:
crop = frame[0:150, 0:250]
cv2.imwrite(os.path.join(videos_dir, 'watermark_crop.jpg'), crop)

# Let's check the pixel values:
# Background is around [245, 246, 248]
# Watermark letters are around [215, 218, 222]
# Difference is around 25-30 units darker
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
print("Background max/median:", np.median(gray[0:100, 0:100]))
print("Watermark min in bg:", np.min(gray[0:100, 0:100]))
