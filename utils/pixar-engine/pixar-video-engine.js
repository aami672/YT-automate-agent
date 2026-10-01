const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const { Logger } = require('../logger');
const {
  parseCustomScriptToStoryboard,
  getShuffledStoryboard,
  expandStoryPreset
} = require('./storyboard-templates');

class PixarVideoEngine {
  constructor(options = {}) {
    this.logger = new Logger('PixarVideoEngine');
    this.options = options;
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
      storyboardPackage = getShuffledStoryboard(durationPreset, language);
    }

    const timestamp = Date.now();
    const resolvedTempDir = tempDir || path.join(__dirname, '..', '..', 'temp', `pixar_${timestamp}`);
    await fs.mkdir(resolvedTempDir, { recursive: true });

    const finalOutput = outputFilePath || path.join(__dirname, '..', '..', 'data', 'videos', `pixar_${timestamp}_60fps.mp4`);
    await fs.mkdir(path.dirname(finalOutput), { recursive: true });

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

    // 4. Generate Thumbnail & SRT Captions
    const thumbnailPath = path.join(__dirname, '..', '..', 'data', 'assets', `pixar_thumb_${timestamp}.jpg`);
    const firstFramePng = path.join(resolvedTempDir, 'frame_scene_1.png');
    if (require('fs').existsSync(firstFramePng)) {
      await fs.copyFile(firstFramePng, thumbnailPath);
    }

    const srtContent = this.generateSRT(storyboardPackage.storyboard);
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
      storyboard: storyboardPackage.storyboard,
      fps: 60,
      resolution: '720x1280',
      durationPreset: durationPreset,
      duration: storyboardPackage.storyboard.length * 9.5
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
