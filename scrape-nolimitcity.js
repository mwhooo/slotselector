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

// Common image URL patterns for NoLimit City games
const IMAGE_SOURCES = [
  (slug) => `https://fan-cdn.nolimitcity.com/${slug}_thumb.webp`,
  (slug) => `https://fan-cdn.nolimitcity.com/${slug}.webp`,
  (slug) => `https://fan-cdn.nolimitcity.com/${slug}_thumbnail.png`,
  (slug) => `https://fan-cdn.nolimitcity.com/${slug}.png`,
  (slug) => `https://fan-cdn.nolimitcity.com/${slug}.jpg`,
];

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

// Try to fetch game images from NoLimit City CDN
async function tryDownloadGameImage(slug) {
  for (const getUrl of IMAGE_SOURCES) {
    const url = getUrl(slug);
    const ext = url.includes('.webp') ? '.webp' : url.includes('.png') ? '.png' : '.jpg';
    const filename = `nolimitcity-${slug}${ext}`;
    const filepath = path.join(IMAGES_DIR, filename);

    // Check if image already exists
    if (fs.existsSync(filepath)) {
      return { filename, existed: true };
    }

    try {
      await downloadFile(url, filepath);
      return { filename, existed: false, success: true };
    } catch (error) {
      // Try next URL pattern
    }
  }
  return { filename: null, failed: true };
}

async function main() {
  console.log('Starting NoLimit City image download...\n');

  // Load the nolimitcity_slots.json
  const slotsPath = path.join(__dirname, 'nolimitcity_slots.json');
  let games = [];

  if (fs.existsSync(slotsPath)) {
    games = JSON.parse(fs.readFileSync(slotsPath, 'utf-8'));
  } else {
    console.error('nolimitcity_slots.json not found. Please run the updater first.');
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
    const slug = game.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    
    process.stdout.write(`[${i + 1}/${games.length}] ${game}... `);

    try {
      const result = await tryDownloadGameImage(slug);
      
      if (result.existed) {
        console.log('✓ (already have)');
        existed++;
      } else if (result.success) {
        console.log('✓ (downloaded)');
        slotProviders[result.filename] = 'NoLimit City';
        downloaded++;
      } else {
        console.log('✗ (not found)');
        failed++;
      }
    } catch (error) {
      console.log(`✗ (error: ${error.message})`);
      failed++;
    }

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 300));
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
