import cv2
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
videos_dir = os.path.join(base_dir, 'data', 'videos')

# 1. Scene 1 - Aloo mouth
s1 = cv2.imread(os.path.join(assets_dir, 'reel_scene1_aloo.jpg'))
crop1 = s1[520:600, 260:380] # Aloo mouth
cv2.imwrite(os.path.join(videos_dir, 'test_mouth_s1.jpg'), crop1)

# 2. Scene 2 - Tamatar mouth
s2 = cv2.imread(os.path.join(assets_dir, 'reel_scene2_tamatar.jpg'))
crop2 = s2[520:600, 460:600] # Tamatar mouth
cv2.imwrite(os.path.join(videos_dir, 'test_mouth_s2.jpg'), crop2)

# 3. Scene 3 - Gobhi & Aloo mouth
s3 = cv2.imread(os.path.join(assets_dir, 'reel_scene3_argument.jpg'))
crop3_aloo = s3[670:760, 310:410] # Aloo mouth in arg
crop3_gobhi = s3[440:510, 660:760] # Gobhi mouth
cv2.imwrite(os.path.join(videos_dir, 'test_mouth_s3_aloo.jpg'), crop3_aloo)
cv2.imwrite(os.path.join(videos_dir, 'test_mouth_s3_gobhi.jpg'), crop3_gobhi)

# 4. Scene 4 - Matar mouth
s4 = cv2.imread(os.path.join(assets_dir, 'reel_scene4_matar.jpg'))
crop4_matar = s4[360:440, 440:580] # Matar mouth
cv2.imwrite(os.path.join(videos_dir, 'test_mouth_s4_matar.jpg'), crop4_matar)

print("Mouth crops saved for verification!")
