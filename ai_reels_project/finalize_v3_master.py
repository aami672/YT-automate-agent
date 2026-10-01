import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
AI_REELS_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
OUTPUT_DIR = os.path.join(AI_REELS_DIR, "output")
AUDIO_DIR = os.path.join(AI_REELS_DIR, "audio_tracks")

video_path = os.path.join(OUTPUT_DIR, "v3_master_dissolve_video.mp4")
dialogue_path = os.path.join(AUDIO_DIR, "v3_master_dialogue.mp3")
bgm_path = os.path.join(AUDIO_DIR, "cheerful_cartoon_bgm.wav")
bell_path = os.path.join(AUDIO_DIR, "real_school_bell.wav")
final_output = os.path.join(OUTPUT_DIR, "backpack_squad_1min_premium_60fps.mp4")

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
    "-preset", "fast",
    "-crf", "17",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "256k",
    "-ar", "44100",
    "-shortest",
    final_output
]

print("Executing final 60 FPS master multiplexing...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("[-] Error:", res.stderr)
    sys.exit(1)
else:
    print("[✓] Master Reel successfully multiplexed and verified!")
    print(f"Output: {final_output}")
