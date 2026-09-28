import os
import sys
import asyncio
import subprocess
import wave
import cv2
import numpy as np
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\Amar's PC\Documents\Youtube Automation\youtube-automation-agent"
assets_dir = os.path.join(base_dir, 'data', 'assets')
audio_dir = os.path.join(base_dir, 'data', 'audio', 'gulab_jamun')
videos_dir = os.path.join(base_dir, 'data', 'videos')
sfx_dir = os.path.join(audio_dir, 'sfx')

os.makedirs(sfx_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)

ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

scenes = [
    {
        'id': 1,
        'title': 'The Mirror Motivation',
        'image': os.path.join(assets_dir, 'gulab_scene1_mirror.jpg'),
        'dialogues': [
            {
                'speaker': 'gulab_jamun',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+5%',
                'pitch': '+4Hz',
                'text': 'बहुत हो गया मीठा-मीठा जीवन! आज से गुलाब जामुन बनेगा... सिक्स पैक जामुन! अब कोई मुझे गोल-मटोल नहीं बोलेगा!'
            }
        ],
        'zoom_type': 'zoom_in'
    },
    {
        'id': 2,
        'title': 'Trainer Samosa Entry',
        'image': os.path.join(assets_dir, 'gulab_scene2_trainer.jpg'),
        'dialogues': [
            {
                'speaker': 'trainer_samosa',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+15%',
                'pitch': '+6Hz',
                'text': 'अरे ओए मीठे! देसी आयरन जिम में स्वागत है! अगर क्रंच चाहिए तो चाशनी छोड़, पसीना बहा! चलो, पचास डंबल पुश-अप्स!'
            }
        ],
        'zoom_type': 'pan_and_zoom'
    },
    {
        'id': 3,
        'title': 'The Workout Struggle',
        'image': os.path.join(assets_dir, 'gulab_scene3_workout.jpg'),
        'dialogues': [
            {
                'speaker': 'gulab_jamun',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+10%',
                'pitch': '+4Hz',
                'text': 'उफ्फ समोसा भाई! मेरी तो चाशनी टपक रही है! पर मैं रुकेगा नहीं!'
            },
            {
                'speaker': 'trainer_samosa',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+15%',
                'pitch': '+8Hz',
                'text': 'शाबाश जामुन! नो चाशनी, नो गेन! तेज दौड़!'
            }
        ],
        'zoom_type': 'rhythmic_run'
    },
    {
        'id': 4,
        'title': 'Six-Pack Transformation',
        'image': os.path.join(assets_dir, 'gulab_scene4_sixpack.jpg'),
        'dialogues': [
            {
                'speaker': 'gulab_jamun',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+8%',
                'pitch': '+0Hz',
                'text': 'देख रहे हो समोसा भाई? अब चाशनी नहीं, प्रोटीन शेक पियूँगा!'
            },
            {
                'speaker': 'jalebi',
                'voice': 'hi-IN-SwaraNeural',
                'rate': '+15%',
                'pitch': '+6Hz',
                'text': 'अरे वाह जामुन जी! अब तो आप सबसे क्रिस्पी स्वीट बन गए!'
            },
            {
                'speaker': 'narrator',
                'voice': 'hi-IN-MadhurNeural',
                'rate': '+10%',
                'pitch': '+0Hz',
                'text': 'आपकी पसंदीदा मिठाई कौन सी है? कमेंट में बताओ और फॉलो करो!'
            }
        ],
        'zoom_type': 'punch_in'
    }
]

async def generate_scene_dialogue_audios():
    print("\n--- Generating Character Neural Audios ---")
    for s in scenes:
        parts = []
        for idx, d in enumerate(s['dialogues']):
            p_mp3 = os.path.join(audio_dir, f"scene_{s['id']}_part_{idx}.mp3")
            comm = edge_tts.Communicate(d['text'], d['voice'], rate=d['rate'], pitch=d['pitch'])
            await comm.save(p_mp3)
            parts.append(p_mp3)
            
        merged_wav = os.path.join(audio_dir, f"scene_{s['id']}_dialogue.wav")
        if len(parts) == 1:
            cmd = f'"{ffmpeg_bin}" -y -i "{parts[0]}" -ar 44100 -ac 2 "{merged_wav}"'
        else:
            inputs = " ".join([f'-i "{p}"' for p in parts])
            fcomplex = "".join([f'[{i}:a]' for i in range(len(parts))]) + f'concat=n={len(parts)}:v=0:a=1[a]'
            cmd = f'"{ffmpeg_bin}" -y {inputs} -filter_complex "{fcomplex}" -map "[a]" -ar 44100 -ac 2 "{merged_wav}"'
        subprocess.run(cmd, shell=True, check=True)
        
        # Probe duration
        res = subprocess.run(f'"{ffmpeg_bin}" -i "{merged_wav}" 2>&1', shell=True, stdout=subprocess.PIPE, text=True)
        dur = 5.0
        for line in res.stdout.split('\n'):
            if 'Duration:' in line:
                tstr = line.split('Duration:')[1].split(',')[0].strip()
                p = tstr.split(':')
                dur = float(p[0])*3600 + float(p[1])*60 + float(p[2])
                break
        
        # Add slight padding for natural breathing room
        s['dialogue_wav'] = merged_wav
        s['duration'] = dur + 0.6
        print(f"Scene {s['id']} ({s['title']}) dialogue duration: {s['duration']:.2f}s")

