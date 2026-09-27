const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
require('dotenv').config();

const ffmpegPath = require('ffmpeg-static') || 'ffmpeg';

const DID_KEY = process.env.D_ID_API_KEY || 'Z29vZ2xlLW9hdXRoMnwxMDUwMDk2MTY1MTAzMzQ5NjU5OTRAYWtfWVRhY3kyLVJHVENmb2ZtSUpiUmQ1:rA85FCsqcBguu2bTyNcRi';
const authHeader = 'Basic ' + Buffer.from(DID_KEY).toString('base64');

async function uploadImage(filePath) {
  console.log(`[Upload] Uploading ${filePath} to D-ID...`);
  const fileBytes = fs.readFileSync(filePath);
  const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
  const fileName = path.basename(filePath);

  const header = Buffer.from(
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="image"; filename="${fileName}"\r\n` +
    `Content-Type: image/jpeg\r\n\r\n`
  );
  const footer = Buffer.from(`\r\n--${boundary}--\r\n`);
  const body = Buffer.concat([header, fileBytes, footer]);

  const res = await fetch('https://api.d-id.com/images', {
    method: 'POST',
    headers: {
      'Authorization': authHeader,
      'Content-Type': `multipart/form-data; boundary=${boundary}`
    },
    body
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(`Upload failed (${res.status}): ${JSON.stringify(data)}`);
  }
  console.log(`[Upload] S3 URL: ${data.url}`);
  return data.url;
}

async function createTalk(sourceUrl, text, voiceId) {
  console.log(`[Talk] Creating talk with voice ${voiceId}: "${text.substring(0, 35)}..."`);
  const payload = {
    source_url: sourceUrl,
    script: {
      type: 'text',
      subtitles: false,
      provider: {
        type: 'microsoft',
        voice_id: voiceId
      },
      input: text
    },
    config: {
      fluent: true,
      stitch: true,
      auto_match: true
    }
  };

  const res = await fetch('https://api.d-id.com/talks', {
    method: 'POST',
    headers: {
      'Authorization': authHeader,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(`Talk creation failed (${res.status}): ${JSON.stringify(data)}`);
  }
  console.log(`[Talk] Created talk ID: ${data.id}`);
  return data.id;
}

async function waitForTalk(talkId, outPath) {
  console.log(`[Wait] Waiting for talk ${talkId} to render (timeout: 10 mins)...`);
  const startTime = Date.now();
  let attempts = 0;
  while (Date.now() - startTime < 600000) {
    await new Promise(r => setTimeout(r, 5000));
    attempts++;
    const res = await fetch(`https://api.d-id.com/talks/${talkId}`, {
      headers: { 'Authorization': authHeader }
    });
    const data = await res.json();
    if (attempts % 3 === 0 || data.status === 'done') {
      console.log(`[Status] [${Math.round((Date.now() - startTime) / 1000)}s] Talk status: ${data.status}`);
    }
    
    if (data.status === 'done') {
      console.log(`[Download] Downloading result from ${data.result_url}...`);
      const vidRes = await fetch(data.result_url);
      const vidBuffer = Buffer.from(await vidRes.arrayBuffer());
      fs.writeFileSync(outPath, vidBuffer);
      console.log(`[Success] Saved video to ${outPath} (${vidBuffer.length} bytes)`);
      return outPath;
    }
    if (data.status === 'error' || data.status === 'rejected') {
      throw new Error(`Talk generation failed: ${JSON.stringify(data)}`);
    }
  }
  throw new Error(`Timed out waiting for talk ${talkId}`);
}

async function main() {
  const assetsDir = path.join(__dirname, '..', 'data', 'assets');
  const videosDir = path.join(__dirname, '..', 'data', 'videos');

  const characters = [
    {
      name: 'aloo',
      image: path.join(assetsDir, 'char_aloo.jpg'),
      voice: 'hi-IN-MadhurNeural',
      dialogue: 'गोभी जी, क्या आप मुझसे शादी करेंगी? मैं आपके लिए सब कुछ करूँगा!',
      output: path.join(videosDir, 'aloo_did_talking_live.mp4')
    },
    {
      name: 'tamatar',
      image: path.join(assetsDir, 'char_tamatar.jpg'),
      voice: 'hi-IN-MadhurNeural',
      dialogue: 'ओए गोलू आलू! साइड हट! गोभी तो सिर्फ मेरी बनेगी, देख मेरा लाल रंग और स्वैग!',
      output: path.join(videosDir, 'tamatar_did_talking_live.mp4')
    },
    {
      name: 'gobhi',
      image: path.join(assetsDir, 'char_gobhi.jpg'),
      voice: 'hi-IN-SwaraNeural',
      dialogue: 'हाय राम! तुम दोनों लड़ना बंद करो! मैं तो सिर्फ अपनी पसंद के मटर जी के साथ ही जाऊँगी!',
      output: path.join(videosDir, 'gobhi_did_talking_live.mp4')
    }
  ];

  for (const char of characters) {
    if (fs.existsSync(char.output) && fs.statSync(char.output).size > 100000) {
      console.log(`[Skip] ${char.name} video already exists at ${char.output} (${fs.statSync(char.output).size} bytes)`);
      continue;
    }
    console.log(`\n=== Processing Character: ${char.name.toUpperCase()} ===`);
    const s3Url = await uploadImage(char.image);
    const talkId = await createTalk(s3Url, char.dialogue, char.voice);
    await waitForTalk(talkId, char.output);
  }

  console.log('\n=== Merging All 3 Character Videos into Full Story ===');
  const alooVid = path.join(videosDir, 'aloo_did_talking_live.mp4');
  const tamatarVid = path.join(videosDir, 'tamatar_did_talking_live.mp4');
  const gobhiVid = path.join(videosDir, 'gobhi_did_talking_live.mp4');
  const finalVid = path.join(videosDir, 'final_aloo_tamatar_gobhi_story.mp4');

  if (!fs.existsSync(alooVid) || !fs.existsSync(tamatarVid) || !fs.existsSync(gobhiVid)) {
    throw new Error('One or more input clips are missing!');
  }

  // Concatenate directly via filter_complex
  console.log(`[FFmpeg] Concatenating clips via filter_complex into final vertical short (720x1280)...`);
  const filterCmd = `"${ffmpegPath}" -y ` +
    `-i "${alooVid}" ` +
    `-i "${tamatarVid}" ` +
    `-i "${gobhiVid}" ` +
    `-filter_complex "` +
    `[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];` +
    `[1:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];` +
    `[2:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v2];` +
    `[v0][0:a][v1][1:a][v2][2:a]concat=n=3:v=1:a=1[v][a]" ` +
    `-map "[v]" -map "[a]" -c:v libx264 -preset fast -crf 19 -c:a aac -b:a 192k -ar 44100 -movflags +faststart "${finalVid}"`;

  execSync(filterCmd, { stdio: 'inherit' });

  console.log(`\n🎉 SUCCESS: Final multi-character story video generated at: ${finalVid}`);
  console.log(`Final file size: ${fs.statSync(finalVid).size} bytes`);
}

main().catch(err => {
  console.error('Execution failed:', err);
  process.exit(1);
});
