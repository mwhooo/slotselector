import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const manifestPath = path.join(root, 'data', 'bgaming_711_catalog.json');
const namesPath = path.join(root, 'data', 'bgaming_slots.json');
const providersPath = path.join(root, 'data', 'slot_providers.json');
const imagesPath = path.join(root, 'public', 'images');
const providerName = 'BGaming';
const filenamePrefix = 'bgaming';

const normalize = (value) => value
  .toLowerCase()
  .replace(/&/g, 'and')
  .replace(/[^a-z0-9]+/g, ' ')
  .trim()
  .replace(/\s+/g, ' ');

const slugify = (value) => value
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/&/g, 'and')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
const providers = JSON.parse(await fs.readFile(providersPath, 'utf8'));
let existingNames = [];
try {
  existingNames = JSON.parse(await fs.readFile(namesPath, 'utf8'));
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}

const existingFiles = await fs.readdir(imagesPath);
const imageBySlug = new Map();
for (const filename of existingFiles) {
  const match = filename.match(/^bgaming-(.+)\.(?:jpe?g|png|webp|gif)$/i);
  if (match) imageBySlug.set(match[1], filename);
}

const resolvedGames = manifest.map((game) => {
  const slug = slugify(game.name);
  const extension = path.extname(new URL(game.imageUrl).pathname).toLowerCase();
  if (!['.jpg', '.jpeg', '.png', '.webp', '.gif'].includes(extension)) {
    throw new Error(`Unsupported image type for ${game.name}: ${extension}`);
  }

  return {
    ...game,
    filename: imageBySlug.get(slug) || `${filenamePrefix}-${slug}${extension}`,
  };
});

const downloads = resolvedGames.filter((game) => !existingFiles.includes(game.filename));
let nextDownload = 0;
await Promise.all(Array.from({ length: 6 }, async () => {
  while (nextDownload < downloads.length) {
    const game = downloads[nextDownload++];
    const response = await fetch(game.imageUrl, {
      headers: { 'User-Agent': 'SlotSelector catalog importer' },
    });
    if (!response.ok) {
      throw new Error(`Download failed (${response.status}) for ${game.name}`);
    }

    const image = Buffer.from(await response.arrayBuffer());
    if (!image.length) throw new Error(`Downloaded an empty image for ${game.name}`);
    await fs.writeFile(path.join(imagesPath, game.filename), image, { flag: 'wx' });
    console.log(`Downloaded ${game.name}`);
  }
}));

for (const [filename, provider] of Object.entries(providers)) {
  if (provider === providerName) delete providers[filename];
}
for (const game of resolvedGames) providers[game.filename] = providerName;

const namesByNormalizedTitle = new Map(
  existingNames.map((name) => [normalize(name), name])
);
for (const game of manifest) namesByNormalizedTitle.set(normalize(game.name), game.name);

await fs.writeFile(providersPath, `${JSON.stringify(providers, null, 2)}\n`);
await fs.writeFile(namesPath, `${JSON.stringify([...namesByNormalizedTitle.values()], null, 2)}\n`);

console.log(JSON.stringify({
  lobbyGames: manifest.length,
  downloadedImages: downloads.length,
  reusedImages: manifest.length - downloads.length,
  registeredProviderImages: resolvedGames.length,
  providerNames: namesByNormalizedTitle.size,
}, null, 2));
