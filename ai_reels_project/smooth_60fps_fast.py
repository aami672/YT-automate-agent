import os
import sys
import subprocess
import time

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG_PATH = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
INPUT_VIDEO = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\backpack_squad_3d_reel.mp4"
OUTPUT_VIDEO = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\backpack_squad_3d_reel_smooth_60fps.mp4"

def make_smooth_60fps():
    print(f"[*] Input Video: {INPUT_VIDEO}")
    print(f"[*] Generating Smooth 60 FPS Output: {OUTPUT_VIDEO}")
    
    start_time = time.time()
    
    # framerate filter generates smooth temporal blending & 60fps interpolation without stutter
    vf_filter = "framerate=fps=60:interp_start=0:interp_end=255:scene=100,hqdn3d=1.5:1.5:4:4"
    
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", INPUT_VIDEO,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-r", "60",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    elapsed = time.time() - start_time
    
    if res.returncode == 0 and os.path.exists(OUTPUT_VIDEO):
        size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        print(f"[+] Completed in {elapsed:.1f}s!")
        print(f"[+] 60 FPS Smooth Video Saved to: {OUTPUT_VIDEO} ({size_mb:.2f} MB)")
    else:
        print("[-] Error:", res.stderr[-500:])

if __name__ == "__main__":
    make_smooth_60fps()
