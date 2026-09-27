const { Database } = require('../database/db');

async function main() {
  const db = new Database();
  await db.initialize();

  await db.saveChannelProfile({
    channelName: 'Story Teller',
    goal: 'Create joyful, viral 3D Pixar-style animated cartoon stories, nursery rhymes, and cute costumed baby dances for toddlers and kids',
    targetAudience: 'Kids aged 1-8, toddlers, preschoolers, and parents looking for adorable, fun 3D animated baby dances, fruit costume adventures, and bedtime stories',
    brandVoice: 'Joyful, sweet, cheerful, imaginative, and filled with cute baby giggles',
    defaultStyle: 'story',
    callToAction: 'Subscribe to Story Teller for more adorable 3D baby dances and magical cartoon adventures!',
    bannedTopics: ['violence', 'scary', 'horror', 'weapons', 'politics', 'technical jargon', 'crypto', 'finance'],
    visualStyle: '3D Pixar Disney animated style, ultra cute chubby-cheeked baby in fruit costumes (pineapple, strawberry, banana) and animal outfits, joyful baby dancing, clapping hands, laughing with cute baby giggles, cozy pastel nursery room, soft studio lighting, cute teddy bears, colorful alphabet blocks, 8k cinematic render',
    timezone: 'Asia/Kolkata'
  });

  await db.setSetting('channel_name', 'Story Teller');
  await db.setSetting('default_style', 'story');
  await db.setSetting('target_audience', 'Kids aged 1-8, toddlers, preschoolers, and parents looking for adorable 3D animated baby dances, fruit costume adventures, and bedtime stories');
  await db.setSetting('video_provider', 'auto');
  await db.setSetting('video_provider_order', 'did,kling,seedance,wan,slideshow');
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
