import subprocess
import os

ffmpeg_bin = os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')
vid_path = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"

print("Exists:", os.path.exists(vid_path), "Size:", os.path.getsize(vid_path) if os.path.exists(vid_path) else 0)
cmd = f'"{ffmpeg_bin}" -i "{vid_path}" 2>&1'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(res.stdout)
