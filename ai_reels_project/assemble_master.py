import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
WORK_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.working_dir\20260930_163325_af4236827260"
OUTPUT_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output"
AUDIO_FILE = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\audio_tracks\master_multivoice.mp3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("[*] Assembling Perfect 3D Reel with Correct Characters & Multi-Voice Dialogue...")

# 1. Create concat list
concat_list = os.path.join(WORK_DIR, "concat_fixed.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for i in range(4):
        f.write(f"file 'para_{i}/video.mp4'\n")

# 2. Concat silent video
silent_video = os.path.join(WORK_DIR, "final_silent_fixed.mp4")
cmd_concat = [
    FFMPEG, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", "concat_fixed.txt",
    "-c", "copy",
    "final_silent_fixed.mp4"
]
print("[*] Step 1: Concatenating 4 Scene Videos...")
subprocess.run(cmd_concat, cwd=WORK_DIR, check=True)

# 3. Multiplex with multi-character voice track
final_output = os.path.join(OUTPUT_DIR, "backpack_squad_perfect_3d_reel.mp4")
cmd_merge = [
    FFMPEG, "-y",
    "-i", silent_video,
    "-i", AUDIO_FILE,
    "-c:v", "libx264",
    "-preset", "faster",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    final_output
]
print("[*] Step 2: Multiplexing Multi-Voice Hindi Audio...")
subprocess.run(cmd_merge, check=True)
size_mb = os.path.getsize(final_output) / (1024 * 1024)
print(f"[+] Master 3D Reel Generated: {final_output} ({size_mb:.2f} MB)")

# 4. Generate 60 FPS Ultra-Fluid Version
final_60fps = os.path.join(OUTPUT_DIR, "backpack_squad_perfect_3d_reel_60fps.mp4")
cmd_60 = [
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
print("[*] Step 3: Interpolating to Smooth 60 FPS...")
subprocess.run(cmd_60, check=True)
size_60 = os.path.getsize(final_60fps) / (1024 * 1024)
print(f"[🎉] COMPLETE! 60 FPS Video Generated: {final_60fps} ({size_60:.2f} MB)")
