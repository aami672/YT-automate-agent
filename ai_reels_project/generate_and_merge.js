const { execFile, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ffmpegBinary = require('ffmpeg-static');

const assetsDir = path.join(__dirname, 'assets');
const outputDir = path.join(__dirname, 'output');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const scenes = [
  {
    id: 1,
    image: path.join(assetsDir, 'scene1.jpg'),
    duration: 6,
    filter: "zoompan=z='min(zoom+0.0015,1.2)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25",
    output: path.join(outputDir, 'scene1_animated.mp4')
  },
  {
    id: 2,
    image: path.join(assetsDir, 'scene2.jpg'),
    duration: 6,
    filter: "zoompan=z='min(max(zoom,pzoom)-0.0015,1.2)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25",
    output: path.join(outputDir, 'scene2_animated.mp4')
  },
  {
    id: 3,
    image: path.join(assetsDir, 'scene3.jpg'),
    duration: 6,
    filter: "zoompan=z='min(zoom+0.0012,1.15)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25",
    output: path.join(outputDir, 'scene3_animated.mp4')
  },
  {
    id: 4,
    image: path.join(assetsDir, 'scene4.jpg'),
    duration: 6,
    filter: "zoompan=z='min(zoom+0.0018,1.25)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25",
    output: path.join(outputDir, 'scene4_animated.mp4')
  }
];

function generateSceneVideo(scene) {
  return new Promise((resolve, reject) => {
    console.log(`🎬 Rendering Scene ${scene.id} video clip (${scene.duration}s)...`);
    const args = [
      '-y',
      '-loop', '1',
      '-i', scene.image,
      '-vf', scene.filter,
      '-t', scene.duration.toString(),
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-r', '25',
      scene.output
    ];

    execFile(ffmpegBinary, args, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ Failed to render Scene ${scene.id}:`, error);
        return reject(error);
      }
      console.log(`✅ Scene ${scene.id} clip generated: ${scene.output}`);
      resolve(scene.output);
    });
  });
}

async function mergeAllScenes(sceneVideoPaths) {
  console.log('🔄 Step 2: Merging all scene clips into a single video...');

  const concatListPath = path.join(outputDir, 'concat_list.txt');
  // Use relative filenames to avoid single-quote/space path escape issues
  const fileContent = sceneVideoPaths.map(p => `file '${path.basename(p)}'`).join('\n');
  fs.writeFileSync(concatListPath, fileContent);

  const finalVideoPath = path.join(outputDir, 'final_merged_reel.mp4');

  const args = [
    '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', 'concat_list.txt',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    'final_merged_reel.mp4'
  ];

  return new Promise((resolve, reject) => {
    execFile(ffmpegBinary, args, { cwd: outputDir }, (error, stdout, stderr) => {
      if (error) {
        console.error('❌ Merge failed:', error);
        return reject(error);
      }
      console.log(`🎉 SUCCESS! Single final video created at:\n${finalVideoPath}`);
      resolve(finalVideoPath);
    });
  });
}

async function runPipeline() {
  try {
    console.log('🚀 Starting Full Automated Video Generation & Merge Pipeline...');
    
    // Step 1: Render individual scene video clips
    const sceneOutputs = [];
    for (const scene of scenes) {
      const sceneVideo = await generateSceneVideo(scene);
      sceneOutputs.push(sceneVideo);
    }

    // Step 2: Merge into single final video
    const finalVideo = await mergeAllScenes(sceneOutputs);

    console.log('\n=============================================');
    console.log('✨ All scenes exported and merged successfully!');
    console.log('📁 Final Output:', finalVideo);
    console.log('=============================================\n');
  } catch (err) {
    console.error('💥 Pipeline error:', err);
  }
}

runPipeline();
