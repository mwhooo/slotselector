import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = path.join(root, 'data', 'hacksaw_711_catalog.json');
const namesPath = path.join(root, 'data', 'hacksaw_slots.json');
const providersPath = path.join(root, 'data', 'slot_providers.json');
const rtpPath = path.join(root, 'data', 'slot_rtp.json');
const imagesPath = path.join(root, 'public', 'images');
const providerName = 'Hacksaw Gaming';
const filenamePrefix = 'hacksaw';

const slugify = (value) => value
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/&/g, 'and')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
const providers = JSON.parse(await fs.readFile(providersPath, 'utf8'));
const rtpData = JSON.parse(await fs.readFile(rtpPath, 'utf8'));
const resolvedGames = manifest.map((game) => {
  if (!game.name || !game.imageUrl) {
    throw new Error('Every Hacksaw row must have a name and thumbnail URL');
  }

  const imageUrl = new URL(game.imageUrl);
  const extension = path.extname(imageUrl.pathname).toLowerCase();
  if (imageUrl.protocol !== 'https:' || !['.jpg', '.jpeg', '.png', '.webp', '.gif'].includes(extension)) {
    throw new Error(`Unsupported image URL for ${game.name}: ${game.imageUrl}`);
  }

  if (['minBet', 'maxBet', 'rtp'].some((key) => game[key] !== null && !Number.isFinite(game[key]))) {
    throw new Error(`Invalid metadata for ${game.name}`);
  }

  return {
    ...game,
    filename: `${filenamePrefix}-${slugify(game.name)}${extension}`,
  };
});

const filenames = new Set();
for (const game of resolvedGames) {
  const extension = path.extname(game.filename);
  const filenameBase = path.basename(game.filename, extension);
  let filename = game.filename;
  let suffix = 2;
  while (filenames.has(filename)) filename = `${filenameBase}-${suffix++}${extension}`;
  filenames.add(filename);
  game.filename = filename;
}

let nextDownload = 0;
await Promise.all(Array.from({ length: 8 }, async () => {
  while (nextDownload < resolvedGames.length) {
    const game = resolvedGames[nextDownload++];
    const response = await fetch(game.imageUrl, {
      headers: { 'User-Agent': 'SlotSelector catalog importer' },
    });
    if (!response.ok) {
      throw new Error(`Download failed (${response.status}) for ${game.name}`);
    }

    const image = Buffer.from(await response.arrayBuffer());
    if (!image.length) throw new Error(`Downloaded an empty image for ${game.name}`);
    await fs.writeFile(path.join(imagesPath, game.filename), image);
  }
}));

for (const [filename, provider] of Object.entries(providers)) {
  if (provider === providerName) delete providers[filename];
}
for (const game of resolvedGames) providers[game.filename] = providerName;

rtpData[providerName] = Object.fromEntries(
  manifest.filter(({ rtp }) => Number.isFinite(rtp)).map(({ name, rtp }) => [name, rtp])
);

await fs.writeFile(providersPath, `${JSON.stringify(providers, null, 2)}\n`);
await fs.writeFile(namesPath, `${JSON.stringify(manifest.map(({ name }) => name), null, 2)}\n`);
await fs.writeFile(rtpPath, `${JSON.stringify(rtpData, null, 2)}\n`);

console.log(JSON.stringify({
  lobbyGames: manifest.length,
  refreshedImages: resolvedGames.length,
  registeredProviderImages: resolvedGames.length,
  rtpEntries: Object.keys(rtpData[providerName]).length,
}, null, 2));