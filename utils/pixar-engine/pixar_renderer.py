"""
Universal Pixar 3D Animated Video Renderer (V3 Engine)
Exact generation sequence and format ported from ai_reels_project:
- Multi-character high-pitch cartoon TTS voices (custom pitch/rate per character)
- apad per-scene audio alignment & slot padding (9.54s / 10.04s)
- Realistic physical school bell chime SFX synthesis (numpy inharmonic modal frequencies)
- Upbeat 124 BPM Disney/Pixar acoustic cartoon BGM (Marimba, Ukulele, Glockenspiel in C-G-Am-F major)
- 3D reference character images loading & strict 720x1280 (9:16 vertical) normalization
- Cinematic dissolve crossfades (xfade=transition=fade) with intro fade-in and outro fade-out
- Master multi-track audio mixing ([a_diag][a_bgm][a_bell]amix) and progressive 60 FPS H.264 MP4 delivery.
"""

import sys
import os
import json
import math
import wave
import struct
import asyncio
import subprocess
import argparse
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Ensure UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Find verified high-performance ffmpeg binary
def get_ffmpeg_path():
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # 1. Check verified high-performance FFmpeg 7.1 build
    scratch_ffmpeg = Path("C:/Users/Amar's PC/.gemini/antigravity/scratch/agnes-video-generator/.venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")
    if scratch_ffmpeg.exists():
        return str(scratch_ffmpeg)

    # 2. Check node_modules/ffmpeg-static
    node_static = Path(__file__).resolve().parent.parent.parent / "node_modules" / "ffmpeg-static" / "ffmpeg.exe"
    if node_static.exists():
        return str(node_static)
    
    return "ffmpeg"

FFMPEG = get_ffmpeg_path()

def run_cmd(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if p.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}\nError: {p.stderr}", file=sys.stderr, flush=True)
    return p.returncode == 0

