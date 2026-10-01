import os
import sys
import json
import time
import requests
import shutil

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("[*] Submitting Zero-Jitter Stabilized Backpack Squad Reel...")
    
    brain_dir = r"C:\Users\Amar's PC\.gemini\antigravity\brain\948aeb55-f992-450a-afe5-fdaa77988433"
    ai_reels_dir = r"C:\Users\Amar's PC\.gemini\antigravity\scratch\ai_reels_project"
    output_dir = os.path.join(ai_reels_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    img1 = os.path.join(brain_dir, "backpack_scene1_pencil_1790604281443.jpg")
    img2 = os.path.join(brain_dir, "backpack_scene2_eraser_1790604294471.jpg")
    img3 = os.path.join(brain_dir, "backpack_scene3_ruler_1790604311264.jpg")
    img4 = os.path.join(brain_dir, "backpack_scene4_squad_1790604324147.jpg")
    
    ref_images = [img1, img2, img3, img4]
    
    paragraphs = [
        {
            "text": "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे 10 में से 10 मार्क्स लेकर ही मानेंगे!",
            "scene_prompt": "A delightful 3D Pixar Disney animation scene. Cute anthropomorphic yellow wooden pencil smiling cheerfully in an organized sunlit classroom. Smooth continuous character motion, perfectly stable locked-off cinematic camera with gentle slow-motion push-in. High temporal stability, crystal clear crisp geometry, soft warm ambient lighting, fluid lifelike animation, no camera shake, zero jitter."
        },
        {
            "text": "तभी इरेज़र रोते हुए बोला: अरे पेंसिल भाई धीरे लिखो! तुम तो गलतियां करोगे और पूरा घिसना मुझे ही पड़ेगा, मेरी तो कमर टूट जाएगी!",
            "scene_prompt": "A charming 3D Pixar Disney animation scene. Cute pink and white eraser character with comical expressive worried eyes, standing smoothly by an open math notebook. Fluid gentle breathing animation and soft gestures, stable locked camera with smooth steady glide, clear textures, perfectly continuous 3D lighting, no camera shake, zero jitter."
        },
        {
            "text": "स्केल भाई शान से बोले: शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, क्लास में सब कुछ बिल्कुल सीधा और परफेक्ट रहेगा!",
            "scene_prompt": "A vibrant 3D Pixar Disney animation scene. Sleek tall clear plastic ruler character standing proudly with hands on hips like a cheerful superhero on a notebook. Smooth subtle head nod, steady locked cinematic framing, clean reflections, continuous fluid motion, zero camera shake, zero jitter."
        },
        {
            "text": "तभी स्कूल की घंटी बजी: टन-टन-टन! चलो बैकपैक स्क्वाड, मिशन शुरू! आपका स्कूल में सबसे फेवरेट स्टेशनरी कौन सा था? कमेंट में बताओ!",
            "scene_prompt": "The entire stationery squad celebrating together inside a vibrant pencil box. High-detail 3D Pixar film quality, fluid gentle cheer animations, stable smooth wide camera framing, soft golden morning light, perfectly steady continuous video, zero jitter."
        }
    ]
    
    manuscript_text = "\n\n".join(p["text"] for p in paragraphs)
    scene_prompts = [p["scene_prompt"] for p in paragraphs]
    
    data = {
        "manuscript_text": manuscript_text,
        "style": "Ultra-stable 3D Pixar Disney animated film style, perfectly locked smooth camera, continuous fluid motion, high temporal consistency, zero jitter",
        "audio_voice": "hi-IN-MadhurNeural",
        "audio_rate": "+0%",
        "audio_lang": "hi-IN",
        "audio_enabled": "true",
        "subtitle_enabled": "true",
        "video_width": "768",
        "video_height": "1152",
        "video_duration": "10",
        "scene_prompts": json.dumps(scene_prompts, ensure_ascii=False),
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
            time.sleep(5)
            try:
                t_resp = requests.get(f"http://localhost:8765/api/tasks/{task_id}", timeout=15)
                task_data = t_resp.json()
                status = task_data.get("status")
                step = task_data.get("current_step")
                prog = int((task_data.get("current_progress") or 0) * 100)
                msg = task_data.get("current_message", "")
                print(f"[{status}] Step: {step} | Progress: {prog}% | Message: {msg}")
                
                if status == "completed":
                    print("\n🎉 SUCCESS! Zero-Jitter Video Generation Completed!")
                    final_file = task_data.get("final_video_file")
                    dest_file = os.path.join(output_dir, "backpack_squad_zero_jitter.mp4")
                    if final_file and os.path.exists(final_file):
                        shutil.copy2(final_file, dest_file)
                        print(f"📁 Final Zero-Jitter Reel Saved to: {dest_file}")
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
