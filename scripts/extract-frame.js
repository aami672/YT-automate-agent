const { execSync } = require('child_process');
const ffmpeg = require('ffmpeg-static');
const path = require('path');
const fs = require('fs');

const vid = path.join(__dirname, '..', 'data', 'videos', 'aloo_did_talking_live.mp4');
const out = path.join(__dirname, '..', 'data', 'videos', 'sample_aloo_frame.jpg');

const cmd = `"${ffmpeg}" -y -ss 00:00:02 -i "${vid}" -vframes 1 "${out}"`;
execSync(cmd, { stdio: 'inherit' });
console.log('Sample frame extracted:', out, 'size:', fs.statSync(out).size);
