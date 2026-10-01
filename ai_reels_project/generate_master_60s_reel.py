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
AI_REELS_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
OUTPUT_DIR = os.path.join(AI_REELS_DIR, "output")
AUDIO_DIR = os.path.join(AI_REELS_DIR, "audio_tracks")
CLIPS_DIR = os.path.join(AI_REELS_DIR, "scene_clips")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

SCENES = [
    {
        "index": 0,
        "name": "Pencil_Intro",
        "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे दस में से दस मार्क्स लेकर ही मानेंगे! सारे नोट्स सबसे सुंदर मैं ही लिखूँगा!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_pencil_scene1_1790767758092.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cheerful anthropomorphic yellow wooden pencil with large expressive eyes smiling excitedly on a wooden classroom desk beside a colorful backpack. Warm morning sunlight streaming through the windows, soft bokeh, steady locked-off framing, rich 3D textures, zero jitter, zero hallucinations, pure animated character."
    },
    {
        "index": 1,
        "name": "Eraser_Panicking",
        "text": "तभी इरेज़र रोते हुए बोला: अरे अरे रुको भाई! थोड़ा आहिस्ता लिखो! तुम तो गलतियां कर-कर के पेज भर दोगे, और पीछे-पीछे मिटाते-मिटाते मेरी कमर घिस जाएगी! मुझे भी तो आराम चाहिए!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+0%",
        "pitch": "+14Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_eraser_scene2_1790767774858.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute chunky pink eraser character with comical worried wide eyes and hands on its cheeks, trembling playfully beside an open notebook on the wooden desk. Classroom setting with warm morning light, steady camera, rich tactile rubber textures, no white void, pure 3D animated character."
    },
    {
        "index": 2,
        "name": "Sharpener_Hero",
        "text": "शार्पनर बोला: चिंता मत करो इरेज़र बाबू! जब तक मैं यहाँ हूँ, पेंसिल की नोक को रॉकेट की तरह शार्प रखूँगा! बस एक बार घुमाओ, और लिखाई मक्खन जैसी!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+5%",
        "pitch": "+6Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_sharpener_scene3_1790767790831.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute high-tech blue pencil sharpener character with cheerful expressive eyes and metallic details smiling playfully on the wooden classroom desk. Bright warm morning light, crisp reflections, locked steady framing, perfectly rendered 3D sharpener character."
    },
    {
        "index": 3,
        "name": "Ruler_Superhero",
        "text": "स्केल भाई शान से बोले: खामोश! जब तक स्केल साहब यहाँ मौजूद हैं, एक भी लाइन टेढ़ी नहीं होगी! हर डायग्राम बिल्कुल सीधा और परफेक्ट बनेगा! अनुशासन ही हमारी ताकत है!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-6%",
        "pitch": "-8Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_ruler_scene4_1790767816866.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A tall sleek clear plastic ruler character standing proudly like a superhero with hands on hips on an open math notebook on the wooden classroom desk. Bright morning sunlight, clear transparent reflections, proud confident expression, locked steady framing, pure 3D character."
    },
    {
        "index": 4,
        "name": "Squad_Teamwork",
        "text": "पेंसिल बोली: देखा इसे कहते हैं असली बैकपैक स्क्वाड टीमवर्क! लिखना, मिटाना, शार्प करना और सीधी लाइन खींचना - सब मिलकर करेंगे एग्जाम में टॉप!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+3%",
        "pitch": "+0Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_squad_scene5_1790767901291.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. The entire stationery squad - cute yellow pencil, pink eraser, blue sharpener, and clear ruler gathered together around an open notebook on the wooden school desk. Bright morning sunlight, chalkboard in background, high-detail 3D textures, vibrant Disney Pixar cinematic lighting, no humans, pure animated stationery friends."
    },
    {
        "index": 5,
        "name": "Outro_CTA",
        "text": "टन-टन-टन! स्कूल की घंटी बज चुकी है! तो दोस्तों, आपके स्कूल बैग में आपका सबसे पसंदीदा साथी कौन था - पेंसिल, इरेज़र या स्केल? अभी कमेंट में बताइए और सब्सक्राइब जरूर करें!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+6%",
        "pitch": "+3Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_outro_scene6_1790767918829.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. Celebratory finale of the cute stationery squad (yellow pencil, pink eraser, blue sharpener, clear ruler) waving happily together on the wooden school desk next to a colorful open pencil box. Festive morning sunlight, sparkling confetti bokeh, high 3D render quality, Disney Pixar character animation style, pure animated stationery items."
    }
]

