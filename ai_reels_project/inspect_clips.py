import subprocess
import os

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
CLIPS_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\scene_clips"

for i in range(6):
    p = os.path.join(CLIPS_DIR, f"scene_{i}.mp4")
    r = subprocess.run([FFMPEG, "-i", p], capture_output=True, text=True, errors="replace")
    for line in r.stderr.split("\n"):
        if "Duration:" in line:
            print(f"Scene {i}: {line.strip()}")
        if "Stream #0:0" in line:
            print(f"  Stream 0: {line.strip()}")
