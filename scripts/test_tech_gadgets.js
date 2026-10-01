const { PixarVideoEngine } = require('../utils/pixar-engine/pixar-video-engine');

async function main() {
  console.log('Testing Pixar 3D Animated Video Engine on Tech Gadgets Story...');
  const engine = new PixarVideoEngine();
  const res = await engine.generateAnimatedVideo({
    presetKey: 'tech_gadgets',
    durationPreset: '1min',
    language: 'hindi'
  });
  console.log('Test result:', res.success ? 'SUCCESS' : 'FAILED', res.videoPath);
}

main().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
