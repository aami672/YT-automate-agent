import sys
import os

AGNES_ROOT = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator"
if AGNES_ROOT not in sys.path:
    sys.path.insert(0, AGNES_ROOT)

from core.api.agnes_video import AgnesVideoAPI
from core.config import get_api_key

api_key = get_api_key()
print(f"Loaded Agnes API Key: {api_key[:10]}...")
print("AgnesVideoAPI ready!")
