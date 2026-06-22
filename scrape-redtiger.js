import fs from 'fs';
import https from 'https';
import http from 'http';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const IMAGES_DIR = path.join(__dirname, 'public', 'images');
if (!fs.existsSync(IMAGES_DIR)) {
  fs.mkdirSync(IMAGES_DIR, { recursive: true });
}

// Download file with retry logic
async function downloadFile(url, filepath, maxRetries = 2) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        
        const timeoutHandle = setTimeout(() => {
          reject(new Error('Timeout'));
        }, 15000);

        protocol.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
          clearTimeout(timeoutHandle);
          
          if (res.statusCode === 404) {
            reject(new Error('Not found'));
            return;
          }

          if (res.statusCode !== 200) {
            reject(new Error(`HTTP ${res.statusCode}`));
            return;
          }

          const file = fs.createWriteStream(filepath);
          res.pipe(file);

          file.on('finish', () => {
            file.close();
            resolve(true);
          });

          file.on('error', (err) => {
            clearTimeout(timeoutHandle);
            fs.unlink(filepath, () => {});
            reject(err);
          });
        }).on('error', reject);
      });
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
}

// Convert slot name to URL slug and game path
function nameToGamePath(name) {
  return name
    .toLowerCase()
    .replace(/\s+slot\s*$/i, '') // Remove " Slot" from end
    .replace(/\s+/g, '-')         // Replace spaces with dashes
    .replace(/[^a-z0-9-]/g, '')   // Remove special chars
    .replace(/-+/g, '-')          // Collapse multiple dashes
    .replace(/^-+|-+$/g, '');     // Trim dashes
}

// Fetch game page and extract image URL
async function getImageUrlFromGamePage(gamePath) {
  return new Promise((resolve) => {
    const url = `https://redtiger.com/games/${gamePath}`;
    
    const timeoutHandle = setTimeout(() => {
      resolve(null);
    }, 15000);

    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let html = '';
      
      res.on('data', chunk => {
        html += chunk;
        if (html.length > 5000000) { // Stop if too large
          res.destroy();
        }
      });
      
      res.on('end', () => {
        clearTimeout(timeoutHandle);
        
        // Look for image URLs with small_ or thumbnail_ patterns that contain icon or thumb
        const pattern = /https:\/\/fan-cdn\.nolimitcity\.com\/(small_|thumbnail_)[a-z0-9_-]*(icon|thumb)[a-z0-9_-]*\.(png|jpg|webp)/gi;
        const matches = html.match(pattern);
        
        if (matches && matches.length > 0) {
          resolve(matches[0]);
        } else {
          resolve(null);
        }
      });
    }).on('error', () => {
      clearTimeout(timeoutHandle);
      resolve(null);
    }).on('abort', () => {
      clearTimeout(timeoutHandle);
      resolve(null);
    });
  });
}

// Try to fetch game image
async function tryDownloadGameImage(gameName, gamePath) {
  // First try to get image URL from game page
  const imageUrl = await getImageUrlFromGamePage(gamePath);
  
  if (!imageUrl) {
    return { filename: null, failed: true };
  }

  const ext = imageUrl.includes('.webp') ? '.webp' : imageUrl.includes('.png') ? '.png' : '.jpg';
  const filename = `redtiger-${gamePath}${ext}`;
  const filepath = path.join(IMAGES_DIR, filename);

  // Check if image already exists
  if (fs.existsSync(filepath)) {
    return { filename, existed: true };
  }

  try {
    await downloadFile(imageUrl, filepath);
    return { filename, existed: false, success: true };
  } catch (error) {
    return { filename: null, failed: true };
  }
}

async function main() {
  console.log('Starting Red Tiger image download...\n');

  // Load redtiger_slots.json
  const slotsPath = path.join(__dirname, 'redtiger_slots.json');
  let games = [];

  if (fs.existsSync(slotsPath)) {
    const data = JSON.parse(fs.readFileSync(slotsPath, 'utf-8'));
    if (Array.isArray(data)) {
      games = data;
    } else if (typeof data === 'object') {
      // Handle object format {"name": "Red Tiger", ...}
      games = Object.keys(data).filter(name => name !== '#Wpcf7 F46013 O1');
    }
  } else {
    console.error('redtiger_slots.json not found');
    process.exit(1);
  }

  console.log(`Processing ${games.length} games...\n`);

  // Load existing slot_providers
  const providersPath = path.join(__dirname, 'slot_providers.json');
  let slotProviders = {};
  if (fs.existsSync(providersPath)) {
    slotProviders = JSON.parse(fs.readFileSync(providersPath, 'utf-8'));
  }

  let downloaded = 0;
  let existed = 0;
  let failed = 0;

  for (let i = 0; i < games.length; i++) {
    const game = games[i];
    const gamePath = nameToGamePath(game);
    
    process.stdout.write(`[${i + 1}/${games.length}] ${game.substring(0, 45).padEnd(45)}... `);

    try {
      const result = await tryDownloadGameImage(game, gamePath);
      
      if (result.existed) {
        console.log('✓');
        existed++;
      } else if (result.success) {
        console.log('✓');
        slotProviders[result.filename] = 'Red Tiger';
        downloaded++;
      } else {
        console.log('✗');
        failed++;
      }
    } catch (error) {
      console.log('✗');
      failed++;
    }

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  // Save updated slot_providers
  fs.writeFileSync(
    providersPath,
    JSON.stringify(slotProviders, null, 0),
    'utf-8'
  );

  console.log(`\n✅ Complete!`);
  console.log(`   Downloaded: ${downloaded}`);
  console.log(`   Already existed: ${existed}`);
  console.log(`   Failed: ${failed}`);
  console.log(`   Total slots: ${Object.keys(slotProviders).length}`);
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
