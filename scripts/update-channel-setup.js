const { Database } = require('../database/db');

async function main() {
  const db = new Database();
  await db.initialize();

  await db.saveChannelProfile({
    channelName: 'Story Teller',
    goal: 'Become the most beloved family-friendly 3D cartoon channel for kids moral stories and rhymes',
    targetAudience: 'Kids aged 2-10, toddlers, preschoolers, and parents looking for safe, fun 3D animated cartoon stories and rhymes',
    brandVoice: 'Warm, cheerful, imaginative, and friendly',
    defaultStyle: 'story',
    callToAction: 'Subscribe to Story Teller for more magical cartoon adventures!',
    bannedTopics: ['violence', 'scary', 'horror', 'weapons', 'politics', 'technical jargon'],
    visualStyle: 'Vibrant Pixar 3D cartoon style, rich colors, expressive characters, soft studio lighting',
    timezone: 'Asia/Kolkata'
  });

  await db.setSetting('channel_name', 'Story Teller');
  await db.setSetting('default_style', 'story');
  await db.setSetting('target_audience', 'Kids aged 2-10, toddlers, preschoolers, and parents looking for safe, fun 3D animated cartoon stories and rhymes');
  await db.setSetting('video_provider', 'auto');
  await db.setSetting('video_provider_order', 'kling,seedance,wan,slideshow');
  await db.setSetting('video_generation_mode', 'hybrid');
  await db.setSetting('video_clip_duration', '8');
  await db.setSetting('video_max_generated_seconds', '60');
  await db.setSetting('require_approval', 'true');

  console.log('✅ Channel profile and settings permanently saved in database!');
  process.exit(0);
}

main().catch(err => {
  console.error('Error saving settings:', err);
  process.exit(1);
});
