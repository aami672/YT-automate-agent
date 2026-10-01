# 🎒 School Backpack Squad — 1-Minute 60 FPS 3D Animated Reel

A fully automated production pipeline for creating broadcast-quality **3D Disney/Pixar-style animated Hindi cartoon reels** for YouTube Shorts, Instagram Reels, and TikTok.

---

## 🌟 Locked Feature Architecture

### 1. 3D Character Consistency & Visual Diffusion
- **Pencil Hero**: Classic yellow wooden stationery pencil, sharp graphite tip, pink eraser top, animated expressive eyes & smile (**strictly NO legs, NO tails**).
- **Pink Eraser**: Chunky, soft rubber eraser with expressive worried cartoon eyes and comical body gestures.
- **Blue Sharpener**: High-tech translucent blue sharpener with internal steel blade, upright **9:16 vertical proportions**.
- **Clear Ruler**: Tall, transparent crystal ruler with measurement markings and proud superhero posture.
- **Backpack Squad Unity**: Centered 9:16 vertical group composition on a warm wooden school desk with morning classroom sunlight.
- **Celebration Finale**: Confetti bokeh, festive morning light, and joyful waving animations.

---

### 2. Multi-Character Hindi Cartoon Voice Acting
Built with high-pitch cartoon character profiles:
| Character / Scene | Edge-TTS Voice | Rate | Pitch | Persona |
| :--- | :--- | :--- | :--- | :--- |
| **Scene 1 (Pencil Hero)** | `hi-IN-MadhurNeural` | `+8%` | `+18Hz` | High-energy boyish cartoon protagonist |
| **Scene 2 (Eraser Panicking)** | `hi-IN-SwaraNeural` | `+5%` | `+32Hz` | Squeaky, comical, frantic comic relief |
| **Scene 3 (Sharpener Tech)** | `hi-IN-SwaraNeural` | `+10%` | `+18Hz` | Upbeat, zippy tech buddy |
| **Scene 4 (Ruler Superhero)** | `hi-IN-MadhurNeural` | `-8%` | `-22Hz` | Deep, dramatic cartoon superhero commander |
| **Scene 5 (Squad Action)** | `hi-IN-MadhurNeural` | `+6%` | `+14Hz` | Excited, synchronized teamwork |
| **Scene 6 (Outro & Bell)** | `hi-IN-MadhurNeural` | `+8%` | `+20Hz` | Upbeat audience call-to-action |

---

### 3. Audio & SFX Multi-Layer Mixing
- **Voiceover Layer**: Clear, balanced dialogue track with per-scene timing synchronization.
- **Background Music (BGM)**: Upbeat, playful Disney/Pixar acoustic marimba & ukulele cartoon loop (35% volume).
- **School Bell Chime SFX**: Multi-harmonic authentic electric school bell ring (*Trrrriiiiing & Metal Gong Resonance*) at 90% volume starting at Scene 6.
- **Fade Envelopes**: 0.3s audio fade-in and 1.2s audio fade-out to guarantee zero abrupt sound truncations.

---

### 4. Cinematic Transitions & 60 FPS Fluidity
- **Opening & Ending Dissolves**: 0.75s dissolve fade-in from black at start; 1.0s dissolve fade-out to black at end.
- **Scene-to-Scene Transitions**: 0.5s FFmpeg `xfade` dissolve crossfades across all cuts.
- **60 FPS Motion Interpolation**: High-framerate progressive video encoding (`CRF 16-17`, H.264 High Profile, `yuv420p`).
- **Aspect Ratio**: Standard **9:16 Vertical (`720 × 1280`)** with zero stretching or distortion.

---

## 🚀 Pipeline Scripts

- **`rerender_and_assemble_v3.py`**: The master all-in-one script that executes the complete pipeline end-to-end (voiceover synthesis, 3D video generation, 9:16 normalization, dissolve transitions, multi-track audio mixing, and 60 FPS multiplexing).
- **`create_real_school_bell.py`**: Synthesizes the authentic physical electric school bell sound effect.
- **`generate_audio_assets.py`**: Generates the playful Disney/Pixar acoustic cartoon background music.
- **`finalize_v3_master.py`**: Fast master multiplexing utility for rendering final MP4 output.

---

## 📁 Output Artifacts

- **Master Video Deliverable**: `output/backpack_squad_1min_premium_60fps.mp4`
- **Resolution**: `720 × 1280` (9:16 Vertical)
- **Framerate**: `60.00 FPS` Progressive
- **Duration**: `00:00:57.75` (~58 seconds)
- **Audio**: AAC Stereo, `44.1 kHz`, `216 kbps`
