import os
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
videos_dir = os.path.join(base_dir, 'data', 'videos')
audio_dir = os.path.join(base_dir, 'data', 'audio')
ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

# 1. Check all 4 locked multi-character scene audio files
scene_audios = [
    os.path.join(audio_dir, 'scene_1_audio.wav'), # Aloo: hi-IN-MadhurNeural
    os.path.join(audio_dir, 'scene_2_audio.wav'), # Tamatar: hi-IN-MadhurNeural (+15% rate, tapori)
    os.path.join(audio_dir, 'scene_3_audio.wav'), # Aloo + Gobhi (hi-IN-SwaraNeural female voice)
    os.path.join(audio_dir, 'scene_4_audio.wav')  # Matar (hi-IN-SwaraNeural sassy) + Narrator
]

print("Checking locked multi-character scene audios:")
for i, a in enumerate(scene_audios, 1):
    print(f"Scene {i} Audio: {a} (Exists: {os.path.exists(a)})")

# 2. Concat the locked multi-character audio tracks into one seamless master soundtrack
master_audio = os.path.join(audio_dir, 'master_multicharacter_soundtrack.wav')
in_args = " ".join([f'-i "{a}"' for a in scene_audios])
filter_complex = "".join([f'[{i}:a]' for i in range(len(scene_audios))]) + f'concat=n={len(scene_audios)}:v=0:a=1[a]'
cmd_audio_concat = f'"{ffmpeg_bin}" -y {in_args} -filter_complex "{filter_complex}" -map "[a]" -ar 44100 -ac 2 "{master_audio}"'
subprocess.run(cmd_audio_concat, shell=True, check=True)
print(f"[Audio] Master Multi-Character Soundtrack compiled: {master_audio}")

# 3. Source Agnes animated visual video
# Let's use the animated video from ai_reels_project or data/videos
source_agnes_vid = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"
if not os.path.exists(source_agnes_vid):
    source_agnes_vid = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_agnes_animated.mp4')

temp_output = os.path.join(videos_dir, 'temp_multichar_reel.mp4')
final_output = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4')
final_output_agnes = os.path.join(videos_dir, 'jab_aloo_ko_hua_gobhi_se_pyar_agnes_animated.mp4')
final_output_scratch = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"

# 4. Mux the animated video stream with the locked multi-character audio soundtrack
cmd_mux = f'"{ffmpeg_bin}" -y -i "{source_agnes_vid}" -i "{master_audio}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart "{temp_output}"'
subprocess.run(cmd_mux, shell=True, check=True)

# Replace target files
shutil.copyfile(temp_output, final_output)
shutil.copyfile(temp_output, final_output_agnes)
if os.path.exists(os.path.dirname(final_output_scratch)):
    shutil.copyfile(temp_output, final_output_scratch)
if os.path.exists(temp_output):
    os.remove(temp_output)

print(f"\n[SUCCESS] Agnes fully animated video now has the exact locked multi-character voices!")
print(f"1. Aloo: Emotional Male Voice (hi-IN-MadhurNeural)")
print(f"2. Tamatar: Tapori Villain Voice (hi-IN-MadhurNeural Fast/Pitch)")
print(f"3. Gobhi: Sweet Giggly Female Voice (hi-IN-SwaraNeural)")
print(f"4. Matar: Sassy Voice (hi-IN-SwaraNeural High-Pitch)")
print(f"5. Narrator: Clear CTA Voice (hi-IN-MadhurNeural)")
print(f"Output File: {final_output} ({os.path.getsize(final_output)} bytes)")
