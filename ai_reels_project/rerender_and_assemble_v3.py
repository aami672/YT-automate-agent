import os
import sys
import json
import time
import asyncio
import subprocess
import shutil
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

AGNES_ROOT = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator"
if AGNES_ROOT not in sys.path:
    sys.path.insert(0, AGNES_ROOT)

from core.api.agnes_video import AgnesVideoAPI
from core.config import get_api_key

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BRAIN_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\brain\948aeb55-f992-450a-afe5-fdaa77988433"
AI_REELS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(AI_REELS_DIR, "output")
AUDIO_DIR = os.path.join(AI_REELS_DIR, "audio_tracks")
CLIPS_DIR = os.path.join(AI_REELS_DIR, "scene_clips_v3")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

SCENES = [
    {
        "index": 0,
        "name": "Pencil_Clean",
        "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई एकदम तैयार हैं, आज तो क्लास में पूरे दस में से दस मार्क्स लेकर ही मानेंगे!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+8%",
        "pitch": "+18Hz",
        "image": os.path.join(BRAIN_DIR, "pencil_clean_scene1_1790778959181.jpg"),
        "prompt": "A high-quality 3D Pixar Disney animation scene. A cheerful yellow wooden pencil character with big expressive cartoon eyes and a warm smile on the pencil body standing proudly on a student notebook on a wooden classroom desk. Bright morning sunlight, soft classroom background. Important: NO tail, NO animal legs, pure classic stationery pencil character, steady locked camera, zero jitter, perfectly proportioned vertical 9:16 framing."
    },
    {
        "index": 1,
        "name": "Eraser_Panicking",
        "text": "अरे पेंसिल भाई धीरे लिखो! तुम गलतियां करोगे और मुझे घिसना पड़ेगा, मेरी तो कमर टूट जाएगी!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+5%",
        "pitch": "+32Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_eraser_scene2_1790767774858.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute chunky pink eraser character with comical worried wide eyes and hands on its cheeks, trembling playfully on the wooden desk beside an open notebook. Classroom setting with warm morning light, steady camera, rich tactile rubber textures, perfectly proportioned vertical 9:16 framing."
    },
    {
        "index": 2,
        "name": "Sharpener_Vertical",
        "text": "चिंता मत करो इरेज़र बाबू! जब तक शार्पनर यहाँ है, पेंसिल की नोक रॉकेट की तरह शार्प रहेगी, लिखाई एकदम मक्खन!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+10%",
        "pitch": "+18Hz",
        "image": os.path.join(BRAIN_DIR, "sharpener_vertical_scene3_1790778982658.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute friendly blue plastic pencil sharpener character with big expressive cartoon eyes standing proudly upright on an open notebook on a wooden school desk. Sharp blade visible, bright morning sunlight, locked steady camera, perfectly proportioned vertical 9:16 framing, zero distortion, zero stretching."
    },
    {
        "index": 3,
        "name": "Ruler_Superhero",
        "text": "शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, एक भी लाइन टेढ़ी नहीं होगी, हर डायग्राम बिल्कुल सीधा और परफेक्ट!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-22Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_ruler_scene4_1790767816866.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A tall sleek clear plastic ruler character standing proudly like a superhero with hands on hips on an open math notebook on the wooden classroom desk. Bright morning sunlight, clear transparent reflections, proud confident expression, locked steady framing, pure 3D character, perfectly proportioned 9:16 vertical."
    },
    {
        "index": 4,
        "name": "Squad_Vertical",
        "text": "देखा इसे कहते हैं बैकपैक स्क्वाड! लिखना, मिटाना, शार्प करना और सीधी लाइन - सब मिलकर करेंगे टॉप!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+6%",
        "pitch": "+14Hz",
        "image": os.path.join(BRAIN_DIR, "squad_vertical_scene5_1790779257620.jpg"),
        "prompt": "A high-quality 3D Pixar Disney animation scene. The entire stationery squad - yellow pencil, pink eraser, blue sharpener, and clear ruler grouped closely in the center of an open notebook on the wooden school desk. Warm morning sunlight, chalkboard in background, locked steady camera, perfectly proportioned vertical 9:16 framing, zero stretching, no humans."
    },
    {
        "index": 5,
        "name": "Outro_Vertical",
        "text": "स्कूल की घंटी बज चुकी है दोस्तों! आपका सबसे पसंदीदा स्टेशनरी साथी कौन सा है? कमेंट में बताओ और सब्सक्राइब जरूर करो!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+8%",
        "pitch": "+20Hz",
        "image": os.path.join(BRAIN_DIR, "outro_vertical_scene6_1790779279652.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. Celebratory finale of the cute stationery squad (yellow pencil, pink eraser, blue sharpener, clear ruler) waving happily together with joyful big smiles on the wooden school desk next to a colorful pencil box. Festive morning sunlight, sparkling confetti bokeh, locked steady camera, perfectly proportioned vertical 9:16 framing, zero stretching, no humans."
    }
]

async def create_cartoon_audio_tracks():
    print("[1/4] 🎙️ Generating Distinct High-Pitch Cartoon Character Voiceovers...", flush=True)
    scene_audios = []
    
    for sc in SCENES:
        idx = sc["index"]
        raw_audio = os.path.join(AUDIO_DIR, f"v3_scene_{idx}_raw.mp3")
        padded_audio = os.path.join(AUDIO_DIR, f"v3_scene_{idx}_padded.mp3")
        
        communicate = edge_tts.Communicate(sc["text"], voice=sc["voice"], rate=sc["rate"], pitch=sc["pitch"])
        await communicate.save(raw_audio)
        
        # Duration probe
        r = subprocess.run([FFMPEG, "-i", raw_audio], capture_output=True, text=True, errors="replace")
        dur = 7.0
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
                
        slot_dur = 9.54 if idx < 5 else 10.04
        pad_dur = max(0.0, slot_dur - dur)
        
        cmd_pad = [
            FFMPEG, "-y",
            "-i", raw_audio,
            "-af", f"apad=pad_dur={pad_dur:.2f}",
            "-t", f"{slot_dur:.2f}",
            padded_audio
        ]
        subprocess.run(cmd_pad, capture_output=True)
        scene_audios.append(padded_audio)
        print(f"  [+] Scene {idx} ({sc['name']}): Voice={sc['voice']} (Pitch: {sc['pitch']}, Rate: {sc['rate']}) | Speech={dur:.2f}s (Padded={pad_dur:.2f}s)", flush=True)
        
    concat_txt = os.path.join(AUDIO_DIR, "v3_audio_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in scene_audios:
            rel = os.path.basename(p)
            f.write(f"file '{rel}'\n")
            
    master_dialogue = os.path.join(AUDIO_DIR, "v3_master_dialogue.mp3")
    cmd_concat = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "v3_audio_concat.txt", "-c", "copy", master_dialogue]
    subprocess.run(cmd_concat, cwd=AUDIO_DIR, capture_output=True)
    print(f"  [✓] Master Cartoon Dialogue Track: {master_dialogue}", flush=True)
    return master_dialogue

async def render_updated_scene_videos():
    print("\n[2/4] 🎬 Rendering Updated 3D Scene Videos (Clean Pencil & Proportioned 9:16 Frames)...", flush=True)
    api = AgnesVideoAPI(api_key=get_api_key(), default_duration=10)
    clip_paths = []
    
    # Scenes to re-render for clean pencil and non-stretched sharpener/squad/outro: 0, 2, 4, 5
    # Scenes 1 and 3 can use existing or render if needed
    for sc in SCENES:
        idx = sc["index"]
        clip_file = os.path.join(CLIPS_DIR, f"scene_{idx}.mp4")
        
        # Check if already rendered in v3
        if os.path.exists(clip_file) and os.path.getsize(clip_file) > 100000:
            print(f"  [✓] Scene {idx} already exists: {clip_file}", flush=True)
            clip_paths.append(clip_file)
            continue
            
        # If scene 1 or 3 already exist in old clips_dir and don't need changes, copy them
        old_clip = os.path.join(AI_REELS_DIR, "scene_clips", f"scene_{idx}.mp4")
        if idx in [1, 3] and os.path.exists(old_clip) and os.path.getsize(old_clip) > 100000:
            shutil.copyfile(old_clip, clip_file)
            print(f"  [✓] Scene {idx} reused from verified clip: {clip_file}", flush=True)
            clip_paths.append(clip_file)
            continue
            
        print(f"  [+] Rendering Scene {idx} ({sc['name']}) from updated reference image...", flush=True)
        out = await api.generate_single_video(
            prompt=sc["prompt"],
            reference_image_paths=[sc["image"]],
            duration=10,
            width=768,
            height=1152,
            negative_prompt="tail, animal, legs on pencil, stretched, wide, distorted, jitter, stutter, human, people, children, live action, blurry, low quality, morphing"
        )
        await out.save(clip_file)
        print(f"  [✓] Scene {idx} rendered successfully: {clip_file}", flush=True)
        clip_paths.append(clip_file)
        
    return clip_paths

def build_dissolve_sequence_with_start_end_fades(clip_paths):
    print("\n[3/4] ✨ Normalizing to Strict 9:16 (720x1280) & Applying In/Out Dissolves...", flush=True)
    normalized_clips = []
    
    for idx, c in enumerate(clip_paths):
        norm_path = os.path.join(OUTPUT_DIR, f"v3_scene_{idx}_9x16.mp4")
        cmd_norm = [
            FFMPEG, "-y",
            "-i", c,
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "17",
            "-pix_fmt", "yuv420p",
            norm_path
        ]
        subprocess.run(cmd_norm, capture_output=True)
        normalized_clips.append(norm_path)
        print(f"  [+] Scene {idx} standardized to 720x1280", flush=True)
        
    # Build 5 crossfades + Start Fade In + End Fade Out
    filter_complex = (
        "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=9.54[v01];"
        "[v01][2:v]xfade=transition=fade:duration=0.5:offset=19.08[v02];"
        "[v02][3:v]xfade=transition=fade:duration=0.5:offset=28.62[v03];"
        "[v03][4:v]xfade=transition=fade:duration=0.5:offset=38.16[v04];"
        "[v04][5:v]xfade=transition=fade:duration=0.5:offset=47.70[v_xfade];"
        "[v_xfade]fade=t=in:st=0:d=0.75,fade=t=out:st=56.75:d=1.0[vout]"
    )
    
    xfade_output = os.path.join(OUTPUT_DIR, "v3_master_dissolve_video.mp4")
    inputs = []
    for c in normalized_clips:
        inputs.extend(["-i", c])
        
    cmd = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        xfade_output
    ]
    print("  [+] Executing xfade + intro/outro dissolves...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] xfade failed:", res.stderr, flush=True)
        raise RuntimeError("xfade failure")
        
    print(f"  [✓] Dissolve Video Ready: {xfade_output}", flush=True)
    return xfade_output

def produce_final_master_v3(video_path, dialogue_path):
    print("\n[4/4] 🚀 Multiplexing Master Reel with Boosted BGM, Real School Bell SFX, and 60 FPS...", flush=True)
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_1min_premium_60fps.mp4")
    
    bgm_path = os.path.join(AUDIO_DIR, "cheerful_cartoon_bgm.wav")
    bell_path = os.path.join(AUDIO_DIR, "real_school_bell.wav")
    
    # Audio balancing:
    # 1. Dialogues: volume=1.05 (clean, balanced cartoon dialogue)
    # 2. Cheerful BGM: volume=0.35 (boosted lively cartoon music loop, clearly audible throughout)
    # 3. Real School Bell SFX: delayed to 47.70s (Scene 6 start), volume=0.90 (crisp loud bell ring)
    # 4. Master Audio Fade: 0.3s fade-in at start, 1.2s fade-out at end so no abrupt cutoffs
    
    audio_filter = (
        "[1:a]volume=1.05,aformat=channel_layouts=stereo[a_diag];"
        "[2:a]volume=0.35,aformat=channel_layouts=stereo[a_bgm];"
        "[3:a]adelay=47700|47700,volume=0.90,aformat=channel_layouts=stereo[a_bell];"
        "[a_diag][a_bgm][a_bell]amix=inputs=3:duration=first:dropout_transition=2,"
        "afade=t=in:st=0:d=0.3,afade=t=out:st=56.5:d=1.2[a_mix]"
    )
    
    video_filter = "[0:v]fps=fps=60[v60]"
    full_filter = f"{video_filter};{audio_filter}"
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", dialogue_path,
        "-i", bgm_path,
        "-i", bell_path,
        "-filter_complex", full_filter,
        "-map", "[v60]",
        "-map", "[a_mix]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "44100",
        "-shortest",
        final_output
    ]
    print("  [+] Final encoding to 60 FPS...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] Multiplexing error:", res.stderr, flush=True)
        raise RuntimeError("Final multiplexing failure")
        
    print(f"\n🎉 UPDATED MASTER 1-MINUTE 60 FPS REEL READY:\n{final_output}", flush=True)
    return final_output

async def main():
    print("="*75)
    print("🌟 RE-PRODUCING PERFECT 60 FPS BACKPACK SQUAD REEL (V3) 🌟")
    print("="*75, flush=True)
    
    master_dialogue = await create_cartoon_audio_tracks()
    clip_paths = await render_updated_scene_videos()
    video_track = build_dissolve_sequence_with_start_end_fades(clip_paths)
    final_output = produce_final_master_v3(video_track, master_dialogue)
    print("\n✅ V3 PRODUCTION COMPLETED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
