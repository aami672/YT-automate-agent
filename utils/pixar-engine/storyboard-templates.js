/**
 * Pixar 3D Animated Reel Storyboard Templates & Universal Script Parser
 * Supports 1-Minute, 2-Minute, and 3-Minute durations with multi-character cartoon voices.
 */

const VOICE_PROFILES = {
  hindi: {
    hero: { voice: 'hi-IN-MadhurNeural', pitch: '+18Hz', rate: '+8%' },
    squeaky: { voice: 'hi-IN-SwaraNeural', pitch: '+32Hz', rate: '+5%' },
    fast_tech: { voice: 'hi-IN-SwaraNeural', pitch: '+18Hz', rate: '+10%' },
    deep_hero: { voice: 'hi-IN-MadhurNeural', pitch: '-22Hz', rate: '-8%' },
    action: { voice: 'hi-IN-MadhurNeural', pitch: '+14Hz', rate: '+6%' },
    outro: { voice: 'hi-IN-MadhurNeural', pitch: '+20Hz', rate: '+8%' }
  },
  english: {
    hero: { voice: 'en-US-ChristopherNeural', pitch: '+14Hz', rate: '+6%' },
    squeaky: { voice: 'en-US-AnaNeural', pitch: '+26Hz', rate: '+5%' },
    fast_tech: { voice: 'en-US-JennyNeural', pitch: '+16Hz', rate: '+8%' },
    deep_hero: { voice: 'en-US-GuyNeural', pitch: '-18Hz', rate: '-6%' },
    action: { voice: 'en-US-ChristopherNeural', pitch: '+12Hz', rate: '+6%' },
    outro: { voice: 'en-US-JennyNeural', pitch: '+18Hz', rate: '+8%' }
  }
};

