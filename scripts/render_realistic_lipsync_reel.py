import cv2
import numpy as np
import os
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
videos_dir = os.path.join(base_dir, 'data', 'videos')
audio_dir = os.path.join(base_dir, 'data', 'audio')
ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

def get_audio_envelope(wav_path, fps=30):
    # Extract audio samples using ffmpeg
    raw_pcm = wav_path + ".raw"
    cmd = f'"{ffmpeg_bin}" -y -i "{wav_path}" -f s16le -ac 1 -ar 44100 "{raw_pcm}"'
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    with open(raw_pcm, 'rb') as f:
        data = np.frombuffer(f.read(), dtype=np.int16)
    if os.path.exists(raw_pcm):
        os.remove(raw_pcm)

    sample_rate = 44100
    samples_per_frame = int(sample_rate / fps)
    total_frames = int(len(data) / samples_per_frame)
    
    envelope = []
    for i in range(total_frames):
        chunk = data[i*samples_per_frame:(i+1)*samples_per_frame].astype(np.float32)
        rms = np.sqrt(np.mean(chunk**2)) / 32768.0
        envelope.append(rms)
        
    envelope = np.array(envelope)
    # Normalize envelope to 0..1 range with noise floor
    if np.max(envelope) > 0.01:
        envelope = (envelope - 0.01) / (np.max(envelope) - 0.01)
        envelope = np.clip(envelope, 0.0, 1.0)
    else:
        envelope = np.zeros_like(envelope)
        
    # Smooth envelope slightly for natural lip elasticity
    kernel = np.ones(3) / 3.0
    envelope = np.convolve(envelope, kernel, mode='same')
    return np.clip(envelope, 0.0, 1.0)

def apply_mouth_lipsync(img, mouth_center, mouth_radius, open_amount, stretch_x=1.0):
    """
    Deforms the mouth region using smooth radial warping to simulate natural speech articulation.
    open_amount: 0.0 (closed) to 1.0 (fully open)
    """
    if open_amount < 0.05:
        return img.copy()

    h, w = img.shape[:2]
    cx, cy = mouth_center
    rx, ry = mouth_radius

    # Bounding box around mouth
    x1 = max(0, int(cx - rx * 1.5))
    x2 = min(w, int(cx + rx * 1.5))
    y1 = max(0, int(cy - ry * 1.8))
    y2 = min(h, int(cy + ry * 1.8))

    roi = img[y1:y2, x1:x2].copy()
    rh, rw = roi.shape[:2]
    rcx, rcy = cx - x1, cy - y1

    # Create meshgrid
    y_coords, x_coords = np.mgrid[0:rh, 0:rw].astype(np.float32)

    # Compute normalized distance from mouth center
    dx = (x_coords - rcx) / float(rx)
    dy = (y_coords - rcy) / float(ry)
    dist = dx**2 + dy**2
    mask = np.exp(-dist * 1.8) # Gaussian weight

    # Vertical jaw opening displacement: lower lip moves down, upper lip moves slightly up
    vert_disp = np.where(y_coords > rcy, 1.0, -0.3) * (open_amount * ry * 0.45) * mask
    horiz_disp = np.sign(x_coords - rcx) * (open_amount * (stretch_x - 1.0) * rx * 0.2) * mask

    map_x = (x_coords - horiz_disp).astype(np.float32)
    map_y = (y_coords - vert_disp).astype(np.float32)

    warped_roi = cv2.remap(roi, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # Blend inner oral cavity / teeth shadow when mouth is open
    if open_amount > 0.35:
        inner_mask = np.exp(-(dx**2 * 1.5 + (dy * 1.2)**2) * 4.0)
        inner_mask = np.expand_dims(inner_mask, axis=2)
        # Subtle dark oral depth with slight pink/reddish tone
        oral_color = np.array([30, 20, 60], dtype=np.uint8) # BGR
        intensity = (open_amount - 0.35) * 0.8
        warped_roi = (warped_roi * (1.0 - inner_mask * intensity) + oral_color * (inner_mask * intensity)).astype(np.uint8)

    res = img.copy()
    res[y1:y2, x1:x2] = warped_roi
    return res

def render_scene_with_lipsync(scene_config):
    s_id = scene_config['id']
    img_path = scene_config['image']
    audio_path = scene_config['audio']
    out_video = scene_config['output']

    print(f"\n[*] Rendering Lip-Sync for Scene {s_id}: {scene_config['title']}...")
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Image not found: {img_path}")

    # Scale base image
    target_w, target_h = 720, 1280
    fps = 30
    envelope = get_audio_envelope(audio_path, fps=fps)
    total_frames = len(envelope)
    print(f"Total frames: {total_frames} ({total_frames/fps:.2f}s)")

    temp_raw = os.path.join(videos_dir, f"temp_lipsync_{s_id}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(temp_raw, fourcc, fps, (target_w, target_h))

    # Base image scaled for camera zoom margin
    base_w, base_h = 900, 1600
    img_scaled = cv2.resize(img, (base_w, base_h), interpolation=cv2.INTER_LANCZOS4)
    scale_factor_x = base_w / float(img.shape[1])
    scale_factor_y = base_h / float(img.shape[0])

    for i in range(total_frames):
        t = i / float(total_frames)
        audio_vol = envelope[i]

        # 1. Compute dynamic camera zoom/pan
        if scene_config['zoom'] == 'zoom_in':
            scale = 1.0 + 0.12 * t
            cx, cy = base_w / 2.0, base_h / 2.0
        elif scene_config['zoom'] == 'zoom_out':
            scale = 1.15 - 0.12 * t
            cx, cy = base_w / 2.0, base_h / 2.0
        elif scene_config['zoom'] == 'pan':
            scale = 1.05 + 0.05 * np.sin(t * np.pi)
            cx = base_w / 2.0 + (t - 0.5) * 35.0
            cy = base_h / 2.0
        else:
            scale = 1.0 + 0.15 * (t ** 0.8)
            cx = base_w / 2.0
            cy = base_h / 2.0 + 30.0 * (1.0 - t)

        # 2. Apply Lip-sync deformations on character mouth(s)
        frame_art = img_scaled.copy()

        for char in scene_config['characters']:
            # Check if this character is currently speaking based on time window
            if char['time_start'] <= t <= char['time_end']:
                char_vol = audio_vol * char.get('gain', 1.0)
                mx = int(char['mouth_x'] * scale_factor_x)
                my = int(char['mouth_y'] * scale_factor_y)
                rx = int(char['mouth_rx'] * scale_factor_x)
                ry = int(char['mouth_ry'] * scale_factor_y)
                frame_art = apply_mouth_lipsync(frame_art, (mx, my), (rx, ry), char_vol, stretch_x=char.get('stretch', 1.1))

        # 3. Crop to target 720x1280 viewport
        crop_w = int(base_w / scale)
        crop_h = int(base_h / scale)
        x1 = max(0, min(base_w - crop_w, int(cx - crop_w / 2)))
        y1 = max(0, min(base_h - crop_h, int(cy - crop_h / 2)))

        crop = frame_art[y1:y1+crop_h, x1:x1+crop_w]
        frame = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        writer.write(frame)

    writer.release()

    # Mux with original multi-voice scene audio
    cmd_mux = f'"{ffmpeg_bin}" -y -i "{temp_raw}" -i "{audio_path}" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart -shortest "{out_video}"'
    subprocess.run(cmd_mux, shell=True, check=True)
    if os.path.exists(temp_raw): os.remove(temp_raw)
    print(f"[Done] Scene {s_id} rendered with lip-sync: {out_video}")

def main():
    scene_configs = [
        {
            'id': 1,
            'title': 'The Romantic Entry (Aloo)',
            'image': os.path.join(assets_dir, 'reel_scene1_aloo.jpg'),
            'audio': os.path.join(audio_dir, 'scene_1_audio.wav'),
            'output': os.path.join(videos_dir, 'scene_1_lipsync.mp4'),
            'zoom': 'zoom_in',
            'characters': [
                {
                    'name': 'aloo',
                    'mouth_x': 325,
                    'mouth_y': 560,
                    'mouth_rx': 45,
                    'mouth_ry': 25,
                    'time_start': 0.0,
                    'time_end': 1.0,
                    'gain': 1.2
                }
            ]
        },
        {
            'id': 2,
            'title': 'The Villain Entry (Tamatar)',
            'image': os.path.join(assets_dir, 'reel_scene2_tamatar.jpg'),
            'audio': os.path.join(audio_dir, 'scene_2_audio.wav'),
            'output': os.path.join(videos_dir, 'scene_2_lipsync.mp4'),
            'zoom': 'zoom_out',
            'characters': [
                {
                    'name': 'tamatar',
                    'mouth_x': 530,
                    'mouth_y': 550,
                    'mouth_rx': 55,
                    'mouth_ry': 28,
                    'time_start': 0.0,
                    'time_end': 1.0,
                    'gain': 1.3
                }
            ]
        },
        {
            'id': 3,
            'title': "The Argument & Gobhi's Choice",
            'image': os.path.join(assets_dir, 'reel_scene3_argument.jpg'),
            'audio': os.path.join(audio_dir, 'scene_3_audio.wav'),
            'output': os.path.join(videos_dir, 'scene_3_lipsync.mp4'),
            'zoom': 'pan',
            'characters': [
                {
                    'name': 'aloo',
                    'mouth_x': 360,
                    'mouth_y': 710,
                    'mouth_rx': 40,
                    'mouth_ry': 25,
                    'time_start': 0.0,
                    'time_end': 0.58, # Aloo speaks first half
                    'gain': 1.2
                },
                {
                    'name': 'gobhi',
                    'mouth_x': 710,
                    'mouth_y': 475,
                    'mouth_rx': 35,
                    'mouth_ry': 22,
                    'time_start': 0.55,
                    'time_end': 1.0, # Gobhi speaks second half
                    'gain': 1.2
                }
            ]
        },
        {
            'id': 4,
            'title': 'The Twist Ending (Matar)',
            'image': os.path.join(assets_dir, 'reel_scene4_matar.jpg'),
            'audio': os.path.join(audio_dir, 'scene_4_audio.wav'),
            'output': os.path.join(videos_dir, 'scene_4_lipsync.mp4'),
            'zoom': 'punch_in',
            'characters': [
                {
                    'name': 'matar',
                    'mouth_x': 530,
                    'mouth_y': 580,
                    'mouth_rx': 40,
                    'mouth_ry': 24,
                    'time_start': 0.0,
                    'time_end': 0.70, # Matar speaks
                    'gain': 1.3
                }
            ]
        }
    ]

    for sc in scene_configs:
        render_scene_with_lipsync(sc)

    print("\n==========================================")
    print("🎬 Assembling Final Master Lip-Sync 3D Pixar Reel")
    print("==========================================")

    final_lipsync_reel = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_lipsync_reel.mp4')
    final_std_reel = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4')
    final_agnes_reel = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_agnes_animated.mp4')
    scratch_output = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"

    in_args = " ".join([f'-i "{sc["output"]}"' for sc in scene_configs])
    filter_complex = "".join([f'[{i}:v][{i}:a]' for i in range(len(scene_configs))]) + f'concat=n={len(scene_configs)}:v=1:a=1[v][a]'
    
    cmd_concat = f'"{ffmpeg_bin}" -y {in_args} -filter_complex "{filter_complex}" -map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart "{final_lipsync_reel}"'
    subprocess.run(cmd_concat, shell=True, check=True)

    # Sync to all active output paths
    shutil.copyfile(final_lipsync_reel, final_std_reel)
    shutil.copyfile(final_lipsync_reel, final_agnes_reel)
    if os.path.exists(os.path.dirname(scratch_output)):
        shutil.copyfile(final_lipsync_reel, scratch_output)

    print(f"\n🎉 SUCCESS: Master 4-Scene Reel with Live Character Lip-Sync Complete!")
    print(f"File Size: {os.path.getsize(final_lipsync_reel)} bytes")
    print(f"Path: {final_lipsync_reel}")

if __name__ == '__main__':
    main()
