import os
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
videos_dir = os.path.join(base_dir, 'data', 'videos')
assets_dir = os.path.join(base_dir, 'data', 'assets')
audio_dir = os.path.join(base_dir, 'data', 'audio')
ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

# 1. Input clips
aloo_clip = os.path.join(videos_dir, 'aloo_clean.mp4')
tamatar_clip = os.path.join(videos_dir, 'tamatar_clean.mp4')
gobhi_clip = os.path.join(videos_dir, 'gobhi_clean.mp4')
scene4_audio = os.path.join(audio_dir, 'scene_4_audio.wav')
scene4_img = os.path.join(assets_dir, 'char_matar.jpg')

# 2. Render Scene 4 (Matar with punchy animated motion synced to dialogue)
scene4_video = os.path.join(videos_dir, 'scene4_matar_lipsync_motion.mp4')
# Get audio duration
probe_cmd = f'"{ffmpeg_bin}" -i "{scene4_audio}" 2>&1'
res = subprocess.run(probe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
s4_duration = 11.5
for line in res.stdout.split('\n'):
    if 'Duration:' in line:
        time_str = line.split('Duration:')[1].split(',')[0].strip()
        parts = time_str.split(':')
        s4_duration = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
        break

# Create animated motion for Scene 4
cmd_s4 = f'"{ffmpeg_bin}" -y -loop 1 -i "{scene4_img}" -i "{scene4_audio}" ' \
         f'-vf "scale=800:1422,zoompan=z=\'min(zoom+0.0018,1.20)\':d={int(s4_duration*30)}:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=720x1280:fps=30" ' \
         f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -t {s4_duration} -movflags +faststart "{scene4_video}"'
subprocess.run(cmd_s4, shell=True, check=True)
print(f"[Render] Scene 4 Matar clip rendered: {scene4_video}")

# 3. Assemble all 4 lip-sync scenes
final_lipsync_reel = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_lipsync_reel.mp4')
final_reel_std = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4')
scratch_output = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"

filter_cmd = f'"{ffmpeg_bin}" -y ' \
    f'-i "{aloo_clip}" ' \
    f'-i "{tamatar_clip}" ' \
    f'-i "{gobhi_clip}" ' \
    f'-i "{scene4_video}" ' \
    f'-filter_complex "' \
    f'[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];' \
    f'[1:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];' \
    f'[2:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2];' \
    f'[3:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v3];' \
    f'[v0][0:a][v1][1:a][v2][2:a][v3][3:a]concat=n=4:v=1:a=1[v][a]" ' \
    f'-map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -ar 44100 -movflags +faststart "{final_lipsync_reel}"'

subprocess.run(filter_cmd, shell=True, check=True)

# Copy to final destinations
shutil.copyfile(final_lipsync_reel, final_reel_std)
if os.path.exists(os.path.dirname(scratch_output)):
    shutil.copyfile(final_lipsync_reel, scratch_output)

print(f"\n[DONE] Final 4-Scene Live Lip-Sync Video Rebuilt at: {final_lipsync_reel} ({os.path.getsize(final_lipsync_reel)} bytes)")