def synthesize_scene_sfx_and_music(scene):
    sr = 44100
    dur = scene['duration']
    total_samples = int(dur * sr)
    t = np.linspace(0, dur, total_samples, endpoint=False)
    
    # 1. Background Gym Beat (Desi Bhangra Workout Rhythm: 128 BPM -> 0.468s per beat)
    beat_sec = 60.0 / 128.0
    total_beats = int(dur / beat_sec) + 2
    bgm = np.zeros(total_samples, dtype=np.float32)
    
    # Dholak bass & snare pattern
    for b in range(total_beats):
        b_st = b * beat_sec
        b_idx = int(b_st * sr)
        b_len = int(beat_sec * sr)
        if b_idx + b_len > total_samples:
            b_len = total_samples - b_idx
        if b_len <= 0: break
        bt = np.linspace(0, b_len / sr, b_len, endpoint=False)
        
        # Bass kick on 0, 2
        if b % 2 == 0:
            kick = 0.18 * np.sin(2 * np.pi * 75 * np.exp(-12.0 * bt) * bt) * np.exp(-6.0 * bt)
            bgm[b_idx:b_idx+b_len] += kick
        # Snare / Dholak slap on 1, 3
        else:
            snare = 0.12 * np.random.normal(0, 0.05, b_len) * np.exp(-15.0 * bt)
            bgm[b_idx:b_idx+b_len] += snare
        # Funky bassline notes (E minor / A minor)
        note_freq = 110.0 if (b // 4) % 2 == 0 else 130.81
        synth_bass = 0.08 * np.sin(2 * np.pi * note_freq * bt) * np.exp(-4.0 * bt)
        bgm[b_idx:b_idx+b_len] += synth_bass

    # 2. Specific Sound Effects per Scene
    sfx = np.zeros(total_samples, dtype=np.float32)
    
    if scene['id'] == 1:
        # Mirror tummy squish + sparkle chime
        chime_st = int(0.4 * sr)
        chime_len = min(total_samples - chime_st, int(2.0 * sr))
        if chime_len > 0:
            ct = np.linspace(0, chime_len / sr, chime_len, endpoint=False)
            sfx[chime_st:chime_st+chime_len] += 0.20 * np.sin(2 * np.pi * 1200 * ct) * np.exp(-4.0 * ct)
            
    elif scene['id'] == 2:
        # Barbell clink & trainer coach whistle
        whistle_st = int(0.2 * sr)
        w_len = min(total_samples - whistle_st, int(1.0 * sr))
        if w_len > 0:
            wt = np.linspace(0, w_len / sr, w_len, endpoint=False)
            # Whistle trill (2500Hz + FM modulation)
            whistle = 0.22 * np.sin(2 * np.pi * (2500 + 150 * np.sin(2 * np.pi * 25 * wt)) * wt) * np.sin(np.pi * wt)
            sfx[whistle_st:whistle_st+w_len] += whistle

    elif scene['id'] == 3:
        # Treadmill squeak & motivational whistle
        for step_i in range(int(dur / 0.8)):
            st_idx = int((step_i * 0.8 + 0.3) * sr)
            s_len = min(total_samples - st_idx, int(0.2 * sr))
            if s_len > 0:
                stt = np.linspace(0, s_len / sr, s_len, endpoint=False)
                sfx[st_idx:st_idx+s_len] += 0.15 * np.sin(2 * np.pi * 800 * stt) * np.exp(-15.0 * stt)
                
    elif scene['id'] == 4:
        # Golden spotlight fanfare & victory bell
        bell_st = int(0.3 * sr)
        b_len = min(total_samples - bell_st, int(3.0 * sr))
        if b_len > 0:
            btt = np.linspace(0, b_len / sr, b_len, endpoint=False)
            for f in [523.25, 659.25, 783.99, 1046.50]:
                sfx[bell_st:bell_st+b_len] += 0.15 * np.sin(2 * np.pi * f * btt) * np.exp(-2.5 * btt)

    # Combine BGM + SFX
    mixed_bg = 0.22 * bgm + 0.70 * sfx
    mixed_norm = np.clip(mixed_bg, -0.95, 0.95)
    sfx_int16 = (mixed_norm * 32767).astype(np.int16)
    
    scene_bg_wav = os.path.join(sfx_dir, f"scene_{scene['id']}_bg_sfx.wav")
    with wave.open(scene_bg_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        stereo_data = np.column_stack((sfx_int16, sfx_int16)).flatten()
        wf.writeframes(stereo_data.tobytes())
        
    # Mux dialogue (volume=1.8) + bg_sfx (volume=1.0) into master scene audio
    scene_final_audio = os.path.join(audio_dir, f"scene_{scene['id']}_master_audio.wav")
    cmd = f'"{ffmpeg_bin}" -y -i "{scene["dialogue_wav"]}" -i "{scene_bg_wav}" -filter_complex "[0:a]volume=1.8[dia];[1:a]volume=1.0[bg];[dia][bg]amix=inputs=2:duration=first:dropout_transition=0,volume=1.2[a]" -map "[a]" -ar 44100 -ac 2 "{scene_final_audio}"'
    subprocess.run(cmd, shell=True, check=True)
    scene['final_audio'] = scene_final_audio
    print(f"Scene {scene['id']} audio & SFX mixed: {scene_final_audio}")

def render_scene_3d_video(scene):
    img_path = scene['image']
    audio_path = scene['final_audio']
    duration = scene['duration']
    out_video = os.path.join(videos_dir, f"gulab_scene_{scene['id']}_rendered.mp4")

    target_w, target_h = 720, 1280
    fps = 30
    total_frames = int(duration * fps)

    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Could not load image {img_path}")

    base_w, base_h = 900, 1600
    img_scaled = cv2.resize(img, (base_w, base_h), interpolation=cv2.INTER_LANCZOS4)

    temp_raw = os.path.join(videos_dir, f"temp_gulab_scene_{scene['id']}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(temp_raw, fourcc, fps, (target_w, target_h))

    zoom_type = scene['zoom_type']

    for i in range(total_frames):
        t = i / float(total_frames)

        if zoom_type == 'zoom_in':
            scale = 1.0 + 0.14 * t
            cx = base_w / 2.0
            cy = base_h / 2.0 + 20.0 * t
        elif zoom_type == 'pan_and_zoom':
            scale = 1.08 + 0.05 * np.sin(t * np.pi)
            cx = base_w / 2.0 + (t - 0.5) * 45.0
            cy = base_h / 2.0
        elif zoom_type == 'rhythmic_run':
            scale = 1.05 + 0.06 * np.sin(t * 8.0 * np.pi)
            cx = base_w / 2.0 + 10.0 * np.sin(t * 8.0 * np.pi)
            cy = base_h / 2.0 + 8.0 * np.cos(t * 8.0 * np.pi)
        elif zoom_type == 'punch_in':
            scale = 1.0 + 0.20 * (t ** 0.8)
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

    # Mux with scene master audio
    cmd_mux = f'"{ffmpeg_bin}" -y -i "{temp_raw}" -i "{audio_path}" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart -shortest "{out_video}"'
    subprocess.run(cmd_mux, shell=True, check=True)

    if os.path.exists(temp_raw): os.remove(temp_raw)
    scene['rendered_video'] = out_video
    print(f"Scene {scene['id']} complete: {out_video}")

def assemble_full_story_reel():
    print(f"\n=================================================")
    print(f"🎬 Assembling Complete 3D Animated Reel")
    print(f"=================================================")

    final_reel = os.path.join(videos_dir, 'gulab_jamun_gym_transformation_final_reel.mp4')
    story_mirror = os.path.join(videos_dir, 'final_gulab_jamun_story.mp4')
    brain_copy = r"C:\Users\Amar's PC\.gemini\antigravity\brain\e0b5b209-d2ea-49be-a472-855741d1672a\gulab_jamun_gym_transformation_final_reel.mp4"
    
    in_args = " ".join([f'-i "{s["rendered_video"]}"' for s in scenes])
    filter_complex = "".join([f'[{i}:v][{i}:a]' for i in range(len(scenes))]) + f'concat=n={len(scenes)}:v=1:a=1[v][a]'
    
    cmd_concat = f'"{ffmpeg_bin}" -y {in_args} -filter_complex "{filter_complex}" -map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -movflags +faststart "{final_reel}"'
    subprocess.run(cmd_concat, shell=True, check=True)

    import shutil
    shutil.copyfile(final_reel, story_mirror)
    shutil.copyfile(final_reel, brain_copy)

    print(f"\n🎉 FULL REEL GENERATED: {final_reel}")
    print(f"File Size: {os.path.getsize(final_reel)} bytes")

async def main():
    await generate_scene_dialogue_audios()
    for scene in scenes:
        synthesize_scene_sfx_and_music(scene)
        render_scene_3d_video(scene)
    assemble_full_story_reel()

if __name__ == '__main__':
    asyncio.run(main())