const STORY_PRESETS = {
  backpack_squad: {
    title: 'School Backpack Squad: The First Period Mission',
    genre: 'Pixar 3D School Comedy',
    description: 'When the school bell rings, the backpack stationery comes alive for an epic adventure!',
    tags: ['pixar', '3danimation', 'backpacksquad', 'cartoon', 'animation', 'reels', 'shorts', 'funny'],
    scenes_1min: [
      {
        scene_index: 1,
        title: 'Pencil Hero Wakes Up',
        character: 'Pencil Hero',
        voice_type: 'hero',
        dialogue: 'Arey dosto! Dekho subah ho gayi, school bag khulne wala hai! Aaj hum sabko geometry box aur notebook me rock karna hai!',
        visual_prompt: 'Pixar 3D style upright yellow wooden pencil character with pink eraser top, big expressive cartoon eyes and happy smile, inside open school backpack, cinematic volumetric morning sunlight, vibrant colors, 9:16 vertical composition.'
      },
      {
        scene_index: 2,
        title: 'Panicky Eraser Joins',
        character: 'Panicky Eraser',
        voice_type: 'squeaky',
        dialogue: 'Lekin Maths test ka kya?! Vo difficult algebra sums... agar galti hui toh mujhe apna sir ghis ghis ke mitana padega! Meri shaving kamzor ho jayegi!',
        visual_prompt: 'Pixar 3D style cute pink and blue wedge eraser with surprised cartoon eyes and open mouth, sitting nervously on notebook, soft shadow, clean studio lighting, 9:16 vertical composition.'
      },
      {
        scene_index: 3,
        title: 'Sharpener Power Up',
        character: 'Sharpener Tech',
        voice_type: 'fast_tech',
        dialogue: 'Tension mat lo Eraser bhai! Mera high-speed blade ready hai! Pencil ko 2 second me supersonic laser tip bana dunga!',
        visual_prompt: 'Pixar 3D style metallic sky-blue pencil sharpener with shiny steel blade, wearing glowing futuristic goggles with clever grin, vibrant 9:16 vertical composition.'
      },
      {
        scene_index: 4,
        title: 'Ruler Superhero Steps In',
        character: 'Ruler Superhero',
        voice_type: 'deep_hero',
        dialogue: 'Darne ki koi baat nahi! Mai 30 centimeter ka Ruler hu! Mera line hamesha 100 percent straight hota hai!',
        visual_prompt: 'Pixar 3D style wooden ruler standing tall like a superhero with mini red cape and measurement markings, confident heroic posture, dynamic cinematic rim lighting, 9:16 vertical composition.'
      },
      {
        scene_index: 5,
        title: 'Squad Action Formation',
        character: 'Backpack Squad',
        voice_type: 'action',
        dialogue: 'Backpack Squad... Ready for Action! Pencil sharp, Ruler straight, Eraser alert! Aaj top score hamara hi hoga!',
        visual_prompt: 'Pixar 3D style full backpack squad group standing together heroically on school desk, pencil, eraser, sharpener, and ruler, vibrant colors, cinematic depth of field, 9:16 vertical composition.'
      },
      {
        scene_index: 6,
        title: 'School Bell Outro & CTA',
        character: 'Hero Outro',
        voice_type: 'outro',
        dialogue: 'Oye school bell baj gayi! Chalo fatatafat channel ko Like aur Subscribe karo, aur apna favorite stationery comment karo!',
        visual_prompt: 'Pixar 3D style golden school bell ringing with soundwave sparks, backpack squad waving cheerfully to the camera, golden confetti, vibrant 9:16 vertical composition.'
      }
    ]
  },
  kitchen_heist: {
    title: 'Midnight Kitchen Utensils: The Midnight Snack Heist',
    genre: 'Pixar 3D Kitchen Adventure',
    description: 'When humans go to sleep, the kitchen appliances execute the greatest golden toast mission!',
    tags: ['pixar', 'kitchenadventure', 'animation', 'cartoon', 'shorts', 'funny'],
    scenes_1min: [
      {
        scene_index: 1,
        title: 'Chef Fork Gives Briefing',
        character: 'Chef Fork',
        voice_type: 'hero',
        dialogue: 'Suno sabhi utensils! Fridge ka door band ho chuka hai, kitchen lights off hain. Tonight is Operation Golden Toast!',
        visual_prompt: 'Pixar 3D style shiny silver fork with cute cartoon chef hat and expressive eyes, standing on marble kitchen counter, moonlight beam, 9:16 vertical.'
      },
      {
        scene_index: 2,
        title: 'Nervous Pepper Shaker',
        character: 'Pepper Shaker',
        voice_type: 'squeaky',
        dialogue: 'Lekin Chef! Agar kisine sneeze kar diya toh microwave ka alarm baj jayega! Hum sab Pakde jayenge!',
        visual_prompt: 'Pixar 3D style cute glass pepper shaker shivering with wide nervous cartoon eyes, spice dust particles sparkling in moonlight, 9:16 vertical.'
      },
      {
        scene_index: 3,
        title: 'Spatula Speed Flips',
        character: 'Spatula Master',
        voice_type: 'fast_tech',
        dialogue: 'Chill karo dosto! Meri 360-degree flip technique ke aage koi toast bach nahi sakta! Butter ready, pan hot!',
        visual_prompt: 'Pixar 3D style vibrant red silicone spatula doing dynamic acrobatic flip in mid-air, glowing kitchen ambient lights, 9:16 vertical.'
      },
      {
        scene_index: 4,
        title: 'Heavyweight Chef Knife',
        character: 'Chef Knife',
        voice_type: 'deep_hero',
        dialogue: 'Rasta saaf hai. Mai hu Knife commander. Clean cut, zero noise. Toast buttering begins now!',
        visual_prompt: 'Pixar 3D style sturdy polished chef knife with heroic mask and confident smile standing guarding the cutting board, 9:16 vertical.'
      },
      {
        scene_index: 5,
        title: 'Golden Toast Victory',
        character: 'Kitchen Squad',
        voice_type: 'action',
        dialogue: 'Mission accomplished! Crunchy, golden, and delicious! Hamari kitchen squad kabhi haar nahi manti!',
        visual_prompt: 'Pixar 3D style golden crispy toast glowing with butter steam, all cute kitchen utensils cheering and celebrating together, 9:16 vertical.'
      },
      {
        scene_index: 6,
        title: 'Kitchen Outro & CTA',
        character: 'Chef Fork',
        voice_type: 'outro',
        dialogue: 'Aisi aur mazedaar kitchen stories dekhne ke liye video ko Like karo aur channel Subscribe karna mat bhoolna!',
        visual_prompt: 'Pixar 3D style friendly chef fork waving with shiny spark stars, thumbs up subscribe badge, 9:16 vertical.'
      }
    ]
  },
  tech_gadgets: {
    title: 'Secret Life of Smart Gadgets: The Low Battery Emergency',
    genre: 'Pixar 3D Tech Comedy',
    description: 'When the battery hits 1%, the gadget squad unites for an electrifying turbo charge!',
    tags: ['pixar', 'gadgetsquad', 'techcomedy', 'animation', 'reels', 'shorts'],
    scenes_1min: [
      {
        scene_index: 1,
        title: 'Smartphone Panics at 1%',
        character: 'Smartphone Boss',
        voice_type: 'hero',
        dialogue: 'Emergency alert! Battery sirf 1 percent bachi hai aur screen dim ho rahi hai! Mujhe turant power chahiye!',
        visual_prompt: 'Pixar 3D style sleek smartphone character with glowing red 1% battery icon on screen, sweating cartoon expression, 9:16 vertical.'
      },
      {
        scene_index: 2,
        title: 'Nervous Earbuds Shiver',
        character: 'Wireless Earbuds',
        voice_type: 'squeaky',
        dialogue: 'Oh no! Agar phone switch off ho gaya toh humara party playlist band ho jayega! Hum bekar ho jayenge!',
        visual_prompt: 'Pixar 3D style twin white wireless earbuds hopping with worried cartoon eyes, musical notes hovering in air, 9:16 vertical.'
      },
      {
        scene_index: 3,
        title: 'Power Bank Heavyweight Hero',
        character: 'Power Bank',
        voice_type: 'deep_hero',
        dialogue: 'Ghabrao mat! 20000 mAh ka powerhouse mai hu! Rapid charge delivery shuru karta hu!',
        visual_prompt: 'Pixar 3D style muscular matte black power bank with glowing green battery bars flexing heroically, 9:16 vertical.'
      },
      {
        scene_index: 4,
        title: 'Turbo Cable Speed Connection',
        character: 'Turbo Cable',
        voice_type: 'fast_tech',
        dialogue: 'Braided Type-C cable active! High-speed 65W fast charging in 3, 2, 1... Connected!',
        visual_prompt: 'Pixar 3D style neon blue braided USB cable zooming and plugging in with glowing lightning spark effects, 9:16 vertical.'
      },
      {
        scene_index: 5,
        title: '100% Supercharged Party',
        character: 'Gadget Squad',
        voice_type: 'action',
        dialogue: '100 percent supercharged! Lights, music, gaming mode activated! Squad is back in full power!',
        visual_prompt: 'Pixar 3D style fully charged phone radiating vibrant rainbow neon glow, power bank and earbuds dancing with joy, 9:16 vertical.'
      },
      {
        scene_index: 6,
        title: 'Tech Outro & CTA',
        character: 'Smartphone Boss',
        voice_type: 'outro',
        dialogue: 'Video pasand aayi toh jaldi se Like aur Subscribe ka button dabao aur apna phone model comment karo!',
        visual_prompt: 'Pixar 3D style cheerful smartphone taking a selfie with gadget squad, like and subscribe icons bursting with confetti, 9:16 vertical.'
      }
    ]
  }
};