def get_media_duration(file_path):
    cmd = [FFMPEG, "-i", str(file_path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    for line in p.stderr.split("\n"):
        if "Duration:" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            except Exception:
                pass
    return 0.0

def create_physical_school_bell(output_path, duration=4.0, sample_rate=44100):
    """
    Synthesize authentic electric school gong bell with mechanical hammer
    and inharmonic brass/steel bell modal frequencies.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    bell_wave = np.zeros_like(t)
    
    modes = [
        (910.0, 0.40, 1.2),
        (1320.0, 0.35, 1.5),
        (1840.0, 0.25, 2.0),
        (2610.0, 0.18, 2.5),
        (3580.0, 0.12, 3.2),
        (4920.0, 0.08, 4.0),
        (6400.0, 0.05, 5.0)
    ]
    
    ring_duration = 1.8
    hammer_freq = 16.5
    num_strikes = int(ring_duration * hammer_freq)
    
    for i in range(num_strikes):
        t_strike = i / hammer_freq
        mask = t >= t_strike
        dt = t[mask] - t_strike
        
        clapper = 0.3 * np.exp(-dt * 200.0) * (np.sin(2 * np.pi * 3200 * dt) + 0.5 * np.random.randn(len(dt)))
        bell_wave[mask] += clapper * 0.2
        
        for freq, amp, decay_rate in modes:
            f_detuned = freq + np.random.uniform(-3, 3)
            mode_sig = amp * np.sin(2 * np.pi * f_detuned * dt) * np.exp(-dt * (decay_rate * 3.5))
            bell_wave[mask] += mode_sig * 0.15

    mask_sustain = t >= ring_duration
    dt_sustain = t[mask_sustain] - ring_duration
    for freq, amp, decay_rate in modes:
        sustain_sig = (amp * 0.6) * np.sin(2 * np.pi * freq * dt_sustain) * np.exp(-dt_sustain * 1.4)
        sustain_sig *= (1.0 + 0.25 * np.sin(2 * np.pi * 4.5 * dt_sustain))
        bell_wave[mask_sustain] += sustain_sig

    max_amp = np.max(np.abs(bell_wave))
    if max_amp > 0:
        bell_wave = (bell_wave / max_amp) * 0.90
        
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        int_data = (bell_wave * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    return output_path

def create_cheerful_cartoon_bgm(output_path, total_duration=65.0, sample_rate=44100):
    """
    Synthesize upbeat 124 BPM Disney/Pixar acoustic cartoon BGM with
    Marimba, Ukulele strumming, Tuba pluck, and shakers in C-G-Am-F.
    """
    t = np.linspace(0, total_duration, int(sample_rate * total_duration), endpoint=False)
    bgm_audio = np.zeros_like(t)
    
    bpm = 124.0
    beat_dur = 60.0 / bpm
    
    NOTE_C4 = 261.63
    NOTE_E4 = 329.63
    NOTE_G4 = 392.00
    NOTE_A4 = 440.00
    NOTE_B4 = 493.88
    NOTE_C5 = 523.25
    NOTE_D5 = 587.33
    NOTE_E5 = 659.25
    NOTE_F5 = 698.46
    NOTE_G5 = 783.99
    NOTE_A5 = 880.00
    
    chords = [
        [NOTE_C4, NOTE_E4, NOTE_G4, NOTE_C5],
        [NOTE_G4, NOTE_B4, NOTE_D5, NOTE_G5],
        [NOTE_A4, NOTE_C5, NOTE_E5, NOTE_A5],
        [NOTE_C4 * (4.0/3.0), NOTE_A4, NOTE_C5, NOTE_F5],
    ]
    
    total_beats = int(total_duration / beat_dur)
    
    for beat in range(total_beats):
        t_beat = beat * beat_dur
        chord_idx = (beat // 4) % len(chords)
        chord = chords[chord_idx]
        
        # 1. Bass / Tuba pluck on downbeat
        if beat % 2 == 0:
            root_freq = chord[0] / 2.0
            mask = (t >= t_beat) & (t < t_beat + beat_dur * 1.5)
            dt = t[mask] - t_beat
            bass_pluck = 0.5 * np.sin(2 * np.pi * root_freq * dt) * np.exp(-dt * 6.0)
            bass_pluck += 0.2 * np.sin(2 * np.pi * root_freq * 2 * dt) * np.exp(-dt * 10.0)
            bgm_audio[mask] += bass_pluck
            
        # 2. Ukulele / Acoustic Strum on offbeats
        strum_time = t_beat + beat_dur * 0.5
        mask_strum = (t >= strum_time) & (t < strum_time + beat_dur * 0.8)
        dt_strum = t[mask_strum] - strum_time
        for n in chord:
            strum_wave = 0.15 * np.sin(2 * np.pi * n * dt_strum) * np.exp(-dt_strum * 12.0)
            strum_wave += 0.05 * np.sin(2 * np.pi * n * 2 * dt_strum) * np.exp(-dt_strum * 18.0)
            bgm_audio[mask_strum] += strum_wave
            
        # 3. Playful Marimba 16th note pattern
        for sub in range(4):
            t_sub = t_beat + sub * (beat_dur / 4.0)
            note = chord[(beat * 4 + sub) % len(chord)]
            mask_sub = (t >= t_sub) & (t < t_sub + beat_dur * 0.4)
            dt_sub = t[mask_sub] - t_sub
            marimba = 0.25 * np.sin(2 * np.pi * note * dt_sub) * np.exp(-dt_sub * 22.0)
            marimba += 0.15 * np.sin(2 * np.pi * note * 3 * dt_sub) * np.exp(-dt_sub * 35.0)
            bgm_audio[mask_sub] += marimba
            
        # 4. Light cute shaker
        for s in range(2):
            t_shaker = t_beat + s * (beat_dur / 2.0)
            mask_shaker = (t >= t_shaker) & (t < t_shaker + 0.04)
            dt_shaker = t[mask_shaker] - t_shaker
            noise = (np.random.rand(len(dt_shaker)) * 2 - 1) * np.exp(-dt_shaker * 120.0)
            bgm_audio[mask_shaker] += noise * 0.08

    max_val = np.max(np.abs(bgm_audio))
    if max_val > 0:
        bgm_audio = (bgm_audio / max_val) * 0.80
        
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        int_data = (bgm_audio * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    return output_path

async def generate_single_tts(text, voice, pitch, rate, output_mp3):
    """Generate TTS audio file with pitch and rate modulation using edge-tts."""
    try:
        import edge_tts
        pitch_str = f"+{pitch}Hz" if isinstance(pitch, (int, float)) and pitch >= 0 else f"{pitch}Hz" if isinstance(pitch, (int, float)) else str(pitch)
        rate_str = f"+{rate}%" if isinstance(rate, (int, float)) and rate >= 0 else f"{rate}%" if isinstance(rate, (int, float)) else str(rate)
        
        communicate = edge_tts.Communicate(text, voice, pitch=pitch_str, rate=rate_str)
        await communicate.save(output_mp3)
        return True
    except Exception as e:
        print(f"Edge TTS failed for '{text[:20]}...': {e}", file=sys.stderr, flush=True)
        return False

def resolve_character_image(scene, project_root):
    """Find the best 3D reference image for the scene."""
    img_path = scene.get("image_path") or scene.get("image")
    if img_path:
        p = Path(img_path)
        if not p.is_absolute():
            p = project_root / img_path
        if p.exists():
            return str(p)

    # Check assets/pixar-characters by character name
    char_lower = scene.get("character", "").lower()
    mapping = {
        "pencil": "pencil_hero.jpg",
        "eraser": "eraser_panicking.jpg",
        "sharpener": "sharpener_tech.jpg",
        "ruler": "ruler_superhero.jpg",
        "squad": "squad_vertical.jpg",
        "outro": "outro_vertical.jpg"
    }
    for key, filename in mapping.items():
        if key in char_lower:
            candidate = project_root / "assets" / "pixar-characters" / filename
            if candidate.exists():
                return str(candidate)

    # Check brain directory artifacts
    brain_dir = Path("C:/Users/Amar's PC/.gemini/antigravity/brain/948aeb55-f992-450a-afe5-fdaa77988433")
    if brain_dir.exists():
        brain_map = {
            "pencil": "pencil_clean_scene1_1790778959181.jpg",
            "eraser": "perfect_eraser_scene2_1790767774858.jpg",
            "sharpener": "sharpener_vertical_scene3_1790778982658.jpg",
            "ruler": "perfect_ruler_scene4_1790767816866.jpg",
            "squad": "squad_vertical_scene5_1790779257620.jpg",
            "outro": "outro_vertical_scene6_1790779279652.jpg"
        }
        for key, filename in brain_map.items():
            if key in char_lower:
                candidate = brain_dir / filename
                if candidate.exists():
                    return str(candidate)

    return None

def render_fallback_frame(character_name, scene_title, width, height, output_png):
    """Render high quality fallback 9:16 frame if no 3D asset is available."""
    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    img = Image.new("RGB", (width, height), color=(25, 30, 55))
    draw = ImageDraw.Draw(img)
    
    top_color = (25, 30, 55)
    bottom_color = (80, 110, 160)
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * (y / height))
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * (y / height))
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    cx, cy = int(width * 0.5), int(height * 0.42)
    char_lower = character_name.lower()
    
    if "pencil" in char_lower:
        draw.rounded_rectangle([cx - 45, cy - 180, cx + 45, cy - 130], radius=15, fill=(255, 140, 170))
        draw.rectangle([cx - 48, cy - 130, cx + 48, cy - 100], fill=(210, 215, 225))
        draw.rounded_rectangle([cx - 45, cy - 100, cx + 45, cy + 110], radius=8, fill=(255, 195, 25))
        draw.polygon([(cx - 45, cy + 110), (cx + 45, cy + 110), (cx, cy + 175)], fill=(240, 215, 175))
        draw.polygon([(cx - 15, cy + 155), (cx + 15, cy + 155), (cx, cy + 175)], fill=(40, 40, 45))
        draw.ellipse([cx - 30, cy - 35, cx - 8, cy - 10], fill=(255, 255, 255))
        draw.ellipse([cx - 24, cy - 30, cx - 12, cy - 16], fill=(30, 40, 60))
        draw.ellipse([cx + 8, cy - 35, cx + 30, cy - 10], fill=(255, 255, 255))
        draw.ellipse([cx + 12, cy - 30, cx + 24, cy - 16], fill=(30, 40, 60))
        draw.arc([cx - 18, cy - 5, cx + 18, cy + 20], start=10, end=170, fill=(40, 25, 20), width=4)
    elif "eraser" in char_lower:
        draw.rounded_rectangle([cx - 75, cy - 90, cx + 75, cy + 90], radius=25, fill=(255, 130, 160))
        draw.rounded_rectangle([cx - 65, cy + 10, cx + 65, cy + 80], radius=15, fill=(70, 130, 240))
        draw.ellipse([cx - 45, cy - 60, cx - 10, cy - 15], fill=(255, 255, 255))
        draw.ellipse([cx + 10, cy - 60, cx + 45, cy - 15], fill=(255, 255, 255))
        draw.ellipse([cx - 15, cy - 5, cx + 15, cy + 25], fill=(80, 20, 30))
    elif "sharpener" in char_lower:
        draw.rounded_rectangle([cx - 70, cy - 80, cx + 70, cy + 80], radius=18, fill=(45, 150, 245))
        draw.rounded_rectangle([cx - 35, cy - 55, cx + 35, cy + 55], radius=6, fill=(215, 220, 230))
    elif "ruler" in char_lower:
        draw.rounded_rectangle([cx - 35, cy - 190, cx + 35, cy + 130], radius=10, fill=(245, 175, 55))
        draw.polygon([(cx - 35, cy - 80), (cx - 95, cy + 120), (cx - 35, cy + 40)], fill=(235, 45, 45))
    else:
        draw.rounded_rectangle([cx - 120, cy - 120, cx + 120, cy + 100], radius=35, fill=(50, 75, 130))

    badge_y = int(height * 0.12)
    draw.rounded_rectangle([int(width * 0.12), badge_y, int(width * 0.88), badge_y + 60], radius=30, fill=(15, 20, 35, 200))
    draw.rounded_rectangle([int(width * 0.12), badge_y, int(width * 0.88), badge_y + 60], radius=30, outline=(255, 215, 0), width=2)
    draw.text((int(width * 0.5), badge_y + 30), f"★ {character_name.upper()} ★", fill=(255, 235, 150), anchor="mm")
    draw.text((int(width * 0.5), int(height * 0.82)), scene_title, fill=(255, 255, 255), anchor="mm")
    draw.text((int(width * 0.5), int(height * 0.86)), "3D Disney/Pixar Animated Cinema", fill=(180, 210, 255), anchor="mm")

    img.save(output_png, quality=95)
    return output_png

def render_scene_clip_exact(image_source, output_mp4, duration, fps=60, width=720, height=1280):
    """
    Render standardized 720x1280 9:16 vertical video clip with strict aspect ratio
    and smooth progressive 60 FPS output.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)
    
    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-framerate", str(fps),
        "-i", str(image_source),
        "-t", f"{duration:.2f}",
        "-vf", (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"setsar=1,"
            f"format=yuv420p,"
            f"fps={fps}"
        ),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        str(output_mp4)
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if p.returncode != 0:
        print(f"FFmpeg render failed for clip {output_mp4}:\n{p.stderr}", file=sys.stderr, flush=True)
        raise RuntimeError(f"FFmpeg render failed: {p.stderr}")
    return output_mp4

async def create_cartoon_audio_tracks(storyboard, audio_dir):
    """
    Generate distinct high-pitch cartoon character voiceovers, probe durations,
    pad with apad to slot times, and create master_dialogue.mp3.
    """
    print("[1/4] 🎙️ Generating Distinct Cartoon Character Voiceovers & apad padding...", flush=True)
    os.makedirs(audio_dir, exist_ok=True)
    scene_audios = []
    
    num_scenes = len(storyboard)
    for idx, sc in enumerate(storyboard):
        raw_audio = os.path.join(audio_dir, f"scene_{idx}_raw.mp3")
        padded_audio = os.path.join(audio_dir, f"scene_{idx}_padded.mp3")
        
        voice = sc.get("voice", "hi-IN-MadhurNeural")
        rate = sc.get("rate", "+8%")
        pitch = sc.get("pitch", "+18Hz")
        text = sc.get("dialogue", "")
        
        await generate_single_tts(text, voice, pitch, rate, raw_audio)
        
        # Probe speech duration
        dur = get_media_duration(raw_audio)
        if dur <= 0:
            dur = 7.0
            
        slot_dur = 9.54 if idx < num_scenes - 1 else 10.04
        pad_dur = max(0.0, slot_dur - dur)
        
        cmd_pad = [
            FFMPEG, "-y",
            "-i", raw_audio,
            "-af", f"apad=pad_dur={pad_dur:.2f}",
            "-t", f"{slot_dur:.2f}",
            padded_audio
        ]
        subprocess.run(cmd_pad, capture_output=True)
        scene_audios.append(padded_audio)
        print(f"  [+] Scene {idx+1}/{num_scenes} ({sc.get('character', 'Character')}): Voice={voice} (Pitch: {pitch}, Rate: {rate}) | Speech={dur:.2f}s (Padded={pad_dur:.2f}s)", flush=True)

    concat_txt = os.path.join(audio_dir, "audio_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in scene_audios:
            rel = os.path.basename(p)
            f.write(f"file '{rel}'\n")
            
    master_dialogue = os.path.join(audio_dir, "master_dialogue.mp3")
    cmd_concat = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "audio_concat.txt", "-c", "copy", master_dialogue]
    subprocess.run(cmd_concat, cwd=audio_dir, capture_output=True)
    print(f"  [✓] Master Cartoon Dialogue Track: {master_dialogue}", flush=True)
    return master_dialogue, scene_audios

def build_dissolve_sequence_with_start_end_fades(clip_paths, output_dir, final_slot_offsets=None):
    """
    Assemble scene clips using xfade cross dissolves, fade-in from black,
    and fade-out to black.
    """
    print("\n[3/4] ✨ Normalizing to Strict 9:16 (720x1280) & Applying In/Out Dissolves...", flush=True)
    num_scenes = len(clip_paths)
    transition_dur = 0.50
    
    # Calculate accumulated xfade offsets
    if final_slot_offsets is None:
        offsets = []
        accum = 0.0
        for i in range(num_scenes - 1):
            accum += 9.54
            offsets.append(accum)
    else:
        offsets = final_slot_offsets

    filter_complex_parts = []
    if num_scenes == 1:
        total_dur = 10.0
        filter_complex_parts.append(f"[0:v]fade=t=in:st=0:d=0.75,fade=t=out:st={total_dur - 1.0:.2f}:d=1.0[vout]")
    else:
        filter_complex_parts.append(f"[0:v][1:v]xfade=transition=fade:duration={transition_dur}:offset={offsets[0]:.2f}[v01]")
        last_v = "v01"
        for i in range(2, num_scenes):
            next_v = f"v0{i}"
            filter_complex_parts.append(f"[{last_v}][{i}:v]xfade=transition=fade:duration={transition_dur}:offset={offsets[i-1]:.2f}[{next_v}]")
            last_v = next_v
            
        total_dur = offsets[-1] + 10.04 - transition_dur
        filter_complex_parts.append(f"[{last_v}]fade=t=in:st=0:d=0.75,fade=t=out:st={total_dur - 1.0:.2f}:d=1.0[vout]")

    xfade_output = os.path.join(output_dir, "master_dissolve_video.mp4")
    inputs = []
    for c in clip_paths:
        inputs.extend(["-i", c])
        
    cmd = [
        FFMPEG, "-y",
        *inputs,
        "-filter_complex", ";".join(filter_complex_parts),
        "-map", "[vout]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        xfade_output
    ]
    print("  [+] Executing xfade + intro/outro dissolves...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print(f"[-] xfade failed:\n{res.stderr}", flush=True)
        raise RuntimeError(f"xfade failure: {res.stderr}")
        
    print(f"  [✓] Dissolve Video Ready: {xfade_output}", flush=True)
    return xfade_output, total_dur

def produce_final_master_v3(video_path, dialogue_path, bgm_path, bell_path, output_path, total_dur, bell_delay_s=47.70, fps=60):
    """
    Multiplex Master Reel with Boosted BGM, Real School Bell SFX, and progressive 60 FPS output.
    """
    print("\n[4/4] 🚀 Multiplexing Master Reel with Boosted BGM, Real School Bell SFX, and 60 FPS...", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    bell_delay_ms = int(bell_delay_s * 1000)
    audio_fade_out_st = max(1.0, total_dur - 1.25)
    
    audio_filter = (
        f"[1:a]volume=1.05,aformat=channel_layouts=stereo[a_diag];"
        f"[2:a]volume=0.35,aformat=channel_layouts=stereo[a_bgm];"
        f"[3:a]adelay={bell_delay_ms}|{bell_delay_ms},volume=0.90,aformat=channel_layouts=stereo[a_bell];"
        f"[a_diag][a_bgm][a_bell]amix=inputs=3:duration=first:dropout_transition=2,"
        f"afade=t=in:st=0:d=0.3,afade=t=out:st={audio_fade_out_st:.2f}:d=1.2[a_mix]"
    )
    
    video_filter = f"[0:v]fps=fps={fps}[v60]"
    full_filter = f"{video_filter};{audio_filter}"
    
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", dialogue_path,
        "-i", bgm_path,
        "-i", bell_path,
        "-filter_complex", full_filter,
        "-map", "[v60]",
        "-map", "[a_mix]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "44100",
        "-t", f"{total_dur:.2f}",
        output_path
    ]
    print(f"  [+] Final encoding to 60 FPS MP4 ({output_path})...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print(f"[-] Multiplexing error:\n{res.stderr}", flush=True)
        raise RuntimeError(f"Final multiplexing failure: {res.stderr}")
        
    print(f"\n🎉 MASTER 60 FPS REEL READY:\n{output_path}", flush=True)
    return output_path

async def main_async():
    parser = argparse.ArgumentParser(description="Render Pixar 3D Animated Video Reel (V3 Engine)")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    args = parser.parse_args()
    
    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    storyboard = config.get("storyboard", [])
    options = config.get("options", {})
    output_path = config.get("output_path", "output/pixar_reel_60fps.mp4")
    temp_dir = Path(config.get("temp_dir", "temp/pixar_render"))
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    project_root = Path(__file__).resolve().parent.parent.parent
    width, height = options.get("resolution", [720, 1280])
    fps = options.get("fps", 60)
    
    print("=" * 75)
    print("🌟 PIXAR 3D ANIMATED REEL GENERATION (V3 ENGINE) 🌟")
    print(f"Scenes: {len(storyboard)} | Target: {width}x{height} @ {fps} FPS")
    print("=" * 75, flush=True)
    
    # 1. Generate SFX & BGM Assets
    audio_dir = str(temp_dir / "audio_tracks")
    clips_dir = str(temp_dir / "scene_clips")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(clips_dir, exist_ok=True)
    
    bell_wav = os.path.join(audio_dir, "real_school_bell.wav")
    bgm_wav = os.path.join(audio_dir, "cheerful_cartoon_bgm.wav")
    
    create_physical_school_bell(bell_wav, duration=4.0)
    create_cheerful_cartoon_bgm(bgm_wav, total_duration=240.0)
    
    # 2. Stage 1: Generate dialogue tracks with apad alignment
    master_dialogue, padded_scene_audios = await create_cartoon_audio_tracks(storyboard, audio_dir)
    
    # 3. Stage 2: Render scene clips from verified 3D assets
    print("\n[2/4] 🎬 Rendering Standardized 9:16 Scene Clips...", flush=True)
    clip_paths = []
    num_scenes = len(storyboard)
    
    for idx, scene in enumerate(storyboard):
        clip_file = os.path.join(clips_dir, f"scene_{idx}.mp4")
        slot_dur = 10.04 if idx == num_scenes - 1 else 9.54
        
        # Find 3D reference image
        ref_image = resolve_character_image(scene, project_root)
        if not ref_image or not os.path.exists(ref_image):
            # Render visual frame
            frame_png = os.path.join(clips_dir, f"frame_{idx}.png")
            render_fallback_frame(scene.get("character", "Character"), scene.get("title", f"Scene {idx+1}"), width, height, frame_png)
            ref_image = frame_png
            
        render_scene_clip_exact(ref_image, clip_file, slot_dur, fps=fps, width=width, height=height)
        clip_paths.append(clip_file)
        print(f"  [✓] Scene {idx+1}/{num_scenes} clip rendered: {clip_file} ({slot_dur}s)", flush=True)

    # 4. Stage 3: Assemble dissolve sequence with start & end fades
    offsets = [9.54 * (i + 1) for i in range(num_scenes - 1)]
    dissolve_video, total_dur = build_dissolve_sequence_with_start_end_fades(clip_paths, str(temp_dir), offsets)
    
    # 5. Stage 4: Produce final 60 FPS master
    bell_delay = offsets[-1] if len(offsets) > 0 else 1.0
    final_output = produce_final_master_v3(
        dissolve_video,
        master_dialogue,
        bgm_wav,
        bell_wav,
        output_path,
        total_dur,
        bell_delay_s=bell_delay,
        fps=fps
    )
    
    print("\n✅ PIXAR 3D ANIMATION PIPELINE COMPLETE!")
    print(f"Output: {final_output}")
    return final_output

if __name__ == "__main__":
    asyncio.run(main_async())
