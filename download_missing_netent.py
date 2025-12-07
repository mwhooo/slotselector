#!/usr/bin/env python3
"""Download missing NetEnt slot images"""
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

# Get only NetEnt slots
netent_slots = {name: provider for name, provider in slots.items() if provider == 'NetEnt'}

print(f"Downloading missing NetEnt slot images...")
print(f"Total NetEnt slots: {len(netent_slots)}\n")

successful = 0
failed = 0
skipped = 0
missing = []

for i, slot_name in enumerate(netent_slots.keys(), 1):
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    # Skip if already exists
    if os.path.exists(output_file):
        skipped += 1
        continue
    
    print(f"[{i}/{len(netent_slots)}] Downloading {slot_name}...")
    
    # Construct slot URL on gamingslots.com
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slot_url = f"https://www.gamingslots.com/slots/netent/{slug}-slot/"
    
    try:
        # Fetch the slot page
        try:
            with urllib.request.urlopen(slot_url, timeout=10) as response:
                page_content = response.read().decode('utf-8', errors='ignore')
        except HTTPError as e:
            if e.code == 404:
                missing.append(slot_name)
                failed += 1
                print(f"  → 404 Not Found")
                continue
            raise
        
        # Look for image URL in the page
        image_patterns = [
            r'https://www\.gamingslots\.com/wp-content/uploads/[^"\s<]*\.(?:jpg|png|webp)',
        ]
        
        image_url = None
        for pattern in image_patterns:
            matches = re.findall(pattern, page_content)
            for match in matches:
                if any(x in match for x in ['-logo', '-slot', '-icon', '-game']):
                    image_url = match
                    break
            if image_url:
                break
        
        if not image_url:
            missing.append(slot_name)
            failed += 1
            print(f"  → No image found on page")
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
        print(f"  → Downloaded successfully")
        
    except Exception as e:
        missing.append(slot_name)
        failed += 1
        print(f"  → Error: {str(e)}")
    
    # Rate limiting
    time.sleep(0.3)

print(f"\n{'='*70}")
print(f"OK: {successful} | FAILED: {failed} | SKIPPED: {skipped}")
print(f"TOTAL DOWNLOADED: {successful}/{len(netent_slots)}")

if missing:
    print(f"\nMissing ({len(missing)}):")
    for slot in sorted(missing):
        print(f"  - {slot}")
