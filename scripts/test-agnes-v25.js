const path = require('path');
const fs = require('fs');
require('dotenv').config();

const key = process.env.AGNES_API_KEY || 'sk-3YITyIgKgfWQNLT1JaSO1W0WfXtdmDbi4k3CckJBLemvUpfH';

async function testSubmit() {
  const imagePath = path.join(__dirname, '..', 'data', 'assets', 'char_aloo.jpg');
  const b64 = fs.readFileSync(imagePath).toString('base64');
  const dataUrl = `data:image/jpeg;base64,${b64}`;

  const payload = {
    model: 'agnes-video-2.5-flash',
    prompt: 'A cute 3D Pixar potato character smiling and blinking happily, cinematic lighting',
    mode: 'reference',
    seconds: '5',
    size: '720P',
    aspect_ratio: '9:16',
    images: [ dataUrl ]
  };

  console.log('Submitting Agnes v2.5 flash video payload...');
  const res = await fetch('https://apihub.agnes-ai.com/v1/videos', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  console.log('Submission response:', res.status, data);

  const videoId = data.video_id || data.task_id || data.id;
  if (!videoId) return;

  console.log('Polling task:', videoId);
  for (let i = 1; i <= 20; i++) {
    await new Promise(r => setTimeout(r, 6000));
    const pollRes = await fetch(`https://apihub.agnes-ai.com/agnesapi?video_id=${videoId}&model_name=agnes-video-2.5-flash`, {
      headers: { 'Authorization': `Bearer ${key}` }
    });
    const pollData = await pollRes.json();
    console.log(`[${i * 6}s] Poll:`, pollData.status, pollData.progress ? `${pollData.progress}%` : '', pollData.video_url || pollData.output_url || '');
    if (pollData.status === 'completed' || pollData.status === 'succeeded') {
      console.log('🎉 Video Ready URL:', pollData.video_url || pollData.output_url);
      break;
    }
  }
}

testSubmit().catch(console.error);
