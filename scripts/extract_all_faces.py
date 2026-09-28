import cv2
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
videos_dir = os.path.join(base_dir, 'data', 'videos')

s1 = cv2.imread(os.path.join(assets_dir, 'reel_scene1_aloo.jpg'))
h, w = s1.shape[:2]

# Aloo is around y: 400..800, x: 50..450
# Let's crop Aloo's face:
aloo_face = s1[400:750, 50:450]
cv2.imwrite(os.path.join(videos_dir, 'aloo_face_s1.jpg'), aloo_face)

# Cauliflower face:
gobhi_face = s1[300:650, 450:750]
cv2.imwrite(os.path.join(videos_dir, 'gobhi_face_s1.jpg'), gobhi_face)

# Tamatar in scene 2:
s2 = cv2.imread(os.path.join(assets_dir, 'reel_scene2_tamatar.jpg'))
tamatar_face_s2 = s2[400:750, 250:700]
cv2.imwrite(os.path.join(videos_dir, 'tamatar_face_s2.jpg'), tamatar_face_s2)

# Scene 3:
s3 = cv2.imread(os.path.join(assets_dir, 'reel_scene3_argument.jpg'))
s3_aloo = s3[550:850, 50:450]
s3_tamatar = s3[600:900, 450:750]
s3_gobhi = s3[330:600, 450:750]
cv2.imwrite(os.path.join(videos_dir, 's3_aloo.jpg'), s3_aloo)
cv2.imwrite(os.path.join(videos_dir, 's3_tamatar.jpg'), s3_tamatar)
cv2.imwrite(os.path.join(videos_dir, 's3_gobhi.jpg'), s3_gobhi)

# Scene 4:
s4 = cv2.imread(os.path.join(assets_dir, 'reel_scene4_matar.jpg'))
s4_matar = s4[450:800, 250:650]
cv2.imwrite(os.path.join(videos_dir, 's4_matar.jpg'), s4_matar)
print("Faces extracted successfully!")
