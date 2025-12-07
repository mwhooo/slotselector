import fs from 'fs';
import https from 'https';
import path from 'path';

// Path to the HTML file
const htmlFilePath = path.join(process.cwd(), 'jacks.html');

// Directory to save images
const dir = path.join(process.cwd(), 'public', 'images');

if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

// Function to extract image URLs from HTML
function extractImageUrls(html) {
  const srcRegex = /src=([^ >]+)/g;
  const dataSrcRegex = /data-src=([^ >]+)/g;
  const dataLazySrcRegex = /data-lazy-src=([^ >]+)/g;
  const urls = new Set();

  let match;
  while ((match = srcRegex.exec(html)) !== null) {
    urls.add(match[1]);
  }
  while ((match = dataSrcRegex.exec(html)) !== null) {
    urls.add(match[1]);
  }
  while ((match = dataLazySrcRegex.exec(html)) !== null) {
    urls.add(match[1]);
  }

  return Array.from(urls);
}

// List of specific image URLs to download
const imageUrls = [
  'https://jacks.nl/media/2023-04/jacksnl-opengraph.jpg',
  'https://jacks.nl/media/2025-05/offer-01.jpg',
  'https://jacks.nl/media/2025-05/offer-02.jpg',
  'https://jacks.nl/media/2025-05/offer-03.jpg',
  'https://jacks.nl/media/2025-05/offer-04.jpg',
  'https://jacks.nl/media/2025-05/popular-01.jpg',
  'https://jacks.nl/media/2025-05/popular-02.jpg',
  'https://jacks.nl/media/2022-03/might-of-ra-ifg-game.jpeg'
];

console.log(`Found ${imageUrls.length} image URLs`);

const downloadPromises = imageUrls.map((url, index) => {
  return new Promise((resolve) => {
    const ext = path.extname(url.split('?')[0]);
    const filename = `image${index + 1}${ext}`;
    const filePath = path.join(dir, filename);

    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        console.error(`Failed to download ${url}: Status ${response.statusCode}`);
        resolve();
        return;
      }

      const file = fs.createWriteStream(filePath);
      response.pipe(file);

      file.on('finish', () => {
        file.close();
        console.log(`Downloaded ${filename}`);
        resolve();
      });
    }).on('error', (err) => {
      console.error(`Error downloading ${url}: ${err.message}`);
      resolve();
    });
  });
});

await Promise.all(downloadPromises);
console.log('All downloads completed.');