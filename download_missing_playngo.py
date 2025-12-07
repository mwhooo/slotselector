#!/usr/bin/env python3
"""Download missing Play'n GO slot images from gamingslots.com"""
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

# Get only Play'n GO slots
playngo_slots = {name: provider for name, provider in slots.items() if provider == "Play'n GO"}

print(f"Downloading missing Play'n GO slot images...")
print(f"Total Play'n GO slots: {len(playngo_slots)}\n")

successful = 0
failed = 0
skipped = 0
missing = []

for i, slot_name in enumerate(playngo_slots.keys(), 1):
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    # Skip if already exists
    if os.path.exists(output_file):
        skipped += 1
        continue
    
    # Construct slot URL on gamingslots.com
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slot_url = f"https://www.gamingslots.com/slots/playn-go/{slug}-slot/"
    
    try:
        if i % 20 == 0:
            print(f"[{i}/{len(playngo_slots)}] Processing {slot_name}...", flush=True)
        
        # Fetch the slot page
        try:
            with urllib.request.urlopen(slot_url, timeout=10) as response:
                page_content = response.read().decode('utf-8', errors='ignore')
        except HTTPError as e:
            if e.code == 404:
                missing.append(slot_name)
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
            for match in matches:
                if any(x in match for x in ['-logo', '-slot', '-icon', '-game']):
                    image_url = match
                    break
            if image_url:
                break
        
        if not image_url:
            missing.append(slot_name)
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
        missing.append(slot_name)
        failed += 1
    
    # Rate limiting
    time.sleep(0.1)

print(f"\n{'='*70}")
print(f"OK: {successful} | FAILED: {failed} | SKIPPED: {skipped}")
print(f"TOTAL DOWNLOADED: {successful}/{len(playngo_slots)}")

if missing and len(missing) <= 20:
    print(f"\nMissing ({len(missing)}):")
    for slot in sorted(missing):
        print(f"  - {slot}")
elif missing:
    print(f"\nMissing {len(missing)} images - check gamingslots.com for these")
