const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const mediaDir = path.join(__dirname, 'media');
if (!fs.existsSync(mediaDir)) {
  console.log('❌ Media folder nahi mila!');
  process.exit(1);
}

const items = fs.readdirSync(mediaDir);
let fixedCount = 0;

console.log('🔍 Purani videos check kar rahe hain...\n');

items.forEach(item => {
  const itemPath = path.join(mediaDir, item);
  
  // Agar yeh folder hai (jaise vid_123)
  if (fs.statSync(itemPath).isDirectory()) {
    const m3u8Path = path.join(itemPath, 'index.m3u8');
    const mp4Path = path.join(mediaDir, item + '.mp4');

    // Agar HLS file hai par MP4 nahi hai
    if (fs.existsSync(m3u8Path) && !fs.existsSync(mp4Path)) {
      console.log(`⏳ Repairing: ${item} (Please wait...)`);
      try {
        // HLS ko MP4 mein convert karo bina quality kharab kiye (-c copy)
        execSync(`ffmpeg -y -i "${m3u8Path}" -c copy -movflags +faststart "${mp4Path}"`, { stdio: 'ignore' });
        console.log(`✅ Fixed: ${item}.mp4`);
        fixedCount++;
      } catch (e) {
        console.log(`❌ Failed to repair: ${item}`);
      }
    }
  }
});

console.log(`\n🎉 Kaam khatam! Total ${fixedCount} purani videos repair ho gayi hain.`);
