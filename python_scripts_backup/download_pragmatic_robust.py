import json
import urllib.request
from PIL import Image
from io import BytesIO
import os
import re
from urllib.error import URLError, HTTPError
import time

# Load slot providers
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

output_dir = "public/images"
os.makedirs(output_dir, exist_ok=True)

print(f"Downloading images for Pragmatic Play slots from gamingslots.com...")
print("Starting from where we left off...\n")

successful = 0
failed = 0
skipped = 0

for i, slot_name in enumerate(slots.keys(), 1):
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    # Skip if already exists
    if os.path.exists(output_file):
        skipped += 1
        continue
    
    # Construct slot URL on gamingslots.com
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    # Handle some special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slot_url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        if i % 50 == 0:
            print(f"[{i}/{len(slots)}] Processing {slot_name}...", flush=True)
        
        # Fetch the slot page with retry
        try:
            with urllib.request.urlopen(slot_url, timeout=10) as response:
                page_content = response.read().decode('utf-8', errors='ignore')
        except HTTPError as e:
            if e.code == 404:
                failed += 1
                continue
            raise
        
        # Look for image URL in the page
        image_patterns = [
            r'https://www\.gamingslots\.com/wp-content/uploads/[^"\s<]*\.(?:jpg|png|webp)',
        ]
        
        image_url = None
        for pattern in image_patterns:
            matches = re.findall(pattern, page_content)
            # Filter for logo/slot images
            for match in matches:
                if any(x in match for x in ['-logo', '-slot', '-icon', '-game']):
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
        
        # Open and convert image
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPG
        img.save(output_file, 'JPEG', quality=85)
        successful += 1
        
    except Exception as e:
        failed += 1
    
    # Rate limiting
    time.sleep(0.2)

print(f"\n{'='*60}")
print(f"OK: {successful} | FAILED: {failed} | SKIPPED: {skipped}")
print(f"TOTAL: {successful + failed + skipped}/{len(slots)}")
