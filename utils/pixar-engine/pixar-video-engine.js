const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const { Logger } = require('../logger');
const {
  parseCustomScriptToStoryboard,
  getShuffledStoryboard,
  expandStoryPreset
} = require('./storyboard-templates');

const { AITextService } = require('../ai-text-service');

class PixarVideoEngine {
  constructor(options = {}) {
    this.logger = new Logger('PixarVideoEngine');
    this.options = options;
    const { CredentialManager } = require('../credential-manager');
    this.credentials = options.credentials || new CredentialManager().credentials || {};
    
    if (options.aiVideoGenerator) {
      this.aiVideoGenerator = options.aiVideoGenerator;
    } else {
      const { AIVideoGenerator } = require('../ai-video-generator');
      this.aiVideoGenerator = new AIVideoGenerator(this.credentials);
    }
  }

  getPythonPath() {
    // 1. Check if custom PYTHON_PATH set
    if (process.env.PYTHON_PATH) return process.env.PYTHON_PATH;

    // 2. Check scratch venv where edge-tts, numpy, PIL are installed
    const scratchVenvPython = 'C:\\Users\\Amar\'s PC\\.gemini\\antigravity\\scratch\\agnes-video-generator\\.venv\\Scripts\\python.exe';
    if (require('fs').existsSync(scratchVenvPython)) {
      return scratchVenvPython;
    }

    // 3. Fallback to system python
    return 'python';
  }

  async generateDynamicGeminiScript(durationPreset = '1min', language = 'hindi', customTopic = null) {
    try {
      this.logger.info('Invoking Gemini to write a fresh 3D Pixar screenplay (non-living things coming to life)...');
      const numScenes = durationPreset === '3min' ? 18 : durationPreset === '2min' ? 12 : 6;
      
      const themeIdeas = [
        'Stationery items inside a student school pencil box (Pencil, Eraser, Sharpener, Ruler)',
        'Midnight kitchen utensils having an epic cooking party (Chef Fork, Pepper Shaker, Red Spatula, Chef Knife)',
        'Smart gadgets on a computer desk dealing with 1% low battery emergency (Smartphone, Wireless Earbuds, Power Bank, Fast Cable)',
        'Bathroom toiletries planning a morning freshness mission (Toothbrush Hero, Toothpaste Tube, Soapy Soap, Shower Sponge)',
        'Bedroom toys and alarm clock organizing a wake-up heist (Alarm Clock, Fluffy Pillow, Night Lamp, Teddy Commander)',
        'Shoe rack footwear preparing for an epic marathon race (Running Sneaker, Sturdy Boot, Comfy Slipper, Dancing Sandal)',
        'Fridge snacks and drinks having a cool celebration (Apple Hero, Chilled Juice Bottle, Cheese Block, Ice Cream Cone)',
        'Toolbox tools fixing a broken toy car (Hammer Boss, Screwdriver Scout, Wrench Muscle, Measuring Tape)'
      ];
      const selectedTheme = customTopic || themeIdeas[Math.floor(Math.random() * themeIdeas.length)];

      const prompt = `You are a master 3D Pixar / Disney animation comedy writer for children.
Write a funny, high-energy ${numScenes}-scene screenplay about ordinary non-living objects that secretly come to life with distinct funny personalities when humans aren't looking!

Theme: ${selectedTheme}
Language: Natural spoken Hindi dialogue with English/Hinglish comic punchlines (e.g. "Arre yaar!", "Emergency alert!").
Tone: Playful, wholesome, funny, fast-paced, high cartoon energy suitable for kids and YouTube Shorts / Reels.

Return ONLY a valid JSON object matching this exact structure:
{
  "title": "Creative Story Title",
  "genre": "Pixar 3D Comedy Animation",
  "tags": ["pixar", "3danimation", "cartoon", "hindi", "shorts", "reels", "kids"],
  "scenes": [
    {
      "scene_index": 1,
      "character": "Character Name",
      "voice_type": "hero",
      "dialogue": "Funny Hindi dialogue line that this character speaks enthusiastically",
      "visual_prompt": "A high-quality 3D Pixar animation scene description with character appearance, expressions, lighting, 9:16 vertical orientation"
    }
  ]
}
Ensure there are exactly ${numScenes} scenes. The final scene must be an upbeat Outro & Call to Action (like and subscribe).`;

      const aiText = new AITextService(this.credentials);
      const rawResponse = await aiText.generateText(prompt, { temperature: 0.85 });
      
      let parsed = null;
      try {
        const jsonMatch = rawResponse.match(/```(?:json)?\s*([\s\S]*?)\s*```/) || [null, rawResponse];
        parsed = JSON.parse(jsonMatch[1] || rawResponse);
      } catch (e) {
        this.logger.warn(`JSON parse of Gemini script failed (${e.message}), using fallback story package`);
      }

      if (parsed && parsed.scenes && Array.isArray(parsed.scenes) && parsed.scenes.length >= 6) {
        const { VOICE_PROFILES } = require('./storyboard-templates');
        const voices = VOICE_PROFILES[language] || VOICE_PROFILES.hindi;
        
        const validatedStoryboard = parsed.scenes.map((s, idx) => {
          const vType = s.voice_type || (idx === parsed.scenes.length - 1 ? 'outro' : 'hero');
          const voiceCfg = voices[vType] || voices.hero;
          return {
            scene_index: idx + 1,
            title: `Scene ${idx + 1}: ${s.character || 'Character'}`,
            character: s.character || `Hero ${idx + 1}`,
            voice_type: vType,
            voice: voiceCfg.voice,
            pitch: voiceCfg.pitch,
            rate: voiceCfg.rate,
            dialogue: s.dialogue,
            visual_prompt: s.visual_prompt,
            target_duration: 9.5
          };
        });

        this.logger.info(`Gemini generated fresh 3D Pixar story: "${parsed.title}" (${validatedStoryboard.length} scenes)`);
        return {
          title: parsed.title,
          genre: parsed.genre || 'Pixar 3D Comedy Animation',
          tags: parsed.tags || ['pixar', '3danimation', 'cartoon', 'shorts'],
          storyboard: validatedStoryboard
        };
      }
    } catch (err) {
      this.logger.warn(`Gemini script generation encountered error: ${err.message}. Using default 3D story.`);
    }

    return null;
  }