/**
 * Expand a 6-scene story preset to 12 scenes (2-minute) or 18 scenes (3-minute)
 */
function expandStoryPreset(presetKey, targetDurationKey = '1min', language = 'hindi') {
  const preset = STORY_PRESETS[presetKey] || STORY_PRESETS.backpack_squad;
  const baseScenes = preset.scenes_1min;
  const voices = VOICE_PROFILES[language] || VOICE_PROFILES.hindi;
  
  if (targetDurationKey === '1min') {
    return {
      title: preset.title,
      genre: preset.genre,
      tags: preset.tags,
      storyboard: baseScenes.map(s => ({
        ...s,
        voice: voices[s.voice_type]?.voice || voices.hero.voice,
        pitch: voices[s.voice_type]?.pitch || '+18Hz',
        rate: voices[s.voice_type]?.rate || '+8%',
        target_duration: 9.5
      }))
    };
  }

  const numScenes = targetDurationKey === '3min' ? 18 : 12;
  const expandedScenes = [];
  
  for (let i = 0; i < numScenes; i++) {
    const base = baseScenes[i % baseScenes.length];
    const cycle = Math.floor(i / baseScenes.length) + 1;
    const sceneIndex = i + 1;
    
    let dialogue = base.dialogue;
    let title = `${base.title} (Part ${cycle})`;
    
    if (cycle === 2) {
      dialogue = `Round 2! ` + dialogue;
    } else if (cycle === 3) {
      dialogue = `Ultimate Stage! ` + dialogue;
    }
    
    expandedScenes.push({
      scene_index: sceneIndex,
      title: i === numScenes - 1 ? 'Epic Grand Finale & Outro' : title,
      character: base.character,
      voice_type: i === numScenes - 1 ? 'outro' : base.voice_type,
      voice: voices[base.voice_type]?.voice || voices.hero.voice,
      pitch: voices[base.voice_type]?.pitch || '+18Hz',
      rate: voices[base.voice_type]?.rate || '+8%',
      dialogue: i === numScenes - 1 ? 'Dosto video ko Like aur Subscribe karo aur agle episode ke liye comment karo!' : dialogue,
      visual_prompt: base.visual_prompt,
      target_duration: 9.5
    });
  }

  return {
    title: `${preset.title} (${targetDurationKey === '3min' ? '3-Min Epic' : '2-Min Extended'})`,
    genre: preset.genre,
    tags: preset.tags,
    storyboard: expandedScenes
  };
}

