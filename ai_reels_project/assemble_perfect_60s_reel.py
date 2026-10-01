import os
import sys
import subprocess
import asyncio
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
AI_REELS_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
OUTPUT_DIR = os.path.join(AI_REELS_DIR, "output")
AUDIO_DIR = os.path.join(AI_REELS_DIR, "audio_tracks")
CLIPS_DIR = os.path.join(AI_REELS_DIR, "scene_clips")

SCENE_SCRIPTS = [
    {
        "index": 0,
        "name": "Pencil_Intro",
        "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई एकदम तैयार हैं, आज तो क्लास में पूरे दस में से दस मार्क्स लेकर ही मानेंगे!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+6%",
        "pitch": "+3Hz"
    },
    {
        "index": 1,
        "name": "Eraser_Panicking",
        "text": "अरे पेंसिल भाई धीरे लिखो! तुम गलतियां करोगे और मुझे घिसना पड़ेगा, मेरी तो कमर टूट जाएगी!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+4%",
        "pitch": "+15Hz"
    },
    {
        "index": 2,
        "name": "Sharpener_Hero",
        "text": "चिंता मत करो इरेज़र बाबू! जब तक शार्पनर यहाँ है, पेंसिल की नोक रॉकेट की तरह शार्प रहेगी, लिखाई एकदम मक्खन!",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+7%",
        "pitch": "+8Hz"
    },
    {
        "index": 3,
        "name": "Ruler_Superhero",
        "text": "शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, एक भी लाइन टेढ़ी नहीं होगी, हर डायग्राम बिल्कुल सीधा और परफेक्ट!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "pitch": "-8Hz"
    },
    {
        "index": 4,
        "name": "Squad_Teamwork",
        "text": "देखा इसे कहते हैं बैकपैक स्क्वाड! लिखना, मिटाना, शार्प करना और सीधी लाइन - सब मिलकर करेंगे टॉप!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+5%",
        "pitch": "+2Hz"
    },
    {
        "index": 5,
        "name": "Outro_CTA",
        "text": "टन-टन-टन! स्कूल की घंटी बजी! आपका सबसे पसंदीदा स्टेशनरी साथी कौन सा है? कमेंट में बताओ और सब्सक्राइब करो!",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+8%",
        "pitch": "+4Hz"
    }
]

async def create_perfect_timed_audio():
    print("[1/3] 🎙️ Creating perfectly timed multi-voice Hindi audio tracks...")
    scene_audios = []
    
    for sc in SCENE_SCRIPTS:
        idx = sc["index"]
        raw_audio = os.path.join(AUDIO_DIR, f"scene_{idx}_raw.mp3")
        padded_audio = os.path.join(AUDIO_DIR, f"scene_{idx}_padded.mp3")
        
        # 1. Generate Voice with edge-tts
        communicate = edge_tts.Communicate(sc["text"], voice=sc["voice"], rate=sc["rate"], pitch=sc["pitch"])
        await communicate.save(raw_audio)
        
        # 2. Get exact duration
        r = subprocess.run([FFMPEG, "-i", raw_audio], capture_output=True, text=True, errors="replace")
        dur = 7.0
        for line in r.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                break
                
        # Target slot for each scene in the final video (crossfaded) is 9.54s (last is 10.04s)
        slot_dur = 9.54 if idx < 5 else 10.04
        pad_dur = max(0.0, slot_dur - dur)
        
        # Pad with silence to maintain perfect scene synchronization across cuts
        cmd_pad = [
            FFMPEG, "-y",
            "-i", raw_audio,
            "-af", f"apad=pad_dur={pad_dur:.2f}",
            "-t", f"{slot_dur:.2f}",
            padded_audio
        ]
        subprocess.run(cmd_pad, capture_output=True)
        scene_audios.append(padded_audio)
        print(f"  [+] Scene {idx} ({sc['name']}): Speech={dur:.2f}s | Target={slot_dur:.2f}s (Padded silence: {pad_dur:.2f}s)")
        
    # Concat all 6 padded audio clips
    concat_txt = os.path.join(AUDIO_DIR, "synced_audio_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in scene_audios:
            rel = os.path.basename(p)
            f.write(f"file '{rel}'\n")
            
    master_dialogue = os.path.join(AUDIO_DIR, "master_dialogue_synced.mp3")
    cmd_concat = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "synced_audio_concat.txt", "-c", "copy", master_dialogue]
    subprocess.run(cmd_concat, cwd=AUDIO_DIR, capture_output=True)
    
    print(f"  [✓] Master Dialogue track created: {master_dialogue}")
    return master_dialogue

