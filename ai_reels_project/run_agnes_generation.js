const fs = require('fs');
const path = require('path');

const AGNES_API_URL = "http://localhost:8765/api/tasks/manuscript";
const assetsDir = path.join(__dirname, 'assets');
const outputDir = path.join(__dirname, 'output');

const scriptText = `जब आलू को हुआ गोभी से प्यार! गोभी जी, जब से आपको सब्ज़ी मंडी में देखा है, मेरा दिल सिर्फ आपके लिए धड़कता है! मैं आपके बिना नहीं रह सकता!
तभी लाल टमाटर आ गया: ओए गोलू आलू, साइड हट! गोभी तो सिर्फ मेरी बनेगी! देख मेरा लाल रंग और स्वैग, तेरे जैसा बोरिंग नहीं हूँ मैं!
आलू बोला: अरे टमाटर भाई, तुम तो दो दिन में गल जाओगे, मैं आलू हूँ, हर डिश में साथ निभाता हूँ! पर गोभी हंसी: हाय राम, मैं तो सिर्फ मटर जी के साथ जोड़ी बनाती हूँ!
तभी छोटा मटर बोला: चलो हटो सब, अब गोभी-मटर का ज़माना है! आपकी पसंदीदा सब्ज़ी कौन सी है? कमेंट में बताओ और फॉलो करो!`;

async function submitAgnesTask() {
  console.log("==================================================================");
  console.log("🚀 Submitting Task to Agnes Video Generator with Locked Assets...");
  console.log("==================================================================");

  const formData = new FormData();
  formData.append("manuscript_text", scriptText);
  formData.append("creative_name", "Aloo_Gobhi_Pixar_Reel_3D");
  formData.append("style", "3D Pixar Animation, Vibrant Colors, Expressive Eyes, Cute Cartoon Sabzi Mandi, Cinematic Lighting, High-Detail Produce Textures");
  formData.append("video_width", "768");
  formData.append("video_height", "1152");
  formData.append("audio_enabled", "true");
  formData.append("audio_voice", "hi-IN-MadhurNeural");
  formData.append("audio_lang", "hi");
  formData.append("audio_rate", "+0%");
  formData.append("subtitle_enabled", "true");

  // Pass the 4 locked scene reference images
  const refImages = [
    { file: 'scene1.jpg', paraIdx: 0 },
    { file: 'scene2.jpg', paraIdx: 1 },
    { file: 'scene3.jpg', paraIdx: 2 },
    { file: 'scene4.jpg', paraIdx: 3 }
  ];

  const map = [];
  for (let i = 0; i < refImages.length; i++) {
    const imgPath = path.join(assetsDir, refImages[i].file);
    if (fs.existsSync(imgPath)) {
      const buffer = fs.readFileSync(imgPath);
      const blob = new Blob([buffer], { type: 'image/jpeg' });
      formData.append("reference_images", blob, refImages[i].file);
      map.push([refImages[i].paraIdx]);
      console.log(`🖼️ Attached Reference Image for Scene ${i + 1}: ${refImages[i].file}`);
    }
  }

  formData.append("reference_images_map", JSON.stringify(map));

  console.log("\n📡 Sending request to Agnes Video Generator on port 8765...");
  try {
    const res = await fetch(AGNES_API_URL, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    console.log("Response from Agnes:", data);

    if (data.task_id) {
      console.log(`\n✅ Task Created! ID: ${data.task_id}`);
      console.log(`📁 Working Dir: ${data.dir_name}`);
      console.log(`\n⏳ Tracking progress...`);
      await pollTask(data.task_id);
    } else {
      console.error("❌ Submission failed:", data);
    }
  } catch (err) {
    console.error("❌ Failed to connect to Agnes server:", err.message);
  }
}

async function pollTask(taskId) {
  let isDone = false;
  while (!isDone) {
    await new Promise(r => setTimeout(r, 4000));
    try {
      const res = await fetch(`http://localhost:8765/api/tasks/${taskId}`);
      const state = await res.json();
      const progress = Math.round((state.current_progress || 0) * 100);
      console.log(`[${state.current_step || 'running'}] Progress: ${progress}% - ${state.current_message || ''}`);

      if (state.status === "completed" || state.current_status === "completed") {
        isDone = true;
        console.log("\n🎉 VIDEO GENERATION COMPLETED!");
        if (state.final_video_file && fs.existsSync(state.final_video_file)) {
          const dest = path.join(outputDir, "agnes_final_3d_reel.mp4");
          fs.copyFileSync(state.final_video_file, dest);
          console.log(`✅ Final Watermark-Free 3D Reel saved to:\n${dest}`);
        }
      } else if (state.status === "failed" || state.status === "error") {
        isDone = true;
        console.error("❌ Task failed:", state.error_traceback || state.current_message);
      }
    } catch (e) {
      console.warn("Poll error:", e.message);
    }
  }
}

submitAgnesTask();
