import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = path.join(root, 'data', 'endorphina_711_catalog.json');
const namesPath = path.join(root, 'data', 'endorphina_slots.json');
const providersPath = path.join(root, 'data', 'slot_providers.json');
const rtpPath = path.join(root, 'data', 'slot_rtp.json');
const imagesPath = path.join(root, 'public', 'images');
const providerName = 'Endorphina';
const filenamePrefix = 'endorphina';

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
  const slug = slugify(game.name);
  const extension = path.extname(new URL(game.imageUrl).pathname).toLowerCase();
  if (!['.jpg', '.jpeg', '.png', '.webp', '.gif'].includes(extension)) {
    throw new Error(`Unsupported image type for ${game.name}: ${extension}`);
  }

  const hasBetLimits = Number.isFinite(game.minBet) && Number.isFinite(game.maxBet);
  const hasRtp = Number.isFinite(game.rtp);
  const allMetadataUnknown = game.minBet === null && game.maxBet === null && game.rtp === null;
  if (!(hasBetLimits && hasRtp) && !allMetadataUnknown) {
    throw new Error(`Incomplete bet limits or RTP for ${game.name}`);
  }

  return {
    ...game,
    filename: `${filenamePrefix}-${slug}${extension}`,
  };
});

let nextDownload = 0;
await Promise.all(Array.from({ length: 6 }, async () => {
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
    console.log(`Refreshed ${game.name}`);
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
