import urllib.request
import os
import subprocess

FFMPEG = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
AUDIO_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\audio_tracks"

# Let's download a real school bell / service bell / clock bell from Google sound library
urls = [
    ("https://actions.google.com/sounds/v1/household/bell_ring_short.ogg", "bell_short.ogg"),
    ("https://actions.google.com/sounds/v1/cartoon/metal_twang.ogg", "twang.ogg"),
    ("https://actions.google.com/sounds/v1/foley/bike_bell.ogg", "bike_bell.ogg"),
]

for url, fname in urls:
    try:
        dest = os.path.join(AUDIO_DIR, fname)
        urllib.request.urlretrieve(url, dest)
        print(f"Downloaded {fname}")
    except Exception as e:
        print(f"Failed {fname}: {e}")
