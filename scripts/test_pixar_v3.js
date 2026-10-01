const { PixarVideoEngine } = require('../utils/pixar-engine/pixar-video-engine');

async function test() {
  console.log('Testing Pixar 3D Animated Video Engine V3...');
  const engine = new PixarVideoEngine();
  const res = await engine.generateAnimatedVideo({
    presetKey: 'backpack_squad',
    durationPreset: '1min',
    language: 'hindi'
  });
  console.log('Test completed successfully! Generated video:', res.videoPath);
}

test().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