async def generate_multivoice_audio():
    print("[1/4] 🎙️ Generating 6 Multi-Character Hindi Voiceover Tracks...")
    audio_files = []
    durations = []
    
    for sc in SCENES:
        out_path = os.path.join(AUDIO_DIR, f"scene_{sc['index']}.mp3")
        communicate = edge_tts.Communicate(sc["text"], voice=sc["voice"], rate=sc["rate"], pitch=sc["pitch"])
        await communicate.save(out_path)
        
        # Probe duration
        r = subprocess.run([FFMPEG, "-i", out_path], capture_output=True, text=True, errors="replace")
        dur = 9.5
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
        durations.append(dur)
        audio_files.append(out_path)
        print(f"  [+] Scene {sc['index']} ({sc['name']}): Voice={sc['voice']} (Pitch: {sc['pitch']}, Rate: {sc['rate']}) | Duration: {dur:.2f}s", flush=True)
        
    concat_list = os.path.join(AUDIO_DIR, "audio_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for fpath in audio_files:
            rel = os.path.basename(fpath)
            f.write(f"file '{rel}'\n")
            
    master_audio = os.path.join(AUDIO_DIR, "master_multivoice.mp3")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_concat.txt", "-c", "copy", master_audio]
    subprocess.run(cmd, cwd=AUDIO_DIR, capture_output=True)
    
    total_audio_dur = sum(durations)
    print(f"  [+] Master audio track ready! Total Duration: {total_audio_dur:.2f}s", flush=True)
    return master_audio, durations

async def generate_scene_videos(durations):
    print("\n[2/4] 🎬 Generating 6 High-Fidelity 3D Video Clips directly...", flush=True)
    api = AgnesVideoAPI(api_key=get_api_key(), default_duration=10)
    clip_paths = []
    
    for sc in SCENES:
        idx = sc["index"]
        clip_file = os.path.join(CLIPS_DIR, f"scene_{idx}.mp4")
        
        # If already exists and valid size, skip
        if os.path.exists(clip_file) and os.path.getsize(clip_file) > 100000:
            print(f"  [✓] Scene {idx} ({sc['name']}) already rendered: {clip_file}", flush=True)
            clip_paths.append(clip_file)
            continue
            
        print(f"  [+] Rendering Scene {idx} ({sc['name']}) from reference image...", flush=True)
        target_dur = max(5, min(10, int(round(durations[idx]))))
        
        out = await api.generate_single_video(
            prompt=sc["prompt"],
            reference_image_paths=[sc["image"]],
            duration=target_dur,
            width=768,
            height=1152,
            negative_prompt="jitter, stutter, flickering, human, people, children, live action, blurry, low quality, distorted, extra limbs, messy background, morphing"
        )
        await out.save(clip_file)
        print(f"  [✓] Scene {idx} rendered successfully: {clip_file}", flush=True)
        clip_paths.append(clip_file)
        
    return clip_paths

def build_dissolve_transitions(clip_paths, durations, trans_dur=0.5):
    print("\n[3/4] ✨ Applying Smooth Dissolve / Blur Crossfades between Scene Cuts...", flush=True)
    xfade_video = os.path.join(OUTPUT_DIR, "temp_dissolve_sequence.mp4")
    
    inputs_cmd = []
    for c in clip_paths:
        inputs_cmd.extend(["-i", c])
        
    n = len(clip_paths)
    filter_chains = []
    current_offset = durations[0] - trans_dur
    prev_label = "0:v"
    
    for i in range(1, n):
        next_label = f"{i}:v"
        out_label = f"v{i}" if i < n - 1 else "vout"
        
        filter_chains.append(
            f"[{prev_label}][{next_label}]xfade=transition=fade:duration={trans_dur}:offset={current_offset:.3f}[{out_label}]"
        )
        prev_label = out_label
        if i < n - 1:
            current_offset += durations[i] - trans_dur
            
    filter_str = ";".join(filter_chains)
    
    cmd_xfade = [
        FFMPEG, "-y",
        *inputs_cmd,
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        xfade_video
    ]
    res = subprocess.run(cmd_xfade, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] xfade complex filter fallback to direct concat:", res.stderr, flush=True)
        concat_txt = os.path.join(OUTPUT_DIR, "clips_concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in clip_paths:
                f.write(f"file '{c}'\n")
        cmd_fallback = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", xfade_video]
        subprocess.run(cmd_fallback, capture_output=True)
        
    print("  [✓] Dissolve transitions applied successfully!", flush=True)
    return xfade_video

def assemble_final_master(video_track, master_audio):
    print("\n[4/4] 🚀 Multiplexing Multi-Voice Hindi Dialogue with 60 FPS Interpolation...", flush=True)
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_1min_premium_60fps.mp4")
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_track,
        "-i", master_audio,
        "-filter_complex", "[0:v]fps=fps=60[v60]",
        "-map", "[v60]",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "44100",
        "-shortest",
        final_output
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] Multiplexing error:", res.stderr, flush=True)
        return None
        
    print(f"\n🎉 MASTER 1-MINUTE 60 FPS REEL PRODUCED SUCCESSFULLY!\nOutput Path: {final_output}", flush=True)
    return final_output

async def main():
    print("="*75)
    print("🌟 1-MINUTE 'SCHOOL BACKPACK SQUAD' 60 FPS DISNEY PIXAR 3D REEL PIPELINE 🌟")
    print("="*75, flush=True)
    
    master_audio, durations = await generate_multivoice_audio()
    clip_paths = await generate_scene_videos(durations)
    
    if len(clip_paths) == len(SCENES):
        video_track = build_dissolve_transitions(clip_paths, durations)
        final_file = assemble_final_master(video_track, master_audio)
        if final_file:
            print(f"\n[DONE] Reel ready at: {final_file}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
