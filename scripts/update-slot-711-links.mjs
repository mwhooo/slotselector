import fs from 'node:fs/promises';
import path from 'node:path';

const dataDirectory = path.resolve('data');
const providers = JSON.parse(await fs.readFile(path.join(dataDirectory, 'slot_providers.json'), 'utf8'));
const outputPath = path.join(path.resolve('public'), 'slot_711_links.json');

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

  return name
    .replace(/_/g, ' ')
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
    .trim()
    .replace(/\s+/g, ' ');
};

const localSlots = [...new Map(Object.entries(providers).map(([filename, provider]) => {
  const name = getDisplayName(filename, provider);
  return [`${provider}:${normalizeSlotName(name)}`, { name, provider }];
})).values()];

const fetchPage = async (pageNumber) => {
  const url = new URL('https://www.711.nl/api/games');
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
    per_page: '200',
    page: String(pageNumber),
  })) {
    url.searchParams.set(key, value);
  }

  const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`711 API returned ${response.status} for page ${pageNumber}`);
  return response.json();
};

const firstPage = await fetchPage(1);
const apiGames = [...(firstPage.data ?? [])];
for (let pageNumber = 2; pageNumber <= firstPage.meta.last_page; pageNumber += 4) {
  const pageNumbers = Array.from(
    { length: Math.min(4, firstPage.meta.last_page - pageNumber + 1) },
    (_, index) => pageNumber + index
  );
  const pages = await Promise.all(pageNumbers.map(fetchPage));
  apiGames.push(...pages.flatMap((page) => page.data ?? []));
  console.log(`Fetched ${Math.min(pageNumber + pageNumbers.length - 1, firstPage.meta.last_page)}/${firstPage.meta.last_page} pages`);
}

const apiMatches = new Map();
for (const game of apiGames) {
  if (!game.real_play || !game.real_play_url) continue;

  let launchUrl;
  try {
    launchUrl = new URL(game.real_play_url);
  } catch {
    continue;
  }
  if (launchUrl.hostname !== 'www.711.nl' || !launchUrl.pathname.startsWith('/g/nl/')) continue;

  const key = `${normalizeProvider(game.provider)}:${normalizeSlotName(game.name)}`;
  const urls = apiMatches.get(key) ?? new Set();
  urls.add(launchUrl.href);
  apiMatches.set(key, urls);
}

const links = {};
const unmatched = [];
const ambiguous = [];
for (const slot of localSlots) {
  const apiKey = `${normalizeProvider(slot.provider)}:${normalizeSlotName(slot.name)}`;
  const matches = apiMatches.get(apiKey);
  if (matches?.size === 1) {
    links[`${slot.provider}:${normalizeSlotName(slot.name)}`] = { '711': [...matches][0] };
  } else if (matches?.size > 1) {
    ambiguous.push(slot);
  } else {
    unmatched.push(slot);
  }
}

await fs.writeFile(outputPath, `${JSON.stringify(links, null, 2)}\n`);
console.log(JSON.stringify({
  apiGames: apiGames.length,
  localSlots: localSlots.length,
  linked: Object.keys(links).length,
  unmatched: unmatched.length,
  ambiguous: ambiguous.length,
  unmatchedExamples: unmatched.slice(0, 20),
  ambiguousExamples: ambiguous.slice(0, 10),
}, null, 2));