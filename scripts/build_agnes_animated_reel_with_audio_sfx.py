import os
import sys
import asyncio
import subprocess
import wave
import struct
import math
import numpy as np
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"C:\Users\Amar's PC\Documents\Youtube Automation\youtube-automation-agent"
agnes_working_dir = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.working_dir\20260927_221255_15124c16b160"
audio_dir = os.path.join(base_dir, 'data', 'audio')
videos_dir = os.path.join(base_dir, 'data', 'videos')
sfx_dir = os.path.join(audio_dir, 'sfx')
os.makedirs(sfx_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)

ffmpeg_bin = os.path.join(base_dir, 'node_modules', 'ffmpeg-static', 'ffmpeg.exe')

# Exact durations of the Agnes animated video clips
scene_durations = [11.05, 10.04, 13.19, 9.09]
total_duration = sum(scene_durations) # 43.37s

scene_offsets = [
    0.0,
    scene_durations[0], # 11.05
    scene_durations[0] + scene_durations[1], # 21.09
    scene_durations[0] + scene_durations[1] + scene_durations[2] # 34.28
]

print(f"Total Video Duration: {total_duration:.2f}s across 4 animated scenes")
print(f"Scene Offsets: {scene_offsets}")

# Step 1: Generate All Locked Multi-Character Dialogues with Exact Timings
dialogues = [
    # Scene 1: Romantic Aloo
    {
        'id': 's1_aloo',
        'voice': 'hi-IN-MadhurNeural',
        'rate': '+0%',
        'pitch': '+0Hz',
        'text': 'गोभी जी! जब से आपको सब्ज़ी मंडी में देखा है, मेरा दिल सिर्फ आपके लिए धड़कता है! मैं आपके बिना नहीं रह सकता!',
        'start_time': 0.3
    },
    # Scene 2: Tamatar Villain
    {
        'id': 's2_tamatar',
        'voice': 'hi-IN-MadhurNeural',
        'rate': '+15%',
        'pitch': '+6Hz',
        'text': 'ओए गोलू आलू! साइड हट! गोभी तो सिर्फ मेरी बनेगी! देख मेरा लाल रंग और ग्लो... तेरे जैसा बोरिंग नहीं हूँ मैं!',
        'start_time': scene_offsets[1] + 0.3 # 11.35s
    },
    # Scene 3: Aloo & Gobhi Argument
    {
        'id': 's3_aloo',
        'voice': 'hi-IN-MadhurNeural',
        'rate': '+10%',
        'pitch': '-2Hz',
        'text': 'अरे टमाटर भाई, तुम तो दो दिन में गल जाओगे... मैं आलू हूँ, हर डिश में साथ निभाता हूँ!',
        'start_time': scene_offsets[2] + 0.3 # 21.39s
    },
    {
        'id': 's3_gobhi',
        'voice': 'hi-IN-SwaraNeural',
        'rate': '+5%',
        'pitch': '+5Hz',
        'text': 'हाय राम! पर मैं तो सिर्फ मटर जी के साथ जोड़ी बनाती हूँ!',
        'start_time': scene_offsets[2] + 7.5 # 28.59s
    },
    # Scene 4: Matar Twist & Narrator
    {
        'id': 's4_matar',
        'voice': 'hi-IN-SwaraNeural',
        'rate': '+20%',
        'pitch': '+10Hz',
        'text': 'चलो हटो सब, आलू-गोभी नहीं, अब मटर-पनीर और गोभी-मटर का ज़माना है!',
        'start_time': scene_offsets[3] + 0.3 # 34.58s
    },
    {
        'id': 's4_narrator',
        'voice': 'hi-IN-MadhurNeural',
        'rate': '+10%',
        'pitch': '+0Hz',
        'text': 'आपकी पसंदीदा सब्ज़ी कौन सी है? कमेंट में बताओ और फॉलो करो!',
        'start_time': scene_offsets[3] + 5.0 # 39.28s
    }
]

