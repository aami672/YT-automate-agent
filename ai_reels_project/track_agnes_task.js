const fs = require('fs');
const path = require('path');

const taskId = '15124c16b160';
const outputDir = path.join(__dirname, 'output');

async function trackTask() {
  console.log(`🎬 Tracking Agnes Video Task ${taskId}...`);
  let isCompleted = false;

  while (!isCompleted) {
    await new Promise(r => setTimeout(r, 6000));
    try {
      const res = await fetch(`http://localhost:8765/api/tasks/${taskId}`);
      const data = await res.json();
      const pct = Math.round((data.current_progress || 0) * 100);
      console.log(`[${data.status}] Step: ${data.current_step} | Progress: ${pct}% | Message: ${data.current_message}`);

      if (data.status === "completed") {
        isCompleted = true;
        console.log("\n=======================================================");
        console.log("🎉 SUCCESS! Video Generation with Reference Images Completed!");
        console.log("=======================================================");
        if (data.final_video_file && fs.existsSync(data.final_video_file)) {
          const dest = path.join(outputDir, "agnes_final_3d_reel.mp4");
          fs.copyFileSync(data.final_video_file, dest);
          console.log(`📁 Final Watermark-Free 3D Video saved to:\n${dest}`);
        }
      } else if (data.status === "failed") {
        isCompleted = true;
        console.error("❌ Task failed:", data.error_traceback || data.current_message);
      }
    } catch (e) {
      console.warn("Tracking polling error:", e.message);
    }
  }
}

trackTask();
