import numpy as np
import wave
import os

AUDIO_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\audio_tracks"

def make_real_school_bell():
    sample_rate = 44100
    duration = 4.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Authentic Electric School Gong Bell (Mechanical hammer vibrating rapidly on metal bell dome)
    # Hammer rate = 16.5 Hz (striking for 1.8 seconds, then sustained bell resonance)
    bell_wave = np.zeros_like(t)
    
    # Real physical brass/steel bell modal frequencies (inharmonic metal modes)
    # Mode 1: 910 Hz (Hum tone)
    # Mode 2: 1320 Hz (Prime)
    # Mode 3: 1840 Hz (Tierce)
    # Mode 4: 2610 Hz (Quint)
    # Mode 5: 3580 Hz (Nominal)
    # Mode 6: 4920 Hz (Supernominal)
    # Mode 7: 6400 Hz (High shimmer)
    modes = [
        (910.0, 0.40, 1.2),
        (1320.0, 0.35, 1.5),
        (1840.0, 0.25, 2.0),
        (2610.0, 0.18, 2.5),
        (3580.0, 0.12, 3.2),
        (4920.0, 0.08, 4.0),
        (6400.0, 0.05, 5.0)
    ]
    
    ring_duration = 1.8  # 1.8s of hammer striking
    hammer_freq = 16.5  # 16.5 strikes per second
    num_strikes = int(ring_duration * hammer_freq)
    
    for i in range(num_strikes):
        t_strike = i / hammer_freq
        mask = t >= t_strike
        dt = t[mask] - t_strike
        
        # Attack click/clapper impulse
        clapper = 0.3 * np.exp(-dt * 200.0) * (np.sin(2 * np.pi * 3200 * dt) + 0.5 * np.random.randn(len(dt)))
        bell_wave[mask] += clapper * 0.2
        
        # Modal resonance per strike
        for freq, amp, decay_rate in modes:
            # Slight detuning per mode for rich metallic beating
            f_detuned = freq + np.random.uniform(-3, 3)
            mode_sig = amp * np.sin(2 * np.pi * f_detuned * dt) * np.exp(-dt * (decay_rate * 3.5))
            bell_wave[mask] += mode_sig * 0.15

    # Long sustained acoustic decay of the bell shell after clapper stops
    mask_sustain = t >= ring_duration
    dt_sustain = t[mask_sustain] - ring_duration
    for freq, amp, decay_rate in modes:
        sustain_sig = (amp * 0.6) * np.sin(2 * np.pi * freq * dt_sustain) * np.exp(-dt_sustain * 1.4)
        # Add slight natural tremolo/beating
        sustain_sig *= (1.0 + 0.25 * np.sin(2 * np.pi * 4.5 * dt_sustain))
        bell_wave[mask_sustain] += sustain_sig

    # Normalize
    max_amp = np.max(np.abs(bell_wave))
    if max_amp > 0:
        bell_wave = (bell_wave / max_amp) * 0.90
        
    out_path = os.path.join(AUDIO_DIR, "real_school_bell.wav")
    with wave.open(out_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        int_data = (bell_wave * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())
        
    print(f"Generated Realistic School Electric Bell: {out_path}")
    return out_path

if __name__ == "__main__":
    make_real_school_bell()
