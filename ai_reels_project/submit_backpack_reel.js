const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const http = require('http');

async function submitAndTrack() {
  console.log('🚀 Starting Backpack Squad Reel Production...');

  // 1. Prepare images
  const brainDir = "C:\\Users\\Amar's PC\\.gemini\\antigravity\\brain\\948aeb55-f992-450a-afe5-fdaa77988433";
  const assetsDir = path.join(__dirname, 'assets');
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });

  const img1 = path.join(brainDir, 'backpack_scene1_pencil_1790604281443.jpg');
  const img2 = path.join(brainDir, 'backpack_scene2_eraser_1790604294471.jpg');
  const img3 = path.join(brainDir, 'backpack_scene3_ruler_1790604311264.jpg');
  const img4 = path.join(brainDir, 'backpack_scene4_squad_1790604324147.jpg');

  const refImages = [img1, img2, img3, img4];

  // 2. Prepare Manuscript
  const paragraphs = [
    {
      text: "सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई तैयार हैं, आज तो क्लास में पूरे 10 में से 10 मार्क्स लेकर ही मानेंगे!",
      scene_prompt: "A cheerful, vibrant 3D Pixar-style animation scene inside a bright school classroom. A cute anthropomorphic yellow wooden pencil with large expressive eyes smiling excitedly while standing by a colorful backpack on a wooden desk. Morning sunlight streaming through the classroom windows, cinematic warm lighting, high-detail textures, lyrical camera push-in."
    },
    {
      text: "तभी इरेज़र रोते हुए बोला: अरे पेंसिल भाई धीरे लिखो! तुम तो गलतियां करोगे और पूरा घिसना मुझे ही पड़ेगा, मेरी तो कमर टूट जाएगी!",
      scene_prompt: "Inside a sunlit 3D animated classroom, a chubby pink and white eraser character with wide comical worried eyes and hands on its cheeks, trembling playfully beside a math notebook. Dynamic cinematic low-angle camera, exaggerated funny expressions, rich cartoon physics and soft morning light."
    },
    {
      text: "स्केल भाई शान से बोले: शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, क्लास में सब कुछ बिल्कुल सीधा और परफेक्ट रहेगा!",
      scene_prompt: "A tall, sleek transparent ruler character stands proudly with hands on hips like a superhero on a colorful notebook. Playful Pixar animation style, sunny classroom backdrop with soft depth of field, crisp reflections on the ruler surface, smooth lyrical pan."
    },
    {
      text: "तभी स्कूल की घंटी बजी: टन-टन-टन! चलो बैकपैक स्क्वाड, मिशन शुरू! आपका स्कूल में सबसे फेवरेट स्टेशनरी कौन सा था? कमेंट में बताओ!",
      scene_prompt: "The entire school stationery squad - animated yellow pencil, pink eraser, tall ruler, and a cute little blue sharpener celebrating together inside an open pencil box. Bright confetti and magical morning glow, dynamic camera sweep, joyful expressions, high-energy 3D animated film style."
    }
  ];

  const manuscriptText = paragraphs.map(p => p.text).join('\n\n');
  const scenePrompts = paragraphs.map(p => p.scene_prompt);

  const form = new FormData();
  form.append('manuscript_text', manuscriptText);
  form.append('voice', 'hi-IN-MadhurNeural');
  form.append('rate', '+0%');
  form.append('audio_enabled', 'true');
  form.append('subtitle_enabled', 'true');
  form.append('aspect_ratio', '9:16');
  form.append('video_width', '768');
  form.append('video_height', '1152');
  form.append('scene_prompts', JSON.stringify(scenePrompts));
  form.append('reference_images_map', JSON.stringify([[0], [1], [2], [3]]));

  refImages.forEach((img, idx) => {
    form.append('reference_images', fs.createReadStream(img), {
      filename: `ref_${idx}.jpg`,
      contentType: 'image/jpeg'
    });
  });

  console.log('📡 Submitting task to Agnes API at http://localhost:8765/api/tasks/manuscript ...');

  const req = http.request({
    hostname: 'localhost',
    port: 8765,
    path: '/api/tasks/manuscript',
    method: 'POST',
    headers: form.getHeaders()
  }, (res) => {
    let body = '';
    res.on('data', chunk => body += chunk);
    res.on('end', () => {
      console.log('Response Status:', res.statusCode);
      try {
        const data = JSON.parse(body);
        console.log('Task Submission Result:', data);
        if (data.task_id) {
          trackTask(data.task_id);
        } else {
          console.error('Failed to get task_id from response:', body);
        }
      } catch (err) {
        console.error('JSON parse error:', err, 'Body:', body);
      }
    });
  });

  req.on('error', (e) => {
    console.error('Request error:', e.message);
  });

  form.pipe(req);
}

function trackTask(taskId) {
  console.log(`🎬 Tracking Task ${taskId}...`);
  const interval = setInterval(() => {
    http.get(`http://localhost:8765/api/tasks/${taskId}`, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const task = JSON.parse(body);
          const progress = Math.round((task.current_progress || 0) * 100);
          console.log(`[${task.status || 'unknown'}] Step: ${task.current_step} | Progress: ${progress}% | Message: ${task.current_message || ''}`);

          if (task.status === 'completed') {
            clearInterval(interval);
            console.log('\n🎉 Task Completed successfully!');
            const outDir = path.join(__dirname, 'output');
            if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
            const destPath = path.join(outDir, 'backpack_squad_3d_reel.mp4');

            if (task.final_video_file && fs.existsSync(task.final_video_file)) {
              fs.copyFileSync(task.final_video_file, destPath);
              console.log(`📁 Video saved to: ${destPath}`);
            } else {
              console.log('Final video file path:', task.final_video_file);
            }
          } else if (task.status === 'failed') {
            clearInterval(interval);
            console.error('❌ Task Failed:', task.error || task.current_message);
          }
        } catch (e) {
          console.error('Parse tracking error:', e.message);
        }
      });
    }).on('error', (e) => {
      console.log('Track poll error:', e.message);
    });
  }, 4000);
}

submitAndTrack();
