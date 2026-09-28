import cv2
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
matar_scene = os.path.join(assets_dir, 'reel_scene4_matar.jpg')
matar_out = os.path.join(assets_dir, 'char_matar.jpg')

img = cv2.imread(matar_scene)
if img is not None:
    # Matar character is in the center foreground
    # Crop around the green pea character
    h, w = img.shape[:2]
    # Crop around x: 200..600, y: 450..950
    crop = img[int(h*0.42):int(h*0.80), int(w*0.25):int(w*0.75)]
    crop_sq = cv2.resize(crop, (1024, 1024), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(matar_out, crop_sq)
    print(f"✅ Created Matar avatar image: {matar_out}")
