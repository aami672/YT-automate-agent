import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
VIDEO = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\backpack_squad_zero_jitter.mp4"
OUT_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\extracted_frames"
os.makedirs(OUT_DIR, exist_ok=True)

timestamps = [2, 5, 8, 12, 16, 20, 24, 28, 32, 36]
for t in timestamps:
    out_img = os.path.join(OUT_DIR, f"frame_{t:02d}s.jpg")
    cmd = [
        FFMPEG, "-y",
        "-ss", str(t),
        "-i", VIDEO,
        "-frames:v", "1",
        "-q:v", "2",
        out_img
    ]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(out_img):
        print(f"[+] Frame extracted at {t}s -> {out_img}")
