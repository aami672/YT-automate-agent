import cv2
import numpy as np
import os

ffmpeg = os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')
videos_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'videos')
vid_path = os.path.join(videos_dir, 'aloo_did_talking_live.mp4')

cap = cv2.VideoCapture(vid_path)
ret, f0 = cap.read()
for _ in range(50):
    ret, f50 = cap.read()
cap.release()

diff = cv2.absdiff(f0[0:200, 0:200], f50[0:200, 0:200])
print("Max diff in top-left watermark background between frames:", np.max(diff))