async def generate_speech():
    print("\n--- Generating Neural Spoken Dialogues ---")
    for d in dialogues:
        out_mp3 = os.path.join(audio_dir, f"{d['id']}.mp3")
        out_wav = os.path.join(audio_dir, f"{d['id']}.wav")
        communicate = edge_tts.Communicate(d['text'], d['voice'], rate=d['rate'], pitch=d['pitch'])
        await communicate.save(out_mp3)
        # Convert to 44.1kHz wav
        subprocess.run(f'"{ffmpeg_bin}" -y -i "{out_mp3}" -ar 44100 -ac 2 "{out_wav}"', shell=True, check=True)
        d['wav_path'] = out_wav
        print(f"Generated {d['id']} -> {out_wav} (starts at {d['start_time']:.2f}s)")

# Step 2: Synthesize Rich High Quality Sound Effects (SFX) and Background Music (BGM)
def generate_audio_elements():
    sr = 44100
    print("\n--- Synthesizing Sound Effects & Ambiance ---")
    
    # 1. Market Ambiance (subtle low-level bustling texture)
    amb_len = int(total_duration * sr)
    amb = np.zeros(amb_len, dtype=np.float32)
    t = np.linspace(0, total_duration, amb_len, endpoint=False)
    # Gentle pink noise filter with harmonic undertones
    white = np.random.normal(0, 0.02, amb_len).astype(np.float32)
    for f in [120, 240, 360, 520]:
        white += 0.005 * np.sin(2 * np.pi * f * t)
    amb = np.convolve(white, np.ones(50)/50, mode='same')
    
    # 2. Romantic Chime / Sparkle (Scene 1 Aloo - 0.5s)
    chime_len = int(2.5 * sr)
    chime = np.zeros(chime_len, dtype=np.float32)
    chime_t = np.linspace(0, 2.5, chime_len, endpoint=False)
    for idx, freq in enumerate([523.25, 659.25, 783.99, 1046.50, 1318.51]): # C Major arpeggio
        st = idx * 0.15
        mask = chime_t >= st
        chime[mask] += 0.15 * np.sin(2 * np.pi * freq * (chime_t[mask] - st)) * np.exp(-3.0 * (chime_t[mask] - st))

    # 3. Comedic Whoosh / Swag Slide (Scene 2 Tamatar - 11.1s)
    whoosh_len = int(1.2 * sr)
    whoosh_t = np.linspace(0, 1.2, whoosh_len, endpoint=False)
    f_inst = np.linspace(150, 600, whoosh_len) # pitch sweep up
    whoosh = 0.25 * np.sin(2 * np.pi * f_inst * whoosh_t) * np.sin(np.pi * whoosh_t / 1.2)**2
    # Add wind noise texture
    whoosh += 0.1 * np.random.normal(0, 0.05, whoosh_len) * np.sin(np.pi * whoosh_t / 1.2)

    # 4. Comic Boing / Argument Pop (Scene 3 - 21.2s and 27.5s)
    boing_len = int(1.0 * sr)
    boing_t = np.linspace(0, 1.0, boing_len, endpoint=False)
    f_boing = 220.0 + 120.0 * np.sin(2 * np.pi * 15 * boing_t)
    boing = 0.25 * np.sin(2 * np.pi * f_boing * boing_t) * np.exp(-4.0 * boing_t)

    # 5. Dramatic Record Scratch / Twist Sting (Scene 4 Matar Entry - 34.3s)
    twist_len = int(1.5 * sr)
    twist_t = np.linspace(0, 1.5, twist_len, endpoint=False)
    # Scratch sweep down then punch
    f_twist = np.linspace(800, 120, twist_len)
    twist = 0.3 * np.sin(2 * np.pi * f_twist * twist_t) * np.exp(-2.5 * twist_t)
    # Sunglass Sparkle / Swag Chime
    for f in [1200, 1600, 2400]:
        twist += 0.12 * np.sin(2 * np.pi * f * twist_t) * np.exp(-5.0 * twist_t)

    # 6. Cheerful Outro Bells (Scene 4 CTA - 39.0s to end)
    bell_len = int(4.0 * sr)
    bell_t = np.linspace(0, 4.0, bell_len, endpoint=False)
    bell = np.zeros(bell_len, dtype=np.float32)
    for idx, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        st = idx * 0.4
        mask = bell_t >= st
        bell[mask] += 0.18 * np.sin(2 * np.pi * f * (bell_t[mask] - st)) * np.exp(-2.0 * (bell_t[mask] - st))

    # 7. Whimsical Bouncy BGM (Full Track: acoustic marimba & comedy chord progression)
    bgm = np.zeros(amb_len, dtype=np.float32)
    # Tempo = 120 BPM -> 0.5s per beat
    beat_dur = 0.5
    total_beats = int(total_duration / beat_dur) + 2
    # Comedy chord progression in C Major / G Major: C - Am - F - G
    chords = [
        [261.63, 329.63, 392.00], # C
        [220.00, 261.63, 329.63], # Am
        [174.61, 220.00, 261.63], # F
        [196.00, 246.94, 293.66], # G
    ]
    for b in range(total_beats):
        chord = chords[(b // 4) % len(chords)]
        beat_start = b * beat_dur
        b_idx = int(beat_start * sr)
        b_len = int(beat_dur * sr)
        if b_idx + b_len > amb_len:
            b_len = amb_len - b_idx
        if b_len <= 0:
            break
        bt = np.linspace(0, b_len / sr, b_len, endpoint=False)
        # Bouncy bass note
        bass_note = chord[0] / 2.0
        bass_wave = 0.12 * np.sin(2 * np.pi * bass_note * bt) * np.exp(-5.0 * bt)
        # Marimba syncopated melody
        m_note = chord[b % 3] * (2.0 if b % 2 == 1 else 1.0)
        m_wave = 0.10 * np.sin(2 * np.pi * m_note * bt) * np.exp(-8.0 * bt)
        # Playful woodblock / perc tick
        tick = 0.05 * np.sin(2 * np.pi * 900 * bt) * np.exp(-40.0 * bt)
        
        bgm[b_idx:b_idx+b_len] += (bass_wave + m_wave + tick)

    # Master Sound Design Assembly
    master_sfx = np.zeros(amb_len, dtype=np.float32)
    # Add ambiance at 0.15 volume
    master_sfx += 0.15 * amb
    # Add BGM at 0.20 volume
    master_sfx += 0.22 * bgm

    # Place SFX at exact cue times
    def overlay_sfx(sound, start_sec, vol=1.0):
        start_sample = int(start_sec * sr)
        end_sample = min(amb_len, start_sample + len(sound))
        snd_len = end_sample - start_sample
        if snd_len > 0:
            master_sfx[start_sample:end_sample] += sound[:snd_len] * vol

    overlay_sfx(chime, 0.5, vol=0.6)
    overlay_sfx(whoosh, scene_offsets[1] + 0.1, vol=0.7)
    overlay_sfx(boing, scene_offsets[2] + 0.1, vol=0.6)
    overlay_sfx(boing, scene_offsets[2] + 7.2, vol=0.5)
    overlay_sfx(twist, scene_offsets[3] + 0.1, vol=0.8)
    overlay_sfx(bell, scene_offsets[3] + 4.8, vol=0.6)

    # Save SFX & BGM Master Audio
    sfx_wav = os.path.join(sfx_dir, "master_bgm_and_sfx.wav")
    master_sfx_norm = np.clip(master_sfx, -0.95, 0.95)
    sfx_int16 = (master_sfx_norm * 32767).astype(np.int16)
    
    with wave.open(sfx_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        # Make stereo
        stereo_data = np.column_stack((sfx_int16, sfx_int16)).flatten()
        wf.writeframes(stereo_data.tobytes())
    
    print(f"BGM & SFX Master Audio compiled: {sfx_wav}")
    return sfx_wav

def compose_final_master_soundtrack(bgm_sfx_path):
    print("\n--- Mixing Dialogue with BGM & Sound Effects ---")
    master_soundtrack = os.path.join(audio_dir, "agnes_master_animated_soundtrack.wav")
    
    # Construct ffmpeg filter_complex to place each dialogue at exact timestamp and mix with BGM/SFX
    inputs = [f'-i "{bgm_sfx_path}"']
    for d in dialogues:
        inputs.append(f'-i "{d["wav_path"]}"')
    
    in_str = " ".join(inputs)
    
    # Delay each dialogue to its exact start_time in milliseconds
    filter_chains = ["[0:a]volume=1.0[bgm_sfx]"]
    mix_sources = ["[bgm_sfx]"]
    
    for idx, d in enumerate(dialogues, 1):
        del_ms = int(d['start_time'] * 1000)
        filter_chains.append(f"[{idx}:a]aresample=44100,adelay={del_ms}|{del_ms},volume=1.8[dia_{idx}]")
        mix_sources.append(f"[dia_{idx}]")
    
    total_inputs = len(dialogues) + 1
    mix_str = "".join(mix_sources) + f"amix=inputs={total_inputs}:duration=first:dropout_transition=0,volume=1.2[aout]"
    full_filter = ";".join(filter_chains) + ";" + mix_str
    
    cmd = f'"{ffmpeg_bin}" -y {in_str} -filter_complex "{full_filter}" -map "[aout]" -ar 44100 -ac 2 "{master_soundtrack}"'
    subprocess.run(cmd, shell=True, check=True)
    print(f"Master Soundtrack Mixed: {master_soundtrack}")
    return master_soundtrack

def mux_with_agnes_animated_video(master_audio):
    print("\n--- Muxing with Agnes 3D Animated Video Sequence ---")
    source_video = os.path.join(agnes_working_dir, "final_video.mp4")
    out_video = os.path.join(videos_dir, "jab_aloo_ko_hua_gobhi_se_pyar_agnes_animated.mp4")
    final_reel = os.path.join(videos_dir, "jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4")
    final_story = os.path.join(videos_dir, "final_aloo_tamatar_gobhi_story.mp4")
    scratch_out = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output\agnes_final_3d_reel.mp4"
    brain_out = r"C:\Users\Amar's PC\.gemini\antigravity\brain\e0b5b209-d2ea-49be-a472-855741d1672a\agnes_final_3d_reel.mp4"
    
    temp_target = os.path.join(videos_dir, "temp_agnes_mux.mp4")
    
    # Mux video with master soundtrack
    cmd_mux = f'"{ffmpeg_bin}" -y -i "{source_video}" -i "{master_audio}" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest "{temp_target}"'
    subprocess.run(cmd_mux, shell=True, check=True)
    
    import shutil
    shutil.copyfile(temp_target, out_video)
    shutil.copyfile(temp_target, final_reel)
    shutil.copyfile(temp_target, final_story)
    shutil.copyfile(temp_target, scratch_out)
    shutil.copyfile(temp_target, brain_out)
    if os.path.exists(temp_target): os.remove(temp_target)
    
    print("\n=======================================================")
    print("🎉 FULLY ANIMATED AGNES VIDEO WITH BGM & SFX COMPLETE!")
    print("=======================================================")
    print(f"Output File: {final_reel}")
    print(f"File Size: {os.path.getsize(final_reel)} bytes")
    print(f"Duration: {total_duration:.2f}s (832x1088 30 FPS)")

async def main():
    await generate_speech()
    sfx_path = generate_audio_elements()
    soundtrack = compose_final_master_soundtrack(sfx_path)
    mux_with_agnes_animated_video(soundtrack)

if __name__ == '__main__':
    asyncio.run(main())
