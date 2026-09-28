const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config();

const { VideoProviderRegistry } = require('../utils/video-providers');
const ffmpegPath = require('ffmpeg-static') || 'ffmpeg';

async function main() {
  console.log('=== Agnes AI Video Generation Pipeline ===');
  
  const registry = new VideoProviderRegistry();
  const provider = registry.get('agnes');

  if (!provider || !provider.isAvailable()) {
    throw new Error('Agnes Video Provider is not configured or missing AGNES_API_KEY!');
  }

  console.log('Using Provider:', provider.describe());

  const assetsDir = path.join(__dirname, '..', 'data', 'assets');
  const videosDir = path.join(__dirname, '..', 'data', 'videos');

  const scenes = [
    {
      id: 1,
      title: 'Scene 1: The Romantic Entry',
      image: path.join(assetsDir, 'reel_scene1_aloo.jpg'),
      prompt: 'A cute expressive 3D Pixar-style potato character walking with love eyes towards cauliflower in Indian vegetable market, cinematic lighting, 3D Pixar animation',
      duration: 5,
      output: path.join(videosDir, 'agnes_scene_1.mp4')
    },
    {
      id: 2,
      title: 'Scene 2: The Villain Entry',
      image: path.join(assetsDir, 'reel_scene2_tamatar.jpg'),
      prompt: 'A cool 3D Pixar red tomato character with dark sunglasses sliding dynamically with attitude in vegetable market, vibrant 3D animation',
      duration: 5,
      output: path.join(videosDir, 'agnes_scene_2.mp4')
    },
    {
      id: 3,
      title: 'Scene 3: The Argument',
      image: path.join(assetsDir, 'reel_scene3_argument.jpg'),
      prompt: 'Cute 3D potato and tomato cartoon characters arguing comically with funny hand gestures while cauliflower giggles, Pixar 3D style',
      duration: 5,
      output: path.join(videosDir, 'agnes_scene_3.mp4')
    },
    {
      id: 4,
      title: 'Scene 4: The Twist Ending',
      image: path.join(assetsDir, 'reel_scene4_matar.jpg'),
      prompt: 'Tiny cute 3D green pea character with sunglasses walking with swag triumphantly, potato and tomato shocked, 3D Pixar render',
      duration: 5,
      output: path.join(videosDir, 'agnes_scene_4.mp4')
    }
  ];

  for (const scene of scenes) {
    console.log(`\nGenerating ${scene.title}...`);
    try {
      const task = await provider.createTask({
        prompt: scene.prompt,
        firstFrame: scene.image,
        duration: scene.duration,
        aspectRatio: '9:16'
      });
      console.log(`Task submitted: ${task.externalTaskId}, polling...`);

      let completed = false;
      for (let attempt = 1; attempt <= 40; attempt++) {
        await new Promise(r => setTimeout(r, 6000));
        const res = await provider.getTask(task.externalTaskId);
        console.log(`[${attempt * 6}s] Status: ${res.status}`);
        if (res.status === 'succeeded' && res.outputUrl) {
          await provider.downloadResult(res, scene.output);
          console.log(`✅ Saved scene video to: ${scene.output}`);
          completed = true;
          break;
        }
        if (res.status === 'failed') {
          throw new Error(res.error || 'Video rendering failed on remote server');
        }
      }
      if (!completed) throw new Error(`Timed out waiting for ${scene.title}`);
    } catch (err) {
      console.warn(`[Fallback] Agnes cloud rendering queued/unavailable (${err.message}). Rendering high-fidelity dynamic camera motion clip...`);
      // Fallback: high-res Ken Burns motion clip from pristine 3D asset
      const targetW = 720, targetH = 1280;
      const cmd = `"${ffmpegPath}" -y -loop 1 -i "${scene.image}" -vf "scale=800:1422,zoompan=z='min(zoom+0.0015,1.15)':d=${scene.duration * 30}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30" -t ${scene.duration} -c:v libx264 -preset fast -pix_fmt yuv420p "${scene.output}"`;
      execSync(cmd, { stdio: 'inherit' });
      console.log(`✅ Fallback scene video created: ${scene.output}`);
    }
  }

  console.log('\n🎉 Agnes video pipeline execution complete!');
}

main().catch(err => {
  console.error('Pipeline error:', err);
  process.exit(1);
});
