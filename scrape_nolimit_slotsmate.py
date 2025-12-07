"""
Scrape NoLimit City slots from slotsmate.com
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os

BASE_URL = "https://www.slotsmate.com/software/nolimit-city"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
OUTPUT_DIR = "public/images"
TIMEOUT = 45
PAUSE_EVERY = 3
PAUSE_SECONDS = 1.5

print("=" * 60)
print("Scraping NoLimit City slots from slotsmate.com")
print("=" * 60)

# First get the list page
response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all slot links - they should be in format /software/nolimit-city/SLOT-NAME
slot_links = soup.find_all('a', href=re.compile(r'/software/nolimit-city/[a-z0-9-]+$'))
unique_urls = set()
for link in slot_links:
    href = link.get('href', '')
    if href and not href.endswith('/nolimit-city'):
        unique_urls.add(href)

print(f"\n1. Found {len(unique_urls)} slot URLs on main page")

# For each slot, we need to get the image
# The image structure on slotsmate seems to be: preview images on the listing
# Let's find image elements near slot links

# Look for game cards/items with images
game_items = []
for link in slot_links:
    href = link.get('href', '')
    if not href or href.endswith('/nolimit-city'):
        continue
    
    # Get slot name from URL
    slot_name = href.split('/')[-1]
    
    # Look for associated image
    parent = link.parent
    img = parent.find('img') if parent else None
    if not img:
        # Try going up more levels
        for _ in range(3):
            parent = parent.parent if parent else None
            if parent:
                img = parent.find('img')
                if img:
                    break
    
    img_src = img.get('src', '') if img else ''
    if img_src:
        game_items.append({
            'name': slot_name,
            'url': 'https://www.slotsmate.com' + href,
            'img': img_src
        })

print(f"   Found {len(game_items)} slots with images")

# Remove duplicates
seen_names = set()
unique_games = []
for g in game_items:
    if g['name'] not in seen_names:
        seen_names.add(g['name'])
        unique_games.append(g)

print(f"   Unique slots: {len(unique_games)}")

# Show first 10
print("\nFirst 10 slots:")
for i, g in enumerate(unique_games[:10], 1):
    name_clean = g['name'].replace('-', ' ').title()
    print(f"  {i}. {name_clean}")
    print(f"      Image: {g['img'][:80]}...")

# Now let's download the images
print("\n" + "=" * 60)
print("Downloading images...")
print("=" * 60)

downloaded = 0
failed = 0
slots_list = []

for i, game in enumerate(unique_games, 1):
    name = game['name'].replace('-', ' ').title()
    img_url = game['img']
    
    # Determine file extension
    if '.webp' in img_url:
        ext = '.webp'
    elif '.png' in img_url:
        ext = '.png'
    else:
        ext = '.jpg'
    
    filename = f"nolimitcity-{game['name']}{ext}"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    print(f"[{i}/{len(unique_games)}] {name}...", end=" ")
    
    if os.path.exists(filepath):
        print("✓ (already exists)")
        downloaded += 1
        slots_list.append(name)
        continue
    
    try:
        # Make sure URL is absolute
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        elif img_url.startswith('/'):
            img_url = 'https://www.slotsmate.com' + img_url
        
        img_resp = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT)
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
    if i % PAUSE_EVERY == 0 and i < len(unique_games):
        print(f"      ... pausing {PAUSE_SECONDS}s ...")
        time.sleep(PAUSE_SECONDS)

print("\n" + "=" * 60)
print(f"Downloaded: {downloaded}/{len(unique_games)}")
print(f"Failed: {failed}")
print("=" * 60)

# Save slots list
with open('nolimitcity_slots.json', 'w') as f:
    json.dump(slots_list, f, indent=2)
print(f"\n✓ Saved {len(slots_list)} slots to nolimitcity_slots.json")
