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
        voice: 'hi-IN-MadhurNeural',
        pitch: '+18Hz',
        rate: '+8%',
        dialogue: 'सोमवार की सुबह हो गई दोस्तों! पेंसिल भाई एकदम तैयार हैं, आज तो क्लास में पूरे दस में से दस मार्क्स लेकर ही मानेंगे!',
        image_path: 'assets/pixar-characters/pencil_hero.jpg',
        clip_path: 'assets/pixar-clips/scene_0.mp4',
        visual_prompt: 'A high-quality 3D Pixar Disney animation scene. A cheerful yellow wooden pencil character with big expressive cartoon eyes and a warm smile on the pencil body standing proudly on a student notebook on a wooden classroom desk. Bright morning sunlight, soft classroom background. Important: NO tail, NO animal legs, pure classic stationery pencil character, steady locked camera, zero jitter, perfectly proportioned vertical 9:16 framing.'
      },
      {
        scene_index: 2,
        title: 'Panicky Eraser Joins',
        character: 'Panicky Eraser',
        voice_type: 'squeaky',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+32Hz',
        rate: '+5%',
        dialogue: 'अरे पेंसिल भाई धीरे लिखो! तुम गलतियां करोगे और मुझे घिसना पड़ेगा, मेरी तो कमर टूट जाएगी!',
        image_path: 'assets/pixar-characters/eraser_panicking.jpg',
        clip_path: 'assets/pixar-clips/scene_1.mp4',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A cute chunky pink eraser character with comical worried wide eyes and hands on its cheeks, trembling playfully on the wooden desk beside an open notebook. Classroom setting with warm morning light, steady camera, rich tactile rubber textures, perfectly proportioned vertical 9:16 framing.'
      },
      {
        scene_index: 3,
        title: 'Sharpener Power Up',
        character: 'Sharpener Tech',
        voice_type: 'fast_tech',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+18Hz',
        rate: '+10%',
        dialogue: 'चिंता मत करो इरेज़र बाबू! जब तक शार्पनर यहाँ है, पेंसिल की नोक रॉकेट की तरह शार्प रहेगी, लिखाई एकदम मक्खन!',
        image_path: 'assets/pixar-characters/sharpener_tech.jpg',
        clip_path: 'assets/pixar-clips/scene_2.mp4',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A cute friendly blue plastic pencil sharpener character with big expressive cartoon eyes standing proudly upright on an open notebook on a wooden school desk. Sharp blade visible, bright morning sunlight, locked steady camera, perfectly proportioned vertical 9:16 framing, zero distortion, zero stretching.'
      },
      {
        scene_index: 4,
        title: 'Ruler Superhero Steps In',
        character: 'Ruler Superhero',
        voice_type: 'deep_hero',
        voice: 'hi-IN-MadhurNeural',
        pitch: '-22Hz',
        rate: '-8%',
        dialogue: 'शांत हो जाओ सब! जब तक स्केल साहब यहाँ हैं, एक भी लाइन टेढ़ी नहीं होगी, हर डायग्राम बिल्कुल सीधा और परफेक्ट!',
        image_path: 'assets/pixar-characters/ruler_superhero.jpg',
        clip_path: 'assets/pixar-clips/scene_3.mp4',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A tall sleek clear plastic ruler character standing proudly like a superhero with hands on hips on an open math notebook on the wooden classroom desk. Bright morning sunlight, clear transparent reflections, proud confident expression, locked steady framing, pure 3D character, perfectly proportioned 9:16 vertical.'
      },
      {
        scene_index: 5,
        title: 'Squad Action Formation',
        character: 'Backpack Squad',
        voice_type: 'action',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+14Hz',
        rate: '+6%',
        dialogue: 'देखा इसे कहते हैं बैकपैक स्क्वाड! लिखना, मिटाना, शार्प करना और सीधी लाइन - सब मिलकर करेंगे टॉप!',
        image_path: 'assets/pixar-characters/squad_vertical.jpg',
        clip_path: 'assets/pixar-clips/scene_4.mp4',
        visual_prompt: 'A high-quality 3D Pixar Disney animation scene. The entire stationery squad - yellow pencil, pink eraser, blue sharpener, and clear ruler grouped closely in the center of an open notebook on the wooden school desk. Warm morning sunlight, chalkboard in background, locked steady camera, perfectly proportioned vertical 9:16 framing, zero stretching, no humans.'
      },
      {
        scene_index: 6,
        title: 'School Bell Outro & CTA',
        character: 'Hero Outro',
        voice_type: 'outro',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+20Hz',
        rate: '+8%',
        dialogue: 'स्कूल की घंटी बज चुकी है दोस्तों! आपका सबसे पसंदीदा स्टेशनरी साथी कौन सा है? कमेंट में बताओ और सब्सक्राइब जरूर करो!',
        image_path: 'assets/pixar-characters/outro_vertical.jpg',
        clip_path: 'assets/pixar-clips/scene_5.mp4',
        visual_prompt: 'A high-quality 3D Pixar animation scene. Celebratory finale of the cute stationery squad (yellow pencil, pink eraser, blue sharpener, clear ruler) waving happily together with joyful big smiles on the wooden school desk next to a colorful pencil box. Festive morning sunlight, sparkling confetti bokeh, locked steady camera, perfectly proportioned vertical 9:16 framing, zero stretching, no humans.'
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
        voice: 'hi-IN-MadhurNeural',
        pitch: '+18Hz',
        rate: '+8%',
        dialogue: 'Suno sabhi utensils! Fridge ka door band ho chuka hai, kitchen lights off hain. Tonight is Operation Golden Toast!',
        image_path: 'assets/pixar-characters/kitchen/chef_fork.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation character. A cute friendly shiny silver fork character wearing a tiny white cartoon chef hat with big expressive eyes and a warm smile, standing proudly on a clean marble kitchen counter, soft moonlight beam shining through window, 3D Pixar cartoon render, vertical 9:16'
      },
      {
        scene_index: 2,
        title: 'Nervous Pepper Shaker',
        character: 'Pepper Shaker',
        voice_type: 'squeaky',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+32Hz',
        rate: '+5%',
        dialogue: 'Lekin Chef! Agar kisine sneeze kar diya toh microwave ka alarm baj jayega! Hum sab Pakde jayenge!',
        image_path: 'assets/pixar-characters/kitchen/pepper_shaker.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation character. A cute transparent glass pepper shaker character shivering and trembling with wide comical nervous cartoon eyes, black pepper dust sparkling in moonlight, standing on marble kitchen counter, 3D Pixar cartoon render, vertical 9:16'
      },
      {
        scene_index: 3,
        title: 'Spatula Speed Flips',
        character: 'Spatula Master',
        voice_type: 'fast_tech',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+18Hz',
        rate: '+10%',
        dialogue: 'Chill karo dosto! Meri 360-degree flip technique ke aage koi toast bach nahi sakta! Butter ready, pan hot!',
        image_path: 'assets/pixar-characters/kitchen/spatula_master.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation character. A vibrant red silicone spatula character with cute acrobatic eyes performing a dynamic mid-air flip over a frying pan on a modern kitchen stove, warm glowing kitchen lights, 3D Pixar cartoon render, vertical 9:16'
      },
      {
        scene_index: 4,
        title: 'Heavyweight Chef Knife',
        character: 'Chef Knife',
        voice_type: 'deep_hero',
        voice: 'hi-IN-MadhurNeural',
        pitch: '-22Hz',
        rate: '-8%',
        dialogue: 'Rasta saaf hai. Mai hu Knife commander. Clean cut, zero noise. Toast buttering begins now!',
        image_path: 'assets/pixar-characters/kitchen/chef_knife.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation character. A sturdy polished steel chef knife character with a friendly confident hero expression, standing proudly guarding a wooden cutting board on a clean kitchen counter, soft moonlight and kitchen ambient light, 3D Pixar cartoon render, vertical 9:16'
      },
      {
        scene_index: 5,
        title: 'Golden Toast Victory',
        character: 'Kitchen Squad',
        voice_type: 'action',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+14Hz',
        rate: '+6%',
        dialogue: 'Mission accomplished! Crunchy, golden, and delicious! Hamari kitchen squad kabhi haar nahi manti!',
        image_path: 'assets/pixar-characters/kitchen/kitchen_squad.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation scene. The cute kitchen utensils squad (fork with chef hat, shivering pepper shaker, red spatula, and chef knife) celebrating together around a golden crispy buttery toast on a marble kitchen counter, sparkling fairy bokeh sparks, festive kitchen mood, 3D Pixar render, vertical 9:16'
      },
      {
        scene_index: 6,
        title: 'Kitchen Outro & CTA',
        character: 'Chef Fork',
        voice_type: 'outro',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+20Hz',
        rate: '+8%',
        dialogue: 'Aisi aur mazedaar kitchen stories dekhne ke liye video ko Like karo aur channel Subscribe karna mat bhoolna!',
        image_path: 'assets/pixar-characters/kitchen/kitchen_outro.jpg',
        visual_prompt: 'A high-quality 3D Pixar Disney animation scene. The cute fork character with chef hat waving happily at the camera with a thumbs up badge, golden glowing like and subscribe icons floating in the cozy kitchen air with sparkling confetti bokeh, 3D Pixar render, vertical 9:16'
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
        voice: 'hi-IN-MadhurNeural',
        pitch: '+18Hz',
        rate: '+8%',
        dialogue: 'Emergency alert! Battery sirf 1 percent bachi hai aur screen dim ho rahi hai! Mujhe turant power chahiye!',
        image_path: 'assets/pixar-characters/tech/smartphone_boss.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A sleek friendly cute smartphone character with big expressive cartoon eyes looking anxious with a glowing red low battery 1% icon on its shiny glass screen, sweating comical cartoon drops, standing on a modern wooden desk, vibrant dramatic lighting, 3D Pixar cartoon render, vertical 9:16'
      },
      {
        scene_index: 2,
        title: 'Nervous Earbuds Shiver',
        character: 'Wireless Earbuds',
        voice_type: 'squeaky',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+32Hz',
        rate: '+5%',
        dialogue: 'Oh no! Agar phone switch off ho gaya toh humara party playlist band ho jayega! Hum bekar ho jayenge!',
        image_path: 'assets/pixar-characters/tech/wireless_earbuds.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. Twin cute white glossy wireless earbuds characters hopping and shivering with comical wide worried cartoon eyes, musical notes floating in air, sitting on a modern wooden desk, vibrant colorful ambient lighting, 3D Pixar render, vertical 9:16'
      },
      {
        scene_index: 3,
        title: 'Power Bank Heavyweight Hero',
        character: 'Power Bank',
        voice_type: 'deep_hero',
        voice: 'hi-IN-MadhurNeural',
        pitch: '-22Hz',
        rate: '-8%',
        dialogue: 'Ghabrao mat! 20000 mAh ka powerhouse mai hu! Rapid charge delivery shuru karta hu!',
        image_path: 'assets/pixar-characters/tech/power_bank.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A heavyweight matte black power bank character with muscular cartoon arms flexing heroically, smiling confident eyes, glowing green battery LED bars illuminated on body, standing proudly on a wooden desk, dramatic heroic studio lighting, 3D Pixar render, vertical 9:16'
      },
      {
        scene_index: 4,
        title: 'Turbo Cable Speed Connection',
        character: 'Turbo Cable',
        voice_type: 'fast_tech',
        voice: 'hi-IN-SwaraNeural',
        pitch: '+18Hz',
        rate: '+10%',
        dialogue: 'Braided Type-C cable active! High-speed 65W fast charging in 3, 2, 1... Connected!',
        image_path: 'assets/pixar-characters/tech/turbo_cable.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. A cute super-speed neon blue braided Type-C USB charging cable character with expressive anime cartoon eyes zooming across a wooden desk with glowing electric blue lightning spark particles, connecting heroically, 3D Pixar render, vertical 9:16'
      },
      {
        scene_index: 5,
        title: '100% Supercharged Party',
        character: 'Gadget Squad',
        voice_type: 'action',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+14Hz',
        rate: '+6%',
        dialogue: '100 percent supercharged! Lights, music, gaming mode activated! Squad is back in full power!',
        image_path: 'assets/pixar-characters/tech/gadget_squad.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. The entire smart gadget squad grouped together on a wooden desk: the smartphone radiating colorful neon lights at 100 percent battery, twin white wireless earbuds dancing happily, the muscular black power bank smiling with full green LEDs, and the glowing blue turbo cable celebrating together, vibrant studio party lights, festive bokeh sparks, 3D Pixar render, vertical 9:16'
      },
      {
        scene_index: 6,
        title: 'Tech Outro & CTA',
        character: 'Smartphone Boss',
        voice_type: 'outro',
        voice: 'hi-IN-MadhurNeural',
        pitch: '+20Hz',
        rate: '+8%',
        dialogue: 'Video pasand aayi toh jaldi se Like aur Subscribe ka button dabao aur apna phone model comment karo!',
        image_path: 'assets/pixar-characters/tech/tech_outro.jpg',
        visual_prompt: 'A high-quality 3D Pixar animation scene. Celebratory finale of the cute smartphone character smiling warmly and waving at the camera taking a selfie with its gadget friends, golden glowing like and subscribe icons floating in air with colorful festive confetti bokeh, 3D Pixar render, vertical 9:16'
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
        voice: s.voice || voices[s.voice_type]?.voice || voices.hero.voice,
        pitch: s.pitch || voices[s.voice_type]?.pitch || '+18Hz',
        rate: s.rate || voices[s.voice_type]?.rate || '+8%',
        image_path: s.image_path || '',
        clip_path: s.clip_path || '',
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
      voice: base.voice || voices[base.voice_type]?.voice || voices.hero.voice,
      pitch: base.pitch || voices[base.voice_type]?.pitch || '+18Hz',
      rate: base.rate || voices[base.voice_type]?.rate || '+8%',
      image_path: base.image_path || '',
      clip_path: base.clip_path || '',
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
