import cv2
import numpy as np
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')

scenes = [
    {'name': 'scene1', 'path': os.path.join(assets_dir, 'reel_scene1_aloo.jpg')},
    {'name': 'scene2', 'path': os.path.join(assets_dir, 'reel_scene2_tamatar.jpg')},
    {'name': 'scene3', 'path': os.path.join(assets_dir, 'reel_scene3_argument.jpg')},
    {'name': 'scene4', 'path': os.path.join(assets_dir, 'reel_scene4_matar.jpg')},
]

for s in scenes:
    img = cv2.imread(s['path'])
    if img is not None:
        print(f"Loaded {s['name']}: shape={img.shape}")
