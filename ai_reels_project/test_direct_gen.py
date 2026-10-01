import sys
import os
import asyncio

sys.stdout.reconfigure(encoding='utf-8')

AGNES_ROOT = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\agnes-video-generator"
if AGNES_ROOT not in sys.path:
    sys.path.insert(0, AGNES_ROOT)

from core.api.agnes_video import AgnesVideoAPI
from core.config import get_api_key

BRAIN_DIR = r"C:\Users\Amar's PC\.gemini\antigravity\brain\948aeb55-f992-450a-afe5-fdaa77988433"
img1 = os.path.join(BRAIN_DIR, "perfect_pencil_scene1_1790767758092.jpg")

async def test_scene():
    api = AgnesVideoAPI(api_key=get_api_key(), default_duration=10)
    prompt = "A high-quality 3D Pixar animation scene. A cheerful yellow pencil character with large expressive eyes smiling cheerfully on a warm wooden classroom desk beside a colorful backpack. Warm morning sunlight streaming through the windows, steady locked-off framing, rich 3D textures, zero jitter, zero hallucinations, pure animated character."
    print("Submitting single video...")
    out = await api.generate_single_video(
        prompt=prompt,
        reference_image_paths=[img1],
        duration=10,
        width=768,
        height=1152,
        negative_prompt="jitter, stutter, flickering, human, people, blurry, low quality, distorted, extra limbs, messy background, morphing"
    )
    save_path = os.path.join(r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project\output", "test_scene0_direct.mp4")
    await out.save(save_path)
    print(f"Saved to {save_path}")

if __name__ == "__main__":
    asyncio.run(test_scene())
