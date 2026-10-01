import os
import sys
import json
import time
import asyncio
import requests
import subprocess
import shutil
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
BRAIN_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\brain\948aeb55-f992-450a-afe5-fdaa77988433"
AI_REELS_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
OUTPUT_DIR = os.path.join(AI_REELS_DIR, "output")
AUDIO_DIR = os.path.join(AI_REELS_DIR, "audio_tracks")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

SCENES = [
    {
        "index": 0,
        "name": "Pencil_Intro",
        "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे दस में से दस मार्क्स लेकर ही मानेंगे!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_pencil_scene1_1790767758092.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cheerful anthropomorphic yellow wooden pencil with large expressive eyes smiling cheerfully on a warm wooden classroom desk beside a colorful backpack. Warm morning sunlight streaming through the windows, soft bokeh, steady locked-off framing, rich 3D textures, zero jitter, zero hallucinations, pure animated character."
    },
    {
        "index": 1,
        "name": "Eraser_Panicking",
        "text": "तभी इरेज़र रोते हुए बोला: अरे पेंसिल भाई धीरे लिखो! तुम तो गलतियां कर-कर के पेज भर दोगे, और पीछे-पीछे मिटाते-मिटाते मेरी कमर घिस जाएगी!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+0%",
        "pitch": "+14Hz",
        "image": os.path.join(BRAIN_DIR, "perfect_eraser_scene2_1790767774858.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute chunky pink eraser character with comical worried wide eyes and hands on its cheeks, standing on a wooden classroom desk beside an open notebook. Classroom setting with warm morning light, steady camera, rich tactile rubber textures, no white void, pure 3D animated character."
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
        "text": "स्केल भाई शान से बोले: शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, एक भी लाइन टेढ़ी नहीं होगी! हर डायग्राम बिल्कुल सीधा और परफेक्ट बनेगा!",
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
        dur = 9.0
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
        durations.append(dur)
        audio_files.append(out_path)
        print(f"  [+] Scene {sc['index']} ({sc['name']}): Voice={sc['voice']} (Pitch: {sc['pitch']}, Rate: {sc['rate']}) | Duration: {dur:.2f}s")
        
    # Concat all 6 audio clips into one master audio file
    concat_list = os.path.join(AUDIO_DIR, "audio_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for fpath in audio_files:
            rel = os.path.basename(fpath)
            f.write(f"file '{rel}'\n")
            
    master_audio = os.path.join(AUDIO_DIR, "master_multivoice.mp3")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_concat.txt", "-c", "copy", master_audio]
    subprocess.run(cmd, cwd=AUDIO_DIR, capture_output=True)
    
    # Generate synced SRT subtitle file
    srt_path = os.path.join(AUDIO_DIR, "subtitles.srt")
    current_time = 0.0
    with open(srt_path, "w", encoding="utf-8") as sf:
        for idx, sc in enumerate(SCENES):
            d = durations[idx]
            start_s = current_time
            end_s = current_time + d
            current_time = end_s
            
            def fmt_time(sec):
                hrs = int(sec // 3600)
                mins = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec - int(sec)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{s:02d},{ms:03d}"
                
            sf.write(f"{idx+1}\n")
            sf.write(f"{fmt_time(start_s)} --> {fmt_time(end_s)}\n")
            sf.write(f"{sc['text']}\n\n")
            
    print(f"  [+] Master multi-voice track and synced subtitles ready! Total Duration: {current_time:.2f}s")
    return master_audio, srt_path, durations

def submit_and_render_video():
    print("\n[2/4] 🚀 Submitting 6 Scenes to Agnes Video Generator...")
    manuscript_text = "\n\n".join(sc["text"] for sc in SCENES)
    scene_prompts = [sc["prompt"] for sc in SCENES]
    
    data = {
        "manuscript_text": manuscript_text,
        "style": "Ultra-stable 3D Pixar Disney animated film style, perfectly locked steady camera, high temporal stability, zero jitter, zero hallucinations",
        "audio_voice": "hi-IN-MadhurNeural",
        "audio_rate": "+0%",
        "audio_lang": "hi-IN",
        "audio_enabled": "true",
        "subtitle_enabled": "true",
        "video_width": "768",
        "video_height": "1152",
        "video_duration": "10",
        "scene_prompts": json.dumps(scene_prompts, ensure_ascii=False),
        "reference_images_map": json.dumps([[0], [1], [2], [3], [4], [5]]),
    }
    
    files = []
    opened_files = []
    try:
        for i, sc in enumerate(SCENES):
            f = open(sc["image"], "rb")
            opened_files.append(f)
            files.append(("reference_images", (f"ref_{i}.jpg", f, "image/jpeg")))
            
        resp = requests.post("http://localhost:8765/api/tasks/manuscript", data=data, files=files, timeout=30)
        res_json = resp.json()
        task_id = res_json.get("task_id")
        dir_name = res_json.get("dir_name")
        print(f"  [+] Submitted Task ID: {task_id} (Dir: {dir_name})")
        
        print("\n[3/4] 🎬 Tracking Video Scene Diffusion to Completion...")
        while True:
            time.sleep(5)
            try:
                t_resp = requests.get(f"http://localhost:8765/api/tasks/{task_id}", timeout=15)
                t_data = t_resp.json()
                status = t_data.get("status")
                step = t_data.get("current_step")
                prog = int((t_data.get("current_progress") or 0) * 100)
                msg = t_data.get("current_message", "")
                print(f"  [{status}] Step: {step} | Progress: {prog}% | {msg}")
                
                if status == "completed":
                    print("  [+] Video clips synthesis completed successfully!")
                    work_dir = os.path.join(r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.working_dir", dir_name)
                    return work_dir
                elif status == "failed":
                    print("[-] Task failed:", t_data.get("error"))
                    return None
            except Exception as e:
                print("  [poll warning]", e)
    finally:
        for f in opened_files:
            f.close()

def build_dissolve_xfade_filter(scene_clips, trans_dur=0.5):
    """
    Builds an FFmpeg complex filtergraph to apply crossfade (xfade) between consecutive clips.
    """
    # Probe duration of each clip
    clip_durations = []
    for c in scene_clips:
        r = subprocess.run([FFMPEG, "-i", c], capture_output=True, text=True, errors="replace")
        dur = 10.0
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
        clip_durations.append(dur)
        
    print(f"  Clip durations for xfade: {clip_durations}")
    
    # Construct filtergraph
    # [0:v][1:v]xfade=transition=fade:duration=0.5:offset=T1[v01];
    # [v01][2:v]xfade=transition=fade:duration=0.5:offset=T2[v02]; etc.
    inputs_cmd = []
    for c in scene_clips:
        inputs_cmd.extend(["-i", c])
        
    n = len(scene_clips)
    filter_chains = []
    current_offset = clip_durations[0] - trans_dur
    prev_label = "0:v"
    
    for i in range(1, n):
        next_label = f"{i}:v"
        out_label = f"v{i}" if i < n - 1 else "vout"
        
        filter_chains.append(
            f"[{prev_label}][{next_label}]xfade=transition=fade:duration={trans_dur}:offset={current_offset:.3f}[{out_label}]"
        )
        prev_label = out_label
        if i < n - 1:
            current_offset += clip_durations[i] - trans_dur
            
    filter_str = ";".join(filter_chains)
    return inputs_cmd, filter_str, (current_offset + clip_durations[-1])

def assemble_master_reel(work_dir, master_audio, srt_path, durations):
    print("\n[4/4] 🔨 Assembling Master 3D Reel with Dissolve Transitions, 60 FPS & Crystal Clear Multi-Voice Hindi Audio...")
    
    scene_clips = [os.path.join(work_dir, f"para_{i}", "video.mp4") for i in range(len(SCENES))]
    for c in scene_clips:
        if not os.path.exists(c):
            print(f"Error: Missing clip {c}")
            return None
            
    # 1. Apply Dissolve Transitions via FFmpeg xfade
    xfade_video = os.path.join(OUTPUT_DIR, "temp_xfade_video.mp4")
    inputs_cmd, filter_str, total_dur = build_dissolve_xfade_filter(scene_clips, trans_dur=0.5)
    
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
    print("  [+] Applying 0.5s Dissolve transitions between scene cuts...")
    res = subprocess.run(cmd_xfade, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] xfade failed, fallback to direct concat:", res.stderr)
        # Fallback to concat
        concat_txt = os.path.join(OUTPUT_DIR, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in scene_clips:
                f.write(f"file '{c}'\n")
        cmd_fallback = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", xfade_video]
        subprocess.run(cmd_fallback, capture_output=True)
        
    # 2. Multiplex with Explicit Master Audio Mapping & 60 FPS
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_1min_premium_60fps.mp4")
    
    # We map video from 0:v:0, audio from 1:a:0, set 60 fps, high bitrate AAC
    cmd_final = [
        FFMPEG, "-y",
        "-i", xfade_video,
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
    print(f"  [+] Multiplexing master audio with 60 FPS interpolation to {final_output}...")
    res_final = subprocess.run(cmd_final, capture_output=True, text=True)
    if res_final.returncode != 0:
        print("[-] Final assembly failed:", res_final.stderr)
        return None
        
    print(f"\n🎉 ALL ISSUES FIXED! Master Video Saved Successfully to:\n{final_output}")
    return final_output

async def main():
    print("🎬 STARTING COMPLETE 1-MINUTE BACKPACK SQUAD REEL PRODUCTION 🎬\n" + "="*70)
    master_audio, srt_path, durations = await generate_multivoice_audio()
    
    work_dir = submit_and_render_video()
    if not work_dir:
        print("[-] Video rendering step did not complete.")
        return
        
    final_path = assemble_master_reel(work_dir, master_audio, srt_path, durations)
    if final_path:
        print(f"\n✨ Video is ready for viewing at: {final_path}")

if __name__ == "__main__":
    asyncio.run(main())
