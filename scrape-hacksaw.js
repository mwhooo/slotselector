import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const workspace = __dirname;
const imagesDir = path.join(workspace, 'public/images');
const providersFile = path.join(workspace, 'slot_providers.json');
const hacksawFile = path.join(workspace, 'hacksaw_slots.json');

// Load Hacksaw games
const hacksawGames = JSON.parse(fs.readFileSync(hacksawFile, 'utf-8'));

// Convert game name to URL slug
function nameToGameSlug(name) {
  return name
    .toLowerCase()
    .replace(/\s+/g, '-')        // spaces to hyphens
    .replace(/&/g, 'and')         // & to 'and'
    .replace(/[^a-z0-9-]/g, '')   // remove special chars
    .replace(/-+/g, '-')          // collapse multiple hyphens
    .replace(/^-+|-+$/g, '');     // trim hyphens
}

// Download file with retry logic
function downloadFile(url, destPath, retries = 3) {
  return new Promise((resolve) => {
    const attemptDownload = (attempt) => {
      const file = fs.createWriteStream(destPath);
      const timeout = setTimeout(() => {
        file.destroy();
        fs.unlink(destPath, () => {});
        if (attempt < retries) {
          setTimeout(() => attemptDownload(attempt + 1), 1000);
        } else {
          resolve(false);
        }
      }, 15000);

      https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (response) => {
        if (response.statusCode !== 200) {
          file.destroy();
          fs.unlink(destPath, () => {});
          clearTimeout(timeout);
          if (attempt < retries) {
            setTimeout(() => attemptDownload(attempt + 1), 1000);
          } else {
            resolve(false);
          }
          return;
        }

        response.pipe(file);
        file.on('finish', () => {
          file.close();
          clearTimeout(timeout);
          resolve(true);
        });
        file.on('error', () => {
          fs.unlink(destPath, () => {});
          clearTimeout(timeout);
          if (attempt < retries) {
            setTimeout(() => attemptDownload(attempt + 1), 1000);
          } else {
            resolve(false);
          }
        });
      }).on('error', () => {
        clearTimeout(timeout);
        if (attempt < retries) {
          setTimeout(() => attemptDownload(attempt + 1), 1000);
        } else {
          resolve(false);
        }
      });
    };

    attemptDownload(0);
  });
}

// Main download function
async function downloadHacksawImages() {
  // Load existing providers
  const providers = JSON.parse(fs.readFileSync(providersFile, 'utf-8'));

  // Extract game names and filter valid ones
  const games = Object.keys(hacksawGames)
    .filter(key => !key.startsWith('#')) // Skip invalid entries
    .map(key => key.replace(/ Slot$/, '')); // Remove " Slot" suffix

  console.log(`Processing ${games.length} games...`);

  let downloaded = 0;
  let failed = 0;

  for (let i = 0; i < games.length; i++) {
    const gameName = games[i];
    const slug = nameToGameSlug(gameName);
    const imageUrl = `https://cdn.hacksawgaming.com/games/${slug}.png`;
    
    // Generate filename
    const filename = `hacksaw-${slug}.png`;
    const filepath = path.join(imagesDir, filename);

    // Skip if already exists
    if (fs.existsSync(filepath)) {
      console.log(`[${i + 1}/${games.length}] ${gameName} (exists)`);
      continue;
    }

    // Try to download
    const success = await downloadFile(imageUrl, filepath);
    
    if (success) {
      console.log(`[${i + 1}/${games.length}] ${gameName} ... ✓`);
      providers[filename] = 'Hacksaw Gaming';
      downloaded++;
    } else {
      console.log(`[${i + 1}/${games.length}] ${gameName} ... ✗`);
      failed++;
    }
  }

  // Save updated providers
  fs.writeFileSync(providersFile, JSON.stringify(providers, null, 2));

  console.log('\n✅ Complete!');
  console.log(`   Downloaded: ${downloaded}`);
  console.log(`   Failed: ${failed}`);
  console.log(`   Total slots: ${Object.keys(providers).length}`);
}

downloadHacksawImages().catch(console.error);