def build_dissolve_video():
    print("\n[2/3] ✨ Stitching 6 Scenes with 0.5s Smooth Dissolve Crossfades...")
    clips = [os.path.join(CLIPS_DIR, f"scene_{i}.mp4") for i in range(6)]
    for c in clips:
        if not os.path.exists(c):
            raise FileNotFoundError(f"Missing clip: {c}")
            
    # Clip duration is 10.04s each
    # Transition duration = 0.5s
    # Offsets:
    # Cut 1: 10.04 - 0.5 = 9.54s
    # Cut 2: 9.54 + 9.54 = 19.08s
    # Cut 3: 19.08 + 9.54 = 28.62s
    # Cut 4: 28.62 + 9.54 = 38.16s
    # Cut 5: 38.16 + 9.54 = 47.70s
    # Total Video Duration = 47.70 + 10.04 = 57.74s (~1 minute)
    
    filter_complex = (
        "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=9.54[v01];"
        "[v01][2:v]xfade=transition=fade:duration=0.5:offset=19.08[v02];"
        "[v02][3:v]xfade=transition=fade:duration=0.5:offset=28.62[v03];"
        "[v03][4:v]xfade=transition=fade:duration=0.5:offset=38.16[v04];"
        "[v04][5:v]xfade=transition=fade:duration=0.5:offset=47.70[vout]"
    )
    
    xfade_output = os.path.join(OUTPUT_DIR, "master_dissolve_video_58s.mp4")
    inputs = []
    for c in clips:
        inputs.extend(["-i", c])
        
    cmd = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        xfade_output
    ]
    print("  [+] Executing FFmpeg xfade filtergraph...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] xfade failed:", res.stderr)
        raise RuntimeError("xfade failure")
        
    print(f"  [✓] Dissolve Video successfully rendered: {xfade_output}")
    return xfade_output

def produce_final_master_60fps(video_path, dialogue_path):
    print("\n[3/3] 🚀 Multiplexing Full 1-Minute 60 FPS Master Reel...")
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_1min_premium_60fps.mp4")
    
    # We combine video, dialogue audio, apply fps=60, loud 256k AAC stereo
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", dialogue_path,
        "-filter_complex", "[0:v]fps=fps=60[v60];[1:a]volume=1.5,aformat=channel_layouts=stereo[a_loud]",
        "-map", "[v60]",
        "-map", "[a_loud]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "44100",
        "-shortest",
        final_output
    ]
    print("  [+] Final encoding to 60 FPS with boosted crystal clear dialogues...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] Multiplexing error:", res.stderr)
        raise RuntimeError("Final multiplexing failure")
        
    print(f"\n🎉 1-MINUTE 60 FPS MASTER VIDEO SAVED TO:\n{final_output}")
    return final_output

async def main():
    print("="*75)
    print("🌟 ASSEMBLING 1-MINUTE 60 FPS BACKPACK SQUAD MASTER PIXAR REEL 🌟")
    print("="*75)
    
    master_dialogue = await create_perfect_timed_audio()
    video_track = build_dissolve_video()
    final_output = produce_final_master_60fps(video_track, master_dialogue)
    print("\n✅ PRODUCTION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
