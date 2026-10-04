import fs from 'node:fs/promises';
import path from 'node:path';

const dataDirectory = path.resolve('data');
const providers = JSON.parse(await fs.readFile(path.join(dataDirectory, 'slot_providers.json'), 'utf8'));
const rtpPath = path.join(dataDirectory, 'slot_rtp.json');
const rtpByProvider = JSON.parse(await fs.readFile(rtpPath, 'utf8'));

const normalizeSlotName = (name) => name
  .toLowerCase()
  .replace(/&/g, 'and')
  .replace(/tm$/i, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const normalizeProvider = (provider) => provider
  .toLowerCase()
  .replace(/[^a-z0-9]/g, '')
  .replace(/(gaming|games|game|studios|studio)$/i, '');

const getDisplayName = (filename, provider) => {
  let name = filename.replace(/\.(jpe?g|png|gif|webp)$/i, '');
  const providerSlug = provider
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-');
  const providerPatterns = [...new Set([
    providerSlug.replace(/-/g, '[-_\\s]*'),
    providerSlug.replace(/-/g, ''),
    providerSlug.split('-')[0],
  ])].sort((left, right) => right.length - left.length);

  for (const pattern of providerPatterns) {
    name = name.replace(new RegExp(`^${pattern}[-_\\s]*`, 'i'), '');
  }

  const displayName = name
    .replace(/_/g, ' ')
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
    .trim()
    .replace(/\s+/g, ' ');

  return displayName.replace(/tm$/i, '').trim();
};

const existingNames = new Map(Object.entries(rtpByProvider).map(([provider, games]) => [
  provider,
  new Set(Object.entries(games)
    .filter(([, value]) => Number.isFinite(value))
    .map(([name]) => normalizeSlotName(name))),
]));

const uniqueSlots = new Map();
for (const [filename, provider] of Object.entries(providers)) {
  const name = getDisplayName(filename, provider);
  uniqueSlots.set(`${provider}:${normalizeSlotName(name)}`, { name, provider });
}

const missingSlots = [...uniqueSlots.values()].filter(({ name, provider }) =>
  !existingNames.get(provider)?.has(normalizeSlotName(name))
);

const searchUrl = new URL('https://www.711.nl/api/games');
for (const [key, value] of Object.entries({
  device_support: 'desktop',
  locale: 'nl',
  country: '',
  jurisdiction: '',
  types: '',
  providers: '',
  tags: '',
  number_of_reels: '',
  min_bet: '',
  max_bet: '',
  fuzzy: 'false',
  useAdditionalParameters: 'true',
  per_page: '12',
  page: '',
})) {
  searchUrl.searchParams.set(key, value);
}

const lookupRtp = async ({ name, provider }) => {
  const url = new URL(searchUrl);
  url.searchParams.set('q', name);
  const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`711 API returned ${response.status} for ${name}`);

  const { data = [] } = await response.json();
  const matchingValues = [...new Set(data
    .filter((game) => normalizeSlotName(game.name) === normalizeSlotName(name)
      && normalizeProvider(game.provider) === normalizeProvider(provider))
    .map((game) => Number(game.return_to_player))
    .filter((value) => Number.isFinite(value) && value > 0 && value <= 100))];

  return { name, provider, matchingValues };
};

const results = [];
for (let offset = 0; offset < missingSlots.length; offset += 4) {
  const batch = missingSlots.slice(offset, offset + 4);
  results.push(...await Promise.all(batch.map(lookupRtp)));
  const completed = Math.min(offset + batch.length, missingSlots.length);
  console.log(`Checked ${completed}/${missingSlots.length} missing RTP values`);
}

const resolved = results.filter(({ matchingValues }) => matchingValues.length === 1);
const ambiguous = results.filter(({ matchingValues }) => matchingValues.length > 1);

for (const { name, provider, matchingValues } of resolved) {
  const games = rtpByProvider[provider] ?? (rtpByProvider[provider] = {});
  games[name] = matchingValues[0];
}

if (resolved.length > 0) {
  await fs.writeFile(rtpPath, `${JSON.stringify(rtpByProvider, null, 2)}\n`);
}

console.log(JSON.stringify({
  checked: results.length,
  added: resolved.length,
  ambiguous: ambiguous.length,
  unresolved: results.length - resolved.length,
  unresolvedByProvider: Object.entries(results
    .filter(({ matchingValues }) => matchingValues.length !== 1)
    .reduce((counts, { provider }) => {
      counts[provider] = (counts[provider] ?? 0) + 1;
      return counts;
    }, {}))
    .sort((left, right) => right[1] - left[1]),
}, null, 2));