import os
import sys
import asyncio
import subprocess
import edge_tts
import cv2
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets_dir = os.path.join(base_dir, 'data', 'assets')
videos_dir = os.path.join(base_dir, 'data', 'videos')
audio_dir = os.path.join(base_dir, 'data', 'audio')
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)

ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

scenes = [
    {
        'id': 1,
        'title': 'The Romantic Entry',
        'image': os.path.join(assets_dir, 'reel_scene1_aloo.jpg'),
        'dialogues': [
            {
                'speaker': 'aloo',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+0%',
                'pitch': '+0Hz',
                'text': 'गोभी जी! जब से आपको सब्ज़ी मंडी में देखा है, मेरा दिल सिर्फ आपके लिए धड़कता है! मैं आपके बिना नहीं रह सकता!'
            }
        ],
        'zoom_type': 'zoom_in'
    },
    {
        'id': 2,
        'title': 'The Villain Entry',
        'image': os.path.join(assets_dir, 'reel_scene2_tamatar.jpg'),
        'dialogues': [
            {
                'speaker': 'tamatar',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+15%',
                'pitch': '+6Hz',
                'text': 'ओए गोलू आलू! साइड हट! गोभी तो सिर्फ मेरी बनेगी! देख मेरा लाल रंग और ग्लो... तेरे जैसा बोरिंग नहीं हूँ मैं!'
            }
        ],
        'zoom_type': 'zoom_out'
    },
    {
        'id': 3,
        'title': "The Argument & Gobhi's Choice",
        'image': os.path.join(assets_dir, 'reel_scene3_argument.jpg'),
        'dialogues': [
            {
                'speaker': 'aloo',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+10%',
                'pitch': '-2Hz',
                'text': 'अरे टमाटर भाई, तुम तो दो दिन में गल जाओगे... मैं आलू हूँ, हर डिश में साथ निभाता हूँ!'
            },
            {
                'speaker': 'gobhi',
                'voice': 'hi-IN-SwaraNeural',
                'rate': '+5%',
                'pitch': '+5Hz',
                'text': 'हाय राम! पर मैं तो सिर्फ मटर जी के साथ जोड़ी बनाती हूँ!'
            }
        ],
        'zoom_type': 'pan_and_zoom'
    },
    {
        'id': 4,
        'title': 'The Twist Ending',
        'image': os.path.join(assets_dir, 'reel_scene4_matar.jpg'),
        'dialogues': [
            {
                'speaker': 'matar',
                'voice': 'hi-IN-SwaraNeural',
                'rate': '+20%',
                'pitch': '+10Hz',
                'text': 'चलो हटो सब, आलू-गोभी नहीं, अब मटर-पनीर और गोभी-मटर का ज़माना है!'
            },
            {
                'speaker': 'narrator',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+10%',
                'pitch': '+0Hz',
                'text': 'आपकी पसंदीदा सब्ज़ी कौन सी है? कमेंट में बताओ और फॉलो करो!'
            }
        ],
        'zoom_type': 'punch_in'
    }
]

async def generate_scene_audio(scene):
    scene_audio_parts = []
    for idx, d in enumerate(scene['dialogues']):
        part_path = os.path.join(audio_dir, f"scene_{scene['id']}_part_{idx}.mp3")
        communicate = edge_tts.Communicate(d['text'], d['voice'], rate=d.get('rate', '+0%'), pitch=d.get('pitch', '+0Hz'))
        await communicate.save(part_path)
        scene_audio_parts.append(part_path)

    merged_audio = os.path.join(audio_dir, f"scene_{scene['id']}_audio.wav")
    if len(scene_audio_parts) == 1:
        subprocess.run(f'"{ffmpeg_bin}" -y -i "{scene_audio_parts[0]}" -ar 44100 -ac 2 "{merged_audio}"', shell=True, check=True)
    else:
        # Use filter_complex concat for multiple audio parts
        inputs = " ".join([f'-i "{p}"' for p in scene_audio_parts])
        filter_str = "".join([f'[{i}:a]' for i in range(len(scene_audio_parts))]) + f'concat=n={len(scene_audio_parts)}:v=0:a=1[a]'
        cmd = f'"{ffmpeg_bin}" -y {inputs} -filter_complex "{filter_str}" -map "[a]" -ar 44100 -ac 2 "{merged_audio}"'
        subprocess.run(cmd, shell=True, check=True)

    # Get audio duration
    probe_cmd = f'"{ffmpeg_bin}" -i "{merged_audio}" 2>&1'
    res = subprocess.run(probe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    duration = 5.0
    for line in res.stdout.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            parts = time_str.split(':')
            duration = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break
    
    # Add 0.3s padding
    duration += 0.3
    scene['audio_path'] = merged_audio
    scene['duration'] = duration
    print(f"[Audio] Scene {scene['id']} ({scene['title']}) generated: {duration:.2f}s")

def render_scene_video(scene):
    img_path = scene['image']
    audio_path = scene['audio_path']
    duration = scene['duration']
    out_video = os.path.join(videos_dir, f"scene_{scene['id']}_rendered.mp4")

    # Target 720x1280 (9:16 vertical format)
    target_w, target_h = 720, 1280
    fps = 30
    total_frames = int(duration * fps)

    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not load image {img_path}")

    # Scale base image
    base_w, base_h = 900, 1600
    img_scaled = cv2.resize(img, (base_w, base_h), interpolation=cv2.INTER_LANCZOS4)

    temp_raw = os.path.join(videos_dir, f"temp_scene_{scene['id']}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(temp_raw, fourcc, fps, (target_w, target_h))

    zoom_type = scene['zoom_type']

    for i in range(total_frames):
        t = i / float(total_frames)

        if zoom_type == 'zoom_in':
            scale = 1.0 + 0.12 * t
            cx, cy = base_w / 2.0, base_h / 2.0
        elif zoom_type == 'zoom_out':
            scale = 1.15 - 0.12 * t
            cx, cy = base_w / 2.0, base_h / 2.0
        elif zoom_type == 'pan_and_zoom':
            scale = 1.05 + 0.06 * np.sin(t * np.pi)
            cx = base_w / 2.0 + (t - 0.5) * 35.0
            cy = base_h / 2.0
        elif zoom_type == 'punch_in':
            scale = 1.0 + 0.18 * (t ** 0.8)
            cx = base_w / 2.0
            cy = base_h / 2.0 + 30.0 * (1.0 - t)
        else:
            scale = 1.0 + 0.10 * t
            cx, cy = base_w / 2.0, base_h / 2.0

        crop_w = int(base_w / scale)
        crop_h = int(base_h / scale)
        x1 = max(0, min(base_w - crop_w, int(cx - crop_w / 2)))
        y1 = max(0, min(base_h - crop_h, int(cy - crop_h / 2)))

        crop = img_scaled[y1:y1+crop_h, x1:x1+crop_w]
        frame = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        writer.write(frame)

    writer.release()

    # Mux with scene audio
    print(f"[Mux] Muxing Scene {scene['id']} video with audio...")
    cmd_mux = f'"{ffmpeg_bin}" -y -i "{temp_raw}" -i "{audio_path}" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart -shortest "{out_video}"'
    subprocess.run(cmd_mux, shell=True, check=True)

    if os.path.exists(temp_raw): os.remove(temp_raw)
    scene['rendered_video'] = out_video
    print(f"[Render] Scene {scene['id']} complete: {out_video}")

def assemble_full_reel():
    print(f"\n==========================================")
    print(f"🎬 Assembling Complete 3D Pixar Hindi Reel")
    print(f"==========================================")

    final_reel = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4')
    
    in_args = " ".join([f'-i "{s["rendered_video"]}"' for s in scenes])
    filter_complex = "".join([f'[{i}:v][{i}:a]' for i in range(len(scenes))]) + f'concat=n={len(scenes)}:v=1:a=1[v][a]'
    
    cmd_concat = f'"{ffmpeg_bin}" -y {in_args} -filter_complex "{filter_complex}" -map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart "{final_reel}"'
    subprocess.run(cmd_concat, shell=True, check=True)

    print(f"\n🎉 FULL REEL GENERATED: {final_reel}")
    print(f"File Size: {os.path.getsize(final_reel)} bytes")

async def main():
    print("Step 1: Generating Neural Hindi Dialogue Audios...")
    for scene in scenes:
        await generate_scene_audio(scene)

    print("\nStep 2: Rendering Dynamic 3D Pixar Vertical Video Scenes...")
    for scene in scenes:
        render_scene_video(scene)

    print("\nStep 3: Assembling Full Story Reel...")
    assemble_full_reel()

if __name__ == '__main__':
    asyncio.run(main())
