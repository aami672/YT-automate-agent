const path = require('path');
const fs = require('fs');
require('dotenv').config();
const { AgnesVideoProvider } = require('../utils/video-providers');

async function testAgnes() {
  console.log('Testing Agnes Video Provider...');
  const provider = new AgnesVideoProvider({
    agnesApiKey: process.env.AGNES_API_KEY,
    agnesBaseUrl: process.env.AGNES_BASE_URL
  });

  console.log('Provider details:', provider.describe());

  const imagePath = path.join(__dirname, '..', 'data', 'assets', 'char_aloo.jpg');
  console.log('Using image:', imagePath, 'exists:', fs.existsSync(imagePath));

  const task = await provider.createTask({
    prompt: '3D Pixar animated potato character looking happy, blinking eyes and smiling warmly, cinematic studio lighting',
    firstFrame: imagePath,
    duration: 5,
    aspectRatio: '9:16'
  });

  console.log('Submitted task successfully:', task);
  console.log('Polling task status...');

  let attempts = 0;
  while (attempts < 30) {
    await new Promise(r => setTimeout(r, 5000));
    attempts++;
    const check = await provider.getTask(task.externalTaskId);
    console.log(`[${attempts * 5}s] Task status:`, check.status, 'outputUrl:', check.outputUrl || 'pending');
    if (check.status === 'succeeded' && check.outputUrl) {
      const outPath = path.join(__dirname, '..', 'data', 'videos', 'test_agnes_aloo_output.mp4');
      await provider.downloadResult(check, outPath);
      console.log('✅ Video downloaded successfully to:', outPath);
      break;
    }
    if (check.status === 'failed') {
      console.error('❌ Task failed:', check.error);
      break;
    }
  }
}

testAgnes().catch(err => {
  console.error('Test error:', err.response?.data || err.message || err);
});
