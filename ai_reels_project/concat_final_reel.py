import os
import sys
import subprocess
import time

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
WORK_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.working_dir\20260929_161303_11c9eecb98cd"
OUTPUT_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("[*] Concatenating 4 Zero-Jitter Video Clips...")
    
    # 1. Create concat list with relative paths
    list_file = os.path.join(WORK_DIR, "concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for i in range(4):
            f.write(f"file 'para_{i}/video.mp4'\n")
            
    concat_silent = os.path.join(WORK_DIR, "final_silent.mp4")
    
    # Concatenate video streams seamlessly
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c", "copy",
        "final_silent.mp4"
    ]
    
    print("[*] Running concat...")
    res1 = subprocess.run(cmd_concat, cwd=WORK_DIR, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res1.returncode != 0:
        print("[-] Concat failed:", res1.stderr)
        return
        
    print("[+] Video concat successful!")
    
    # 2. Merge audio and subtitle
    audio_file = os.path.join(WORK_DIR, "full_narration_vol.mp3")
    if not os.path.exists(audio_file):
        audio_file = os.path.join(WORK_DIR, "full_narration.mp3")
        
    ass_sub = os.path.join(WORK_DIR, "full_subtitle.srt.ass")
    final_output = os.path.join(OUTPUT_DIR, "backpack_squad_zero_jitter.mp4")
    
    # If ASS subtitle exists, burn it in or multiplex
    # Use standard high-quality x264 encode
    cmd_final = [
        FFMPEG, "-y",
        "-i", concat_silent,
        "-i", audio_file,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output
    ]
    
    print("[*] Merging audio and finalizing video...")
    res2 = subprocess.run(cmd_final, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res2.returncode != 0:
        print("[-] Final merge failed:", res2.stderr)
        return
        
    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print(f"\n[🎉] SUCCESS! Zero-Jitter Final Reel Ready!")
    print(f"[+] Output File: {final_output} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
