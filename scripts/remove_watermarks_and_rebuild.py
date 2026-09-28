import cv2
import numpy as np
import os
import sys
import subprocess
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
videos_dir = os.path.join(base_dir, 'data', 'videos')
ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

characters = [
    {
        'name': 'aloo',
        'input_video': os.path.join(videos_dir, 'aloo_did_talking_live.mp4'),
        'orig_image': os.path.join(assets_dir, 'char_aloo.jpg'),
        'clean_video': os.path.join(videos_dir, 'aloo_clean.mp4')
    },
    {
        'name': 'tamatar',
        'input_video': os.path.join(videos_dir, 'tamatar_did_talking_live.mp4'),
        'orig_image': os.path.join(assets_dir, 'char_tamatar.jpg'),
        'clean_video': os.path.join(videos_dir, 'tamatar_clean.mp4')
    },
    {
        'name': 'gobhi',
        'input_video': os.path.join(videos_dir, 'gobhi_did_talking_live.mp4'),
        'orig_image': os.path.join(assets_dir, 'char_gobhi.jpg'),
        'clean_video': os.path.join(videos_dir, 'gobhi_clean.mp4')
    }
]

def clean_video(char_info):
    in_vid = char_info['input_video']
    orig_img_path = char_info['orig_image']
    out_vid = char_info['clean_video']
    
    print(f"\n==========================================")
    print(f"[*] Processing Character: {char_info['name'].upper()}")
    print(f"Input: {in_vid}")
    print(f"Output: {out_vid}")
    print(f"==========================================")

    if not os.path.exists(in_vid):
        print(f"Error: {in_vid} does not exist!")
        return

    # Extract audio stream first
    temp_audio = os.path.join(videos_dir, f"temp_audio_{char_info['name']}.aac")
    cmd_audio = f'"{ffmpeg_bin}" -y -i "{in_vid}" -vn -c:a copy "{temp_audio}"'
    subprocess.run(cmd_audio, shell=True, check=True)

    # Open video
    cap = cv2.VideoCapture(in_vid)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Prepare pristine background
    orig_bgr = cv2.imread(orig_img_path)
    if orig_bgr.shape[0] != height or orig_bgr.shape[1] != width:
        orig_bgr = cv2.resize(orig_bgr, (width, height), interpolation=cv2.INTER_LANCZOS4)

    # Compute static background mask
    gray_orig = cv2.cvtColor(orig_bgr, cv2.COLOR_BGR2GRAY)
    char_base_mask = (gray_orig < 232).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    char_base_mask = cv2.morphologyEx(char_base_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(char_base_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        char_contour_mask = np.zeros_like(char_base_mask)
        cv2.drawContours(char_contour_mask, [largest], -1, 255, -1)
    else:
        char_contour_mask = char_base_mask

    # Soft boundary feathering
    feather_alpha = cv2.GaussianBlur(char_contour_mask, (9, 9), 0).astype(np.float32) / 255.0
    feather_alpha = np.expand_dims(feather_alpha, axis=2)

    # Temporary raw processed video
    temp_raw_vid = os.path.join(videos_dir, f"temp_raw_{char_info['name']}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(temp_raw_vid, fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % 30 == 0 or frame_idx == total_frames:
            print(f"[{char_info['name']}] Cleaning frame {frame_idx}/{total_frames} ({int(frame_idx/total_frames*100)}%)...")

        # 1. Clean face skin luminance
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
        y_smooth = cv2.bilateralFilter(y, d=5, sigmaColor=15, sigmaSpace=15)
        yuv_clean = cv2.merge([y_smooth, u, v])
        frame_skin_clean = cv2.cvtColor(yuv_clean, cv2.COLOR_YUV2BGR)

        # 2. Composite character onto pristine 100% watermark-free studio background
        frame_clean = (frame_skin_clean * feather_alpha + orig_bgr * (1.0 - feather_alpha)).astype(np.uint8)

        writer.write(frame_clean)

    cap.release()
    writer.release()

    # Merge cleaned video with audio using FFmpeg with high quality encoding
    print(f"[{char_info['name']}] Muxing clean video with original audio...")
    cmd_mux = f'"{ffmpeg_bin}" -y -i "{temp_raw_vid}" -i "{temp_audio}" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart "{out_vid}"'
    subprocess.run(cmd_mux, shell=True, check=True)

    # Clean temporary files
    if os.path.exists(temp_raw_vid): os.remove(temp_raw_vid)
    if os.path.exists(temp_audio): os.remove(temp_audio)
    print(f"[SUCCESS] Finished cleaning: {out_vid}")

def rebuild_final_story():
    print(f"\n==========================================")
    print(f"[*] Rebuilding Final Multi-Character Story (No Watermarks)")
    print(f"==========================================")

    aloo_clean = characters[0]['clean_video']
    tamatar_clean = characters[1]['clean_video']
    gobhi_clean = characters[2]['clean_video']
    final_out = os.path.join(videos_dir, 'final_aloo_tamatar_gobhi_story.mp4')

    filter_cmd = f'"{ffmpeg_bin}" -y ' \
        f'-i "{aloo_clean}" ' \
        f'-i "{tamatar_clean}" ' \
        f'-i "{gobhi_clean}" ' \
        f'-filter_complex "' \
        f'[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];' \
        f'[1:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];' \
        f'[2:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2];' \
        f'[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]" ' \
        f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -ar 44100 -movflags +faststart "{final_out}"'

    subprocess.run(filter_cmd, shell=True, check=True)
    print(f"\n[DONE] Final watermark-free story video rebuilt at: {final_out} ({os.path.getsize(final_out)} bytes)")

def main():
    for char in characters:
        clean_video(char)
    rebuild_final_story()

if __name__ == '__main__':
    main()