/**
 * Universal Script Parser: Takes any user script text and converts it into a structured storyboard
 */
function parseCustomScriptToStoryboard(scriptText, durationKey = '1min', language = 'hindi') {
  const voices = VOICE_PROFILES[language] || VOICE_PROFILES.hindi;
  const numScenes = durationKey === '3min' ? 18 : durationKey === '2min' ? 12 : 6;
  
  const rawLines = (scriptText || '')
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0);

  const voiceTypeSequence = ['hero', 'squeaky', 'fast_tech', 'deep_hero', 'action', 'outro'];
  const characterPool = ['Lead Hero', 'Funny Sidekick', 'Tech Wizard', 'Strong Protector', 'Squad Ally', 'Story Narrator'];

  const scenes = [];

  if (rawLines.length === 0) {
    // Return default shuffled preset if empty
    return expandStoryPreset('backpack_squad', durationKey, language);
  }

  // Parse lines into dialogue scenes
  for (let i = 0; i < numScenes; i++) {
    const sceneIndex = i + 1;
    const vType = i === numScenes - 1 ? 'outro' : voiceTypeSequence[i % voiceTypeSequence.length];
    const defaultChar = characterPool[i % characterPool.length];
    
    let line = rawLines[i % rawLines.length];
    let character = defaultChar;
    let dialogue = line;

    // Check if line is in format "Character: Dialogue"
    if (line.includes(':')) {
      const parts = line.split(':');
      character = parts[0].trim();
      dialogue = parts.slice(1).join(':').trim();
    }

    const voiceCfg = voices[vType] || voices.hero;

    scenes.push({
      scene_index: sceneIndex,
      title: `Scene ${sceneIndex}: ${character}`,
      character: character,
      voice_type: vType,
      voice: voiceCfg.voice,
      pitch: voiceCfg.pitch,
      rate: voiceCfg.rate,
      dialogue: dialogue || `Scene ${sceneIndex} action moment!`,
      visual_prompt: `Pixar 3D animation style cute character ${character}, vibrant cinematic studio lighting, highly expressive 3D model, clean composition, 9:16 vertical ratio.`,
      target_duration: 9.5
    });
  }

  return {
    title: `Pixar 3D Animated Story (${durationKey})`,
    genre: 'Pixar 3D Animated Reel',
    tags: ['pixar', '3danimation', 'cartoon', 'shorts', 'reels', 'viral'],
    storyboard: scenes
  };
}

/**
 * Get a random shuffled storyboard from our library
 */
function getShuffledStoryboard(durationKey = '1min', language = 'hindi') {
  const keys = Object.keys(STORY_PRESETS);
  const randomKey = keys[Math.floor(Math.random() * keys.length)];
  return expandStoryPreset(randomKey, durationKey, language);
}

module.exports = {
  VOICE_PROFILES,
  STORY_PRESETS,
  expandStoryPreset,
  parseCustomScriptToStoryboard,
  getShuffledStoryboard
};
