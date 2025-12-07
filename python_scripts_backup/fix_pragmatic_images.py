import json
import urllib.request
from PIL import Image
from io import BytesIO
import os
import re
from urllib.error import URLError, HTTPError
import time

# Load existing providers or create new dict
try:
    with open('slot_providers.json', 'r', encoding='utf-8') as f:
        slots = json.load(f)
except:
    slots = {}

output_dir = "public/images"
os.makedirs(output_dir, exist_ok=True)

# If we only have 6, restore the full list by scraping again
if len(slots) < 50:
    print("Restoring full Pragmatic Play slot list...")
    import requests
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get("https://www.gamingslots.com/slots/pragmatic-play/", 
                              headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        slots = {}
        for link in soup.find_all('a', href=re.compile(r'/slots/pragmatic-play/')):
            if 'pragmatic-play/' not in link.get('href', ''):
                continue
            slot_name = link.get_text(strip=True).replace('Pragmatic Play', '').strip()
            if slot_name and slot_name not in slots:
                slots[slot_name] = "Pragmatic Play"
        
        print(f"Restored {len(slots)} slots")
    except Exception as e:
        print(f"Could not restore: {e}")

print(f"Fixing images for {len(slots)} Pragmatic Play slots...")

successful = 0
failed = 0
skipped = 0

for i, slot_name in enumerate(slots.keys(), 1):
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    # Skip if already exists - but we'll re-download to fix bad ones
    # Actually, let's check if it's the GS logo by file size
    if os.path.exists(output_file):
        skipped += 1
        continue
    
    # Construct slot URL
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slot_url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        if i % 50 == 0:
            print(f"[{i}/{len(slots)}] Processing...")
        
        # Fetch the slot page
        with urllib.request.urlopen(slot_url, timeout=10) as response:
            page_content = response.read().decode('utf-8', errors='ignore')
        
        # Look for slot-specific image URLs (not the generic GS logo)
        # Pattern: look for URLs with the slot name in them
        image_patterns = [
            rf'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*{re.escape(slug)}[^"<]*\.(?:jpg|png|webp)',
            r'https://www\.gamingslots\.com/wp-content/uploads/\d{4}/\d{2}/[^"<]*-(?:logo|slot|game)[^"<]*\.(?:jpg|png|webp)',
            r'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*\.(?:jpg|png|webp)(?![^"<]*icon-logo)',
        ]
        
        image_url = None
        for pattern in image_patterns:
            matches = re.findall(pattern, page_content)
            for match in matches:
                # Skip the generic GS logo
                if 'icon-logo' not in match and 'cropped' not in match:
                    image_url = match
                    break
            if image_url:
                break
        
        if not image_url:
            failed += 1
            continue
        
        # Download the image
        with urllib.request.urlopen(image_url, timeout=10) as response:
            image_data = response.read()
        
        # Open and convert
        img = Image.open(BytesIO(image_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPG
        img.save(output_file, 'JPEG', quality=85)
        successful += 1
        
    except Exception as e:
        failed += 1
    
    time.sleep(0.1)

# Save updated providers
with open('slot_providers.json', 'w', encoding='utf-8') as f:
    json.dump(slots, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"OK: {successful} | FAILED: {failed} | SKIPPED: {skipped}")
print(f"Total slots in provider file: {len(slots)}")
