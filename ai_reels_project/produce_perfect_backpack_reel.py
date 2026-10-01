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
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Characters and Script Definitions
SCENES = [
    {
        "index": 0,
        "name": "Pencil_Intro",
        "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे 10 में से 10 मार्क्स लेकर ही मानेंगे!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
        "image": os.path.join(BRAIN_DIR, "backpack_scene1_pencil_1790604281443.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cheerful anthropomorphic yellow wooden pencil with large expressive eyes peeking out of a colorful student backpack on a wooden classroom desk. Warm morning sunlight streaming through the windows, soft shadows, steady locked-off cinematic framing with slow gentle push-in, rich textures, perfectly stable 3D character animation."
    },
    {
        "index": 1,
        "name": "Eraser_Panicking",
        "text": "तभी इरेज़र रोते हुए बोला: अरे पेंसिल भाई धीरे लिखो! तुम तो गलतियां करोगे और पूरा घिसना मुझे ही पड़ेगा, मेरी तो कमर टूट जाएगी!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+2%",
        "pitch": "+12Hz",
        "image": os.path.join(BRAIN_DIR, "backpack_scene2_eraser_1790604294471.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A cute chunky pink and white eraser character with comical worried wide eyes and hands on its cheeks, standing on a wooden classroom desk beside an open mathematics notebook. Classroom setting with warm morning light, locked steady camera, smooth breathing motion, rich tactile rubber textures, no white void, perfectly consistent school desk setting."
    },
    {
        "index": 2,
        "name": "Ruler_Superhero",
        "text": "स्केल भाई शान से बोले: शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, क्लास में सब कुछ बिल्कुल सीधा और परफेक्ट रहेगा!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "pitch": "-6Hz",
        "image": os.path.join(BRAIN_DIR, "backpack_scene3_ruler_1790604311264.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. A tall sleek clear plastic ruler character with measurement markings, standing proudly with hands on hips like a superhero on a colorful notebook on the wooden classroom desk. Bright morning sunlight, clear reflections, proud confident expression, locked steady framing, smooth subtle motion, no human characters, no eraser, perfectly rendered clear plastic ruler character."
    },
    {
        "index": 3,
        "name": "Squad_Celebration",
        "text": "तभी स्कूल की घंटी बजी: टन-टन-टन! चलो बैकपैक स्क्वाड, मिशन शुरू! आपका स्कूल में सबसे फेवरेट स्टेशनरी कौन सा था? कमेंट में बताओ!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+6%",
        "pitch": "+3Hz",
        "image": os.path.join(BRAIN_DIR, "backpack_scene4_squad_1790604324147.jpg"),
        "prompt": "A high-quality 3D Pixar animation scene. The entire stationery squad - cute yellow pencil, pink eraser, tall clear ruler, and little blue sharpener celebrating together inside a vibrant open pencil box on the wooden classroom desk. Colorful stationery items, festive morning light, joyful bouncy gestures, wide cinematic framing, no human children, pure 3D animated stationery characters having fun."
    }
]

async def generate_multivoice_audio():
    print("[1/4] 🎙️ Generating Multi-Character Hindi Voiceover Tracks...")
    audio_dir = os.path.join(AI_REELS_DIR, "audio_tracks")
    os.makedirs(audio_dir, exist_ok=True)
    
    audio_files = []
    durations = []
    
    for sc in SCENES:
        out_path = os.path.join(audio_dir, f"scene_{sc['index']}.mp3")
        communicate = edge_tts.Communicate(sc["text"], voice=sc["voice"], rate=sc["rate"], pitch=sc["pitch"])
        await communicate.save(out_path)
        
        # Probe duration
        r = subprocess.run([FFMPEG, "-i", out_path], capture_output=True, text=True, errors="replace")
        dur = 8.0
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
        durations.append(dur)
        audio_files.append(out_path)
        print(f"  [+] Scene {sc['index']} ({sc['name']}): Voice={sc['voice']} (Pitch: {sc['pitch']}, Rate: {sc['rate']}) | Duration: {dur:.2f}s")
        
    # Concat all 4 audio clips into one master audio file
    concat_list = os.path.join(audio_dir, "audio_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for fpath in audio_files:
            rel = os.path.basename(fpath)
            f.write(f"file '{rel}'\n")
            
    master_audio = os.path.join(audio_dir, "master_multivoice.mp3")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_concat.txt", "-c", "copy", master_audio]
    subprocess.run(cmd, cwd=audio_dir, capture_output=True)
    
    # Generate synced SRT subtitle file
    srt_path = os.path.join(audio_dir, "subtitles.srt")
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
            
    print(f"  [+] Master audio and subtitles generated! Total Duration: {current_time:.2f}s")
    return master_audio, srt_path, durations

def submit_and_render_video():
    print("\n[2/4] 🚀 Submitting Fixed & Corrected Scenes to Agnes Video Generator...")
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
        "reference_images_map": json.dumps([[0], [1], [2], [3]]),
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

def assemble_master_reel(work_dir, master_audio, srt_path):
    print("\n[4/4] 🔨 Assembling Master 3D Reel with Multi-Voice Hindi Dialogue...")
    
    # Concat 4 scene videos
    concat_txt = os.path.join(work_dir, "concat_fixed.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for i in range(4):
            f.write(f"file 'para_{i}/video.mp4'\n")
            
    concat_silent = os.path.join(work_dir, "final_fixed_silent.mp4")
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_fixed.txt",
        "-c", "copy",
        "final_fixed_silent.mp4"
    ]
    subprocess.run(cmd_concat, cwd=work_dir, capture_output=True)
    
    # Merge with multi-character master audio
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_perfect_3d_reel.mp4")
    cmd_merge = [
        FFMPEG, "-y",
        "-i", concat_silent,
        "-i", master_audio,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_merge, capture_output=True)
    
    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print(f"\n🎉 PERFECT REEL COMPLETED!")
    print(f"📁 Output Video: {final_output} ({size_mb:.2f} MB)")
    
    # Smooth 60 FPS version
    print("\n⚡ Generating 60 FPS Ultra-Fluid Edition...")
    final_60fps = os.path.join(OUTPUT_DIR, "backpack_squad_perfect_3d_reel_60fps.mp4")
    cmd_60fps = [
        FFMPEG, "-y",
        "-i", final_output,
        "-vf", "framerate=fps=60:interp_start=0:interp_end=255:scene=100,hqdn3d=1.5:1.5:4:4",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-r", "60",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        final_60fps
    ]
    subprocess.run(cmd_60fps, capture_output=True)
    size_60 = os.path.getsize(final_60fps) / (1024 * 1024)
    print(f"📁 60 FPS Output: {final_60fps} ({size_60:.2f} MB)")

async def main():
    master_audio, srt_path, durations = await generate_multivoice_audio()
    work_dir = submit_and_render_video()
    if work_dir and os.path.exists(work_dir):
        assemble_master_reel(work_dir, master_audio, srt_path)

if __name__ == "__main__":
    asyncio.run(main())