  async generateAnimatedVideo(options = {}) {
    const {
      scriptText = null,
      presetKey = null,
      durationPreset = '1min', // '1min', '2min', '3min'
      language = 'hindi',
      outputFilePath = null,
      tempDir = null,
      jobId = null
    } = options;

    this.logger.info(`Starting Pixar 3D animated video generation (${durationPreset}, lang: ${language})...`);

    // 1. Build Storyboard
    let storyboardPackage;
    if (presetKey) {
      storyboardPackage = expandStoryPreset(presetKey, durationPreset, language);
    } else if (scriptText && scriptText.trim().length > 0) {
      storyboardPackage = parseCustomScriptToStoryboard(scriptText, durationPreset, language);
    } else {
      // Auto-generate fresh unique story with Gemini AI
      storyboardPackage = await this.generateDynamicGeminiScript(durationPreset, language);
      if (!storyboardPackage) {
        storyboardPackage = getShuffledStoryboard(durationPreset, language);
      }
    }

    const timestamp = Date.now();
    const resolvedTempDir = tempDir || path.join(__dirname, '..', '..', 'temp', `pixar_${timestamp}`);
    await fs.mkdir(resolvedTempDir, { recursive: true });

    const finalOutput = outputFilePath || path.join(__dirname, '..', '..', 'data', 'videos', `pixar_${timestamp}_60fps.mp4`);
    await fs.mkdir(path.dirname(finalOutput), { recursive: true });

    // 1.5 Generate 3D Pixar character visuals dynamically for each scene
    const imagesDir = path.join(resolvedTempDir, 'scene_images');
    await fs.mkdir(imagesDir, { recursive: true });

    for (let i = 0; i < storyboardPackage.storyboard.length; i++) {
      const scene = storyboardPackage.storyboard[i];
      const hasSpecificPreexistingClip = scene.clip_path && require('fs').existsSync(path.resolve(__dirname, '..', '..', scene.clip_path));
      const hasSpecificPreexistingImg = scene.image_path && require('fs').existsSync(path.resolve(__dirname, '..', '..', scene.image_path));
      
      // If the scene is from a new story or doesn't have an existing asset, generate it fresh
      if (!hasSpecificPreexistingClip && !hasSpecificPreexistingImg) {
        const sceneImgPath = path.join(imagesDir, `scene_${i}.jpg`);
        const charPrompt = scene.visual_prompt || `A high-quality 3D Pixar animation scene. ${scene.character}, ${scene.title}. Cute expressive facial features, vibrant cinema lighting, vertical 9:16 composition, 3D Disney Pixar render.`;
        
        try {
          this.logger.info(`[Image Generator] Generating 3D Pixar visual for Scene ${i + 1}/${storyboardPackage.storyboard.length} (${scene.character})...`);
          await this.aiVideoGenerator.generateImage(charPrompt, sceneImgPath);
          scene.image_path = sceneImgPath;
          scene.clip_path = null;
        } catch (imgErr) {
          this.logger.warn(`Failed to generate AI image for scene ${i + 1}: ${imgErr.message}`);
        }
      }
    }

    // 2. Prepare Config JSON
    const configPath = path.join(resolvedTempDir, 'render_config.json');
    const configData = {
      storyboard: storyboardPackage.storyboard,
      options: {
        duration_preset: durationPreset,
        fps: 60,
        resolution: [720, 1280],
        bgm_volume: 0.35,
        voice_volume: 1.05,
        sfx_volume: 0.90
      },
      output_path: finalOutput,
      temp_dir: resolvedTempDir
    };

    await fs.writeFile(configPath, JSON.stringify(configData, null, 2), 'utf8');

    // 3. Run Python Renderer
    const pythonExe = this.getPythonPath();
    const rendererPy = path.join(__dirname, 'pixar_renderer.py');

    this.logger.info(`Invoking Python renderer via ${pythonExe}...`);

    await new Promise((resolve, reject) => {
      const child = spawn(pythonExe, ['-u', rendererPy, '--config', configPath], {
        cwd: path.dirname(rendererPy),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
      });

      child.stdout.on('data', data => {
        const text = data.toString().trim();
        if (text) this.logger.info(`[Python Renderer] ${text}`);
      });

      child.stderr.on('data', data => {
        const text = data.toString().trim();
        if (text) this.logger.warn(`[Python Renderer] ${text}`);
      });

      child.on('close', code => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Python Pixar renderer process exited with code ${code}`));
        }
      });

      child.on('error', err => {
        reject(err);
      });
    });

    // 4. Persist Scene Assets, Thumbnail & SRT Captions
    const assetsDir = path.join(__dirname, '..', '..', 'data', 'assets');
    await fs.mkdir(assetsDir, { recursive: true });

    const thumbnailPath = path.join(assetsDir, `pixar_thumb_${timestamp}.jpg`);
    const firstFramePng = path.join(resolvedTempDir, 'scene_clips', 'frame_0.png');
    const firstCharImg = path.join(__dirname, '..', '..', 'assets', 'pixar-characters', 'pencil_hero.jpg');
    
    if (require('fs').existsSync(firstCharImg)) {
      await fs.copyFile(firstCharImg, thumbnailPath).catch(() => {});
    } else if (require('fs').existsSync(firstFramePng)) {
      await fs.copyFile(firstFramePng, thumbnailPath).catch(() => {});
    }

    const enrichedStoryboard = [];
    for (let i = 0; i < storyboardPackage.storyboard.length; i++) {
      const scene = { ...storyboardPackage.storyboard[i] };
      const sNum = i + 1;
      const sIdx = i;
      
      const candidateFrames = [
        path.join(resolvedTempDir, 'scene_clips', `frame_${sIdx}.png`),
        path.join(resolvedTempDir, `frame_scene_${sNum}.png`),
        scene.image_path ? path.resolve(__dirname, '..', '..', scene.image_path) : null
      ].filter(Boolean);

      const candidateClips = [
        path.join(resolvedTempDir, 'scene_clips', `scene_${sIdx}.mp4`),
        path.join(resolvedTempDir, `clip_scene_${sNum}.mp4`)
      ];

      const candidateAudios = [
        path.join(resolvedTempDir, 'audio_tracks', `scene_${sIdx}_padded.mp3`),
        path.join(resolvedTempDir, 'audio_tracks', `scene_${sIdx}_raw.mp3`),
        path.join(resolvedTempDir, `dialogue_scene_${sNum}.mp3`)
      ];

      const destFrame = path.join(assetsDir, `pixar_${timestamp}_scene_${sNum}.png`);
      const destClip = path.join(assetsDir, `pixar_${timestamp}_scene_${sNum}.mp4`);
      const destAudio = path.join(assetsDir, `pixar_${timestamp}_scene_${sNum}.mp3`);

      for (const cf of candidateFrames) {
        if (require('fs').existsSync(cf)) {
          await fs.copyFile(cf, destFrame).catch(() => {});
          scene.visual_path = destFrame;
          break;
        }
      }

      for (const cc of candidateClips) {
        if (require('fs').existsSync(cc)) {
          await fs.copyFile(cc, destClip).catch(() => {});
          scene.clip_path = destClip;
          break;
        }
      }

      for (const ca of candidateAudios) {
        if (require('fs').existsSync(ca)) {
          await fs.copyFile(ca, destAudio).catch(() => {});
          scene.audio_path = destAudio;
          break;
        }
      }

      enrichedStoryboard.push(scene);
    }

    const srtContent = this.generateSRT(enrichedStoryboard);
    const captionsPath = path.join(__dirname, '..', '..', 'data', 'captions', `pixar_captions_${timestamp}.srt`);
    await fs.mkdir(path.dirname(captionsPath), { recursive: true });
    await fs.writeFile(captionsPath, srtContent, 'utf8');

    this.logger.info(`Pixar 3D animated reel complete: ${finalOutput}`);

    return {
      success: true,
      videoPath: finalOutput,
      thumbnailPath: thumbnailPath,
      captionsPath: captionsPath,
      title: storyboardPackage.title,
      genre: storyboardPackage.genre,
      tags: storyboardPackage.tags,
      storyboard: enrichedStoryboard,
      fps: 60,
      resolution: '720x1280',
      durationPreset: durationPreset,
      duration: enrichedStoryboard.length * 9.5
    };
  }

  generateSRT(storyboard = []) {
    let srt = '';
    let currentTime = 0.0;

    const formatSRTTime = seconds => {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      const ms = Math.floor((seconds % 1) * 1000);
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${ms.toString().padStart(3, '0')}`;
    };

    storyboard.forEach((scene, index) => {
      const start = currentTime;
      const end = currentTime + (scene.target_duration || 9.5);
      srt += `${index + 1}\n`;
      srt += `${formatSRTTime(start)} --> ${formatSRTTime(end)}\n`;
      srt += `[${scene.character}] ${scene.dialogue}\n\n`;
      currentTime = end;
    });

    return srt;
  }
}

module.exports = { PixarVideoEngine };
