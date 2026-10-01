import os
import sys
import subprocess
import time

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG_PATH = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
INPUT_VIDEO = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\backpack_squad_3d_reel.mp4"
OUTPUT_VIDEO = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\backpack_squad_3d_reel_smooth_60fps.mp4"

def interpolate_video():
    print(f"[*] Input Video: {INPUT_VIDEO}")
    print(f"[*] Output Video: {OUTPUT_VIDEO}")
    print("[*] Applying Motion Interpolation Filter (MCI Optical Flow 60 FPS)...")
    
    start_time = time.time()
    
    # Motion-compensated optical flow interpolation to 60 FPS
    # mi_mode=mci (motion compensated interpolation)
    # mc_mode=aobmc (adaptive overlapped block motion compensation)
    # me_mode=bidir (bidirectional motion estimation)
    vf_filter = "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", INPUT_VIDEO,
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ]
    
    print("[*] Running FFmpeg command...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    
    for line in proc.stdout:
        if "frame=" in line or "fps=" in line or "time=" in line:
            print(f"\r{line.strip()}", end="", flush=True)
            
    proc.wait()
    elapsed = time.time() - start_time
    
    if proc.returncode == 0 and os.path.exists(OUTPUT_VIDEO):
        size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        print(f"\n[+] Success! Smooth 60 FPS video generated in {elapsed:.1f}s.")
        print(f"[+] Output File: {OUTPUT_VIDEO} ({size_mb:.2f} MB)")
    else:
        print(f"\n[-] FFmpeg failed with return code {proc.returncode}")

if __name__ == "__main__":
    interpolate_video()
