import numpy as np
import wave
import struct
import os

AUDIO_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\audio_tracks"
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_school_bell():
    sample_rate = 44100
    duration = 4.5
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 1. School electric bell / brass chime (Rich multi-strike ringing)
    # Strikes at 0.0s, 0.4s, 0.8s, 1.2s, 1.6s, 2.0s plus background fast gong hammer (20Hz hammer)
    bell_audio = np.zeros_like(t)
    
    # Classic school bell frequencies (metallic inharmonic modes)
    freqs = [659.25, 880.0, 1174.66, 1318.51, 1760.0, 2637.0, 3520.0]
    weights = [0.4, 0.35, 0.25, 0.2, 0.15, 0.08, 0.05]
    decays = [2.5, 2.0, 1.8, 1.5, 1.2, 0.8, 0.6]
    
    # Rapid hammer vibration (electric school bell: 18 strikes per second)
    num_hammer_strikes = 36  # ~2 seconds of ringing
    strike_interval = 0.055  # ~18Hz
    
    for i in range(num_hammer_strikes):
        t_strike = i * strike_interval
        mask = t >= t_strike
        dt = t[mask] - t_strike
        
        # Each strike impulse
        strike_wave = np.zeros_like(dt)
        for f, w, d in zip(freqs, weights, decays):
            strike_wave += w * np.sin(2 * np.pi * f * dt) * np.exp(-dt * 30.0)
            # Add shimmering long resonance
            strike_wave += (w * 0.3) * np.sin(2 * np.pi * f * dt) * np.exp(-dt * d)
            
        bell_audio[mask] += strike_wave * 0.25

    # Master brass resonance sustaining after ringing stops
    end_strike_time = num_hammer_strikes * strike_interval
    mask_decay = t >= end_strike_time
    dt_decay = t[mask_decay] - end_strike_time
    for f, w, d in zip(freqs, weights, decays):
        bell_audio[mask_decay] += (w * 0.5) * np.sin(2 * np.pi * f * dt_decay) * np.exp(-dt_decay * 1.2)
        
    # Normalize
    max_val = np.max(np.abs(bell_audio))
    if max_val > 0:
        bell_audio = (bell_audio / max_val) * 0.85
        
    bell_path = os.path.join(AUDIO_DIR, "school_bell_sfx.wav")
    with wave.open(bell_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        int_data = (bell_audio * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    print(f"Generated School Bell SFX: {bell_path}")
    return bell_path

def generate_cheerful_cartoon_bgm():
    sample_rate = 44100
    total_duration = 62.0  # 62 seconds of upbeat music loop
    t = np.linspace(0, total_duration, int(sample_rate * total_duration), endpoint=False)
    
    bgm_audio = np.zeros_like(t)
    
    # Upbeat tempo: 124 BPM (0.4838 seconds per beat)
    beat_dur = 60.0 / 124.0
    
    # Cute Major chord progression: C - G - Am - F (playful Disney Pixar style)
    # Scale notes in Hz
    NOTE_C4 = 261.63
    NOTE_D4 = 293.66
    NOTE_E4 = 329.63
    NOTE_F4 = 349.23
    NOTE_G4 = 392.00
    NOTE_A4 = 440.00
    NOTE_B4 = 493.88
    NOTE_C5 = 523.25
    NOTE_D5 = 587.33
    NOTE_E5 = 659.25
    NOTE_G5 = 783.99
    NOTE_A5 = 880.00
    
    # Upbeat Marimba / Ukulele / Glockenspiel arpeggios
    chords = [
        [NOTE_C4, NOTE_E4, NOTE_G4, NOTE_C5], # C
        [NOTE_G4, NOTE_B4, NOTE_D5, NOTE_G5], # G
        [NOTE_A4, NOTE_C5, NOTE_E5, NOTE_A5], # Am
        [NOTE_F4, NOTE_A4, NOTE_C5, NOTE_F4 * 2], # F
    ]
    
    melody_notes = [
        NOTE_C5, NOTE_E5, NOTE_G5, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_G5,
        NOTE_E5, NOTE_G5, NOTE_A5, NOTE_G5, NOTE_F5 if 'NOTE_F5' in locals() else NOTE_F4 * 2, NOTE_E5, NOTE_D5, NOTE_C5
    ]
    
    total_beats = int(total_duration / beat_dur)
    
    for beat in range(total_beats):
        t_beat = beat * beat_dur
        chord_idx = (beat // 4) % len(chords)
        chord = chords[chord_idx]
        
        # 1. Bass / Tuba pluck on downbeat
        if beat % 2 == 0:
            root_freq = chord[0] / 2.0  # Bass note (C3, G3, etc.)
            mask = (t >= t_beat) & (t < t_beat + beat_dur * 1.5)
            dt = t[mask] - t_beat
            bass_pluck = 0.5 * np.sin(2 * np.pi * root_freq * dt) * np.exp(-dt * 6.0)
            bass_pluck += 0.2 * np.sin(2 * np.pi * root_freq * 2 * dt) * np.exp(-dt * 10.0)
            bgm_audio[mask] += bass_pluck
            
        # 2. Ukulele / Acoustic Strum on offbeats (beats 1, 3, etc.)
        strum_time = t_beat + beat_dur * 0.5
        mask_strum = (t >= strum_time) & (t < strum_time + beat_dur * 0.8)
        dt_strum = t[mask_strum] - strum_time
        for n in chord:
            strum_wave = 0.15 * np.sin(2 * np.pi * n * dt_strum) * np.exp(-dt_strum * 12.0)
            strum_wave += 0.05 * np.sin(2 * np.pi * n * 2 * dt_strum) * np.exp(-dt_strum * 18.0)
            bgm_audio[mask_strum] += strum_wave
            
        # 3. Playful Marimba / Xylophone 16th note pattern (4 notes per beat)
        for sub in range(4):
            t_sub = t_beat + sub * (beat_dur / 4.0)
            note = chord[(beat * 4 + sub) % len(chord)]
            mask_sub = (t >= t_sub) & (t < t_sub + beat_dur * 0.4)
            dt_sub = t[mask_sub] - t_sub
            # Marimba woody bell tone
            marimba = 0.25 * np.sin(2 * np.pi * note * dt_sub) * np.exp(-dt_sub * 22.0)
            marimba += 0.15 * np.sin(2 * np.pi * note * 3 * dt_sub) * np.exp(-dt_sub * 35.0)
            bgm_audio[mask_sub] += marimba
            
        # 4. Light cute shaker / hi-hat on every 8th note
        for s in range(2):
            t_shaker = t_beat + s * (beat_dur / 2.0)
            mask_shaker = (t >= t_shaker) & (t < t_shaker + 0.04)
            dt_shaker = t[mask_shaker] - t_shaker
            # Filtered noise burst
            noise = (np.random.rand(len(dt_shaker)) * 2 - 1) * np.exp(-dt_shaker * 120.0)
            bgm_audio[mask_shaker] += noise * 0.08
            
    # Normalize BGM
    max_val = np.max(np.abs(bgm_audio))
    if max_val > 0:
        bgm_audio = (bgm_audio / max_val) * 0.8
        
    bgm_path = os.path.join(AUDIO_DIR, "cheerful_cartoon_bgm.wav")
    with wave.open(bgm_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        int_data = (bgm_audio * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    print(f"Generated Cheerful Cartoon BGM: {bgm_path}")
    return bgm_path

if __name__ == "__main__":
    generate_school_bell()
    generate_cheerful_cartoon_bgm()
