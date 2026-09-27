const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'data', 'youtube_automation.db');
const db = new sqlite3.Database(dbPath);

const prodId = 'prod_did_neural_story_' + Date.now();
const scriptId = 'script_did_neural_story_' + Date.now();
const title = '🥔 आलू, टमाटर और गोभी की प्रेम कहानी | Live 3D Neural Animation';
const videoPath = path.join(__dirname, '..', 'data', 'videos', 'final_aloo_tamatar_gobhi_story.mp4');

const scriptData = {
  id: scriptId,
  title: title,
  hook: 'गोभी जी, क्या आप मुझसे शादी करेंगी?',
  introduction: 'आलू और टमाटर के बीच गोभी के प्यार की अनोखी दास्तान।',
  main_content: 'आलू: गोभी जी, क्या आप मुझसे शादी करेंगी? टमाटर: ओए गोलू आलू! साइड हट! गोभी तो सिर्फ मेरी बनेगी! गोभी: हाय राम! तुम दोनों लड़ना बंद करो! मैं तो सिर्फ मटर जी के साथ जाऊँगी!',
  conclusion: 'सब्जियों का ये ड्रामा कभी खत्म नहीं होगा!',
  call_to_action: 'लाइक और सब्सक्राइब करना न भूलें!',
  full_script: 'आलू, टमाटर और गोभी की लाइव एनिमेटेड कहानी'
};

const assetsObj = {
  finalVideo: videoPath,
  videoPath: videoPath,
  videoUrl: '/videos/final_aloo_tamatar_gobhi_story.mp4',
  engine: 'D-ID Neural Talks API',
  model: 'Imagen 3D Pixar + Azure Hindi Neural Voice',
  characters: ['आलू (hi-IN-MadhurNeural)', 'टमाटर (hi-IN-MadhurNeural)', 'गोभी (hi-IN-SwaraNeural)'],
  resolution: '720x1280 (9:16 Shorts)',
  fps: 30,
  file_size_bytes: fs.existsSync(videoPath) ? fs.statSync(videoPath).size : 0
};

db.serialize(() => {
  db.run(
    `INSERT OR REPLACE INTO scripts (id, title, hook, introduction, main_content, conclusion, call_to_action, full_script)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [scriptData.id, scriptData.title, scriptData.hook, scriptData.introduction, scriptData.main_content, scriptData.conclusion, scriptData.call_to_action, scriptData.full_script],
    (err) => {
      if (err) console.error('Error inserting script:', err);
      else console.log('✅ Script record inserted successfully.');
    }
  );

  db.run(
    `INSERT OR REPLACE INTO productions (id, script_id, status, assets, estimated_duration)
     VALUES (?, ?, ?, ?, ?)`,
    [prodId, scriptId, 'completed', JSON.stringify(assetsObj), '00:30'],
    (err) => {
      if (err) console.error('Error inserting production:', err);
      else console.log(`✅ Production record ${prodId} registered successfully in DB!`);
    }
  );
});

db.close(() => {
  console.log('Database connection closed.');
});
