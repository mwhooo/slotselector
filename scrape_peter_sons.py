"""
Scrape Peter & Sons slots from gamingslots.com
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os

BASE_URL = "https://www.gamingslots.com/slots/peter-sons/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
OUTPUT_DIR = "public/images"
TIMEOUT = 45
PAUSE_EVERY = 3
PAUSE_SECONDS = 1.5

print("=" * 60)
print("Scraping Peter & Sons slots from gamingslots.com")
print("=" * 60)

# Get all slot URLs from the listing page
print("\n1. Fetching slots list page...")
response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all slot page links
slot_links = soup.find_all('a', href=re.compile(r'/slots/peter-sons/[^/]+-slot/?$'))
unique_urls = set()
for link in slot_links:
    unique_urls.add(link['href'])

print(f"   ✓ Found {len(unique_urls)} unique slot URLs")

# Download each slot's image
downloaded = 0
failed = 0
slots_list = []
failed_slots = []

for i, url in enumerate(sorted(unique_urls), 1):
    # Extract slot name from URL
    slot_slug = url.rstrip('/').split('/')[-1].replace('-slot', '')
    slot_name = slot_slug.replace('-', ' ').title()
    
    print(f"[{i}/{len(unique_urls)}] {slot_name}...", end=" ")
    
    try:
        # Fetch slot detail page
        full_url = url if url.startswith('http') else 'https://www.gamingslots.com' + url
        detail_resp = requests.get(full_url, headers=HEADERS, timeout=TIMEOUT)
        detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
        
        # Find the game frame with background image
        game_frame = detail_soup.find('div', id='fpgame-frame')
        if not game_frame:
            print("✗ No game frame found")
            failed += 1
            failed_slots.append(slot_name)
            continue
        
        # Extract background image URL from style
        style = game_frame.get('style', '')
        img_match = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", style)
        if not img_match:
            print("✗ No image URL in style")
            failed += 1
            failed_slots.append(slot_name)
            continue
        
        img_url = img_match.group(1)
        
        # Determine file extension
        if '.webp' in img_url:
            ext = '.webp'
        elif '.png' in img_url:
            ext = '.png'
        else:
            ext = '.jpg'
        
        filename = f"petersons-{slot_slug}{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Check if already exists
        existing = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"petersons-{slot_slug}.")]
        if existing:
            print(f"✓ {existing[0]} (already exists)")
            downloaded += 1
            slots_list.append(slot_name)
            continue
        
        # Download image
        img_resp = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT)
        img_resp.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(img_resp.content)
        
        print(f"✓ {filename}")
        downloaded += 1
        slots_list.append(slot_name)
        
    except Exception as e:
        print(f"✗ {e}")
        failed += 1
        failed_slots.append(slot_name)
    
    # Pause periodically
    if i % PAUSE_EVERY == 0 and i < len(unique_urls):
        print(f"      ... pausing {PAUSE_SECONDS}s ...")
        time.sleep(PAUSE_SECONDS)

print("\n" + "=" * 60)
print(f"Downloaded: {downloaded}/{len(unique_urls)}")
print(f"Failed: {failed}")
print("=" * 60)

if failed_slots:
    print(f"\nFailed slots: {', '.join(failed_slots)}")

# Save slots list
with open('petersons_slots.json', 'w') as f:
    json.dump(slots_list, f, indent=2)
print(f"\n✓ Saved {len(slots_list)} slots to petersons_slots.json")
