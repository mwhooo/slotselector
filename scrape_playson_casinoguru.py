"""
Scrape Playson slots from casino.guru (106 games across 6 pages)
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}
OUTPUT_DIR = "public/images"
TIMEOUT = 45
PAUSE_SECONDS = 2

print("=" * 60)
print("Scraping Playson slots from casino.guru")
print("=" * 60)

# Collect all game URLs from all pages
all_games = {}

for page in range(1, 7):  # 6 pages
    if page == 1:
        url = "https://casino.guru/free-casino-games/slots/playson"
    else:
        url = f"https://casino.guru/free-casino-games/playson/slots/{page}"
    
    print(f"\nPage {page}/6: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find game links
        game_links = soup.find_all('a', href=re.compile(r'-slot-play-free$'))
        
        for link in game_links:
            href = link.get('href', '')
            if href and '-slot-play-free' in href:
                # Get game name from text
                text = link.get_text(strip=True)
                if 'by Playson' in text:
                    name = text.replace('by Playson', '').strip()
                elif text and len(text) > 2 and not text.startswith('Play'):
                    name = text
                else:
                    continue
                
                if name not in all_games.values():
                    all_games[href] = name
        
        print(f"   Found {len(game_links)} links, total unique: {len(all_games)}")
        
        if page < 6:
            time.sleep(1)
            
    except Exception as e:
        print(f"   Error: {e}")

print(f"\n{'=' * 60}")
print(f"Total unique Playson games found: {len(all_games)}")
print("=" * 60)

# Now visit each game page to get the image
downloaded = 0
failed = 0
slots_list = []

for i, (url, name) in enumerate(all_games.items(), 1):
    slug = name.lower().replace(' ', '-').replace(':', '').replace("'", "")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    
    print(f"[{i}/{len(all_games)}] {name}...", end=" ")
    
    # Check if already exists
    existing = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"playson-{slug}")]
    if existing:
        print(f"✓ (already exists)")
        downloaded += 1
        slots_list.append(name)
        continue
    
    try:
        full_url = url if url.startswith('http') else 'https://casino.guru' + url
        resp = requests.get(full_url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find game image - look for main game preview image
        img = None
        
        # Try to find the main game image
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src', '')
            if 'static.casino.guru' in src and 'pict' in src:
                # Skip small icons
                if 'width=600' in src or 'width=400' in src or 'width=300' in src:
                    img = src
                    break
        
        if not img:
            # Try alternative - look for any large game image
            for img_tag in soup.find_all('img'):
                src = img_tag.get('src', '')
                if 'static.casino.guru' in src and '.png' in src:
                    img = src
                    break
        
        if not img:
            print("✗ No image found")
            failed += 1
            continue
        
        # Determine extension
        if '.webp' in img:
            ext = '.webp'
        elif '.png' in img:
            ext = '.png'
        else:
            ext = '.jpg'
        
        filename = f"playson-{slug}{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Download image
        img_resp = requests.get(img, headers=HEADERS, timeout=TIMEOUT)
        img_resp.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(img_resp.content)
        
        print(f"✓ {filename}")
        downloaded += 1
        slots_list.append(name)
        
    except Exception as e:
        print(f"✗ {e}")
        failed += 1
    
    # Pause periodically
    if i % 5 == 0:
        print(f"      ... pausing {PAUSE_SECONDS}s ...")
        time.sleep(PAUSE_SECONDS)

print("\n" + "=" * 60)
print(f"Downloaded: {downloaded}/{len(all_games)}")
print(f"Failed: {failed}")
print("=" * 60)

# Save slots list
with open('playson_slots.json', 'w') as f:
    json.dump(slots_list, f, indent=2)
print(f"\n✓ Saved {len(slots_list)} slots to playson_slots.json")
