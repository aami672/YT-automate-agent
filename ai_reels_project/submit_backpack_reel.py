import os
import sys
import json
import time
import requests
import shutil

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("[*] Starting Backpack Squad 3D Reel Production...")
    
    brain_dir = r"C:\Users\Amar's PC\.gemini\antigravity\brain\948aeb55-f992-450a-afe5-fdaa77988433"
    ai_reels_dir = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
    assets_dir = os.path.join(ai_reels_dir, "assets")
    output_dir = os.path.join(ai_reels_dir, "output")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    img1 = os.path.join(brain_dir, "backpack_scene1_pencil_1790604281443.jpg")
    img2 = os.path.join(brain_dir, "backpack_scene2_eraser_1790604294471.jpg")
    img3 = os.path.join(brain_dir, "backpack_scene3_ruler_1790604311264.jpg")
    img4 = os.path.join(brain_dir, "backpack_scene4_squad_1790604324147.jpg")
    
    ref_images = [img1, img2, img3, img4]
    for i, p in enumerate(ref_images):
        if not os.path.exists(p):
            print(f"Error: Image {p} not found!")
            return
    
    paragraphs = [
        {
            "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे 10 में से 10 मार्क्स लेकर ही मानेंगे!",
            "scene_prompt": "A cheerful, vibrant 3D Pixar-style animation scene inside a bright school classroom. A cute anthropomorphic yellow wooden pencil with large expressive eyes smiling excitedly while standing by a colorful backpack on a wooden desk. Morning sunlight streaming through the classroom windows, cinematic warm lighting, high-detail textures, lyrical camera push-in."
        },
        {
            "text": "तभी इरेज़र रोते हुए बोला: अरे पेंसिल भाई धीरे लिखो! तुम तो गलतियां करोगे और पूरा घिसना मुझे ही पड़ेगा, मेरी तो कमर टूट जाएगी!",
            "scene_prompt": "Inside a sunlit 3D animated classroom, a chubby pink and white eraser character with wide comical worried eyes and hands on its cheeks, trembling playfully beside a math notebook. Dynamic cinematic low-angle camera, exaggerated funny expressions, rich cartoon physics and soft morning light."
        },
        {
            "text": "स्केल भाई शान से बोले: शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, क्लास में सब कुछ बिल्कुल सीधा और परफेक्ट रहेगा!",
            "scene_prompt": "A tall, sleek transparent ruler character stands proudly with hands on hips like a superhero on a colorful notebook. Playful Pixar animation style, sunny classroom backdrop with soft depth of field, crisp reflections on the ruler surface, smooth lyrical pan."
        },
        {
            "text": "तभी स्कूल की घंटी बजी: टन-टन-टन! चलो बैकपैक स्क्वाड, मिशन शुरू! आपका स्कूल में सबसे फेवरेट स्टेशनरी कौन सा था? कमेंट में बताओ!",
            "scene_prompt": "The entire school stationery squad - animated yellow pencil, pink eraser, tall ruler, and a cute little blue sharpener celebrating together inside an open pencil box. Bright confetti and magical morning glow, dynamic camera sweep, joyful expressions, high-energy 3D animated film style."
        }
    ]
    
    manuscript_text = "\n\n".join(p["text"] for p in paragraphs)
    scene_prompts = [p["scene_prompt"] for p in paragraphs]
    
    data = {
        "manuscript_text": manuscript_text,
        "style": "3D Pixar Disney animated film style, vibrant morning classroom lighting, expressive cute characters, cinematic depth",
        "audio_voice": "hi-IN-MadhurNeural",
        "audio_rate": "+0%",
        "audio_lang": "hi-IN",
        "audio_enabled": "true",
        "subtitle_enabled": "true",
        "video_width": "768",
        "video_height": "1152",
        "video_duration": "10",
        "reference_images_map": json.dumps([[0], [1], [2], [3]]),
    }
    
    files = []
    opened_files = []
    try:
        for i, img_path in enumerate(ref_images):
            f = open(img_path, "rb")
            opened_files.append(f)
            files.append(("reference_images", (f"ref_{i}.jpg", f, "image/jpeg")))
            
        print("📡 Submitting task to Agnes API at http://localhost:8765/api/tasks/manuscript ...")
        resp = requests.post("http://localhost:8765/api/tasks/manuscript", data=data, files=files, timeout=30)
        print("Response Status:", resp.status_code)
        res_json = resp.json()
        print("Response:", res_json)
        
        task_id = res_json.get("task_id")
        if not task_id:
            print("Failed to get task_id!")
            return
            
        print(f"\n🎬 Tracking Task {task_id} to completion...")
        while True:
            time.sleep(4)
            try:
                t_resp = requests.get(f"http://localhost:8765/api/tasks/{task_id}", timeout=15)
                task_data = t_resp.json()
                status = task_data.get("status")
                step = task_data.get("current_step")
                prog = int((task_data.get("current_progress") or 0) * 100)
                msg = task_data.get("current_message", "")
                print(f"[{status}] Step: {step} | Progress: {prog}% | Message: {msg}")
                
                if status == "completed":
                    print("\n🎉 SUCCESS! Video Generation Completed!")
                    final_file = task_data.get("final_video_file")
                    dest_file = os.path.join(output_dir, "backpack_squad_3d_reel.mp4")
                    if final_file and os.path.exists(final_file):
                        shutil.copy2(final_file, dest_file)
                        print(f"📁 Final Watermark-Free 3D Reel Saved to: {dest_file}")
                    else:
                        print(f"Working dir final video: {final_file}")
                    break
                elif status == "failed":
                    print(f"❌ Task Failed: {task_data.get('error') or msg}")
                    break
            except Exception as e:
                print(f"Poll warning: {e}")
                
    finally:
        for f in opened_files:
            f.close()

if __name__ == "__main__":
    main()
