const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'data', 'youtube_automation.db');
const db = new sqlite3.Database(dbPath);

const prodId = 'prod_pixar_story_reel_' + Date.now();
const scriptId = 'script_pixar_story_reel_' + Date.now();
const title = '🥔 जब आलू को हुआ गोभी से प्यार | 3D Pixar Hindi Reel';
const videoPath = path.join(__dirname, '..', 'data', 'videos', 'jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4');

const scriptData = {
  id: scriptId,
  title: title,
  hook: 'गोभी जी! जब से आपको सब्ज़ी मंडी में देखा है, मेरा दिल सिर्फ आपके लिए धड़कता है!',
  introduction: 'सब्ज़ी मंडी में आलू और टमाटर के बीच गोभी के प्यार का महा-मुकाबला!',
  main_content: 'Scene 1: आलू का प्रपोजल। Scene 2: टमाटर की विलेन एंट्री और स्वैग। Scene 3: आलू और टमाटर की नोकझोंक व गोभी का जवाब। Scene 4: मटर जी की ट्विस्ट एंट्री!',
  conclusion: 'आपकी पसंदीदा सब्ज़ी कौन सी है? कमेंट में बताओ और फॉलो करो!',
  call_to_action: 'लाइक और सब्सक्राइब करना न भूलें!',
  full_script: 'जब आलू को हुआ गोभी से प्यार - 3D Pixar Hindi Short'
};

const assetsObj = {
  finalVideo: videoPath,
  videoPath: videoPath,
  videoUrl: '/videos/jab_aloo_ko_hua_gobhi_se_pyar_final_reel.mp4',
  engine: '3D Pixar Diffusion + Microsoft Azure Hindi Neural Voice Pipeline',
  scenes: [
    'Scene 1: The Romantic Entry (Aloo & Gobhi in Mandi)',
    'Scene 2: The Villain Entry (Tamatar with Sunglasses)',
    'Scene 3: The Argument & Gobhi’s Choice',
    'Scene 4: The Twist Ending (Matar Swag Entry)'
  ],
  resolution: '720x1280 (9:16 Vertical)',
  fps: 30,
  file_size_bytes: fs.existsSync(videoPath) ? fs.statSync(videoPath).size : 0
};

db.serialize(() => {
  db.run(
    'INSERT OR REPLACE INTO scripts (id, title, hook, introduction, main_content, conclusion, call_to_action, full_script) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    [scriptData.id, scriptData.title, scriptData.hook, scriptData.introduction, scriptData.main_content, scriptData.conclusion, scriptData.call_to_action, scriptData.full_script],
    (err) => {
      if (err) console.error('Error inserting script:', err);
      else console.log('✅ Script record inserted successfully.');
    }
  );

  db.run(
    'INSERT OR REPLACE INTO productions (id, script_id, status, assets, estimated_duration) VALUES (?, ?, ?, ?, ?)',
    [prodId, scriptId, 'completed', JSON.stringify(assetsObj), '00:48'],
    (err) => {
      if (err) console.error('Error inserting production:', err);
      else console.log(`✅ Production record ${prodId} registered successfully in DB!`);
    }
  );
});

db.close();
