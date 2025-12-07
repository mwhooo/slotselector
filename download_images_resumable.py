#!/usr/bin/env python3
"""
Download images with automatic resume capability.
Tracks progress in a JSON file.
"""

import json
import os
import requests
import time
from pathlib import Path

PROGRESS_FILE = 'download_progress.json'

# Load providers
with open('slot_providers.json', 'r') as f:
    providers_data = json.load(f)

# Load progress
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, 'r') as f:
        progress = json.load(f)
else:
    progress = {
        'completed': [],
        'failed': [],
        'total': len(providers_data)
    }

# Image URL patterns
image_patterns = {
    'Pragmatic Play': 'https://www.gamingslots.com/images/slots/pragmatic-play/{slug}-slot-logo.jpg',
    'NetEnt': 'https://www.gamingslots.com/images/slots/netent/{slug}-slot-logo.jpg',
    'Hacksaw Gaming': 'https://www.gamingslots.com/images/slots/hacksaw-gaming/{slug}-logo-hacksaw-gaming.png',
    'Play\'n GO': 'https://www.gamingslots.com/images/slots/play-n-go/{slug}-slot-logo.jpg',
    'Red Tiger': 'https://www.gamingslots.com/images/slots/red-tiger/{slug}-slot-logo.jpg',
    'Relax Gaming': 'https://www.gamingslots.com/images/slots/relax-gaming/{slug}-slot-logo.jpg',
}

def name_to_slug(name):
    slug = name.lower()
    slug = slug.replace("'", "").replace("â€™", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    return slug

# Statistics
ok = len(progress['completed'])
failed = len(progress['failed'])
total = len(providers_data)
skipped = 0

print(f"Resuming download: {ok} done, {failed} failed, {total-ok-failed} remaining...\n")

for i, (image_name, provider) in enumerate(providers_data.items(), 1):
    # Skip if already processed
    if image_name in progress['completed'] or image_name in progress['failed']:
        skipped += 1
        continue
    
    # Extract slot name
    prefix = provider.lower().replace("'", "").replace(" ", "-")
    slot_name = image_name.replace(f"{prefix}-", "").replace(".jpg", "").replace(".png", "")
    slot_name = slot_name.replace(f"{prefix}-", "", 1)  # Remove prefix
    
    # Create slug
    slug = name_to_slug(slot_name)
    
    # Check if exists
    image_path = f"public/images/{image_name}"
    if os.path.exists(image_path):
        progress['completed'].append(image_name)
        ok += 1
        if (ok + failed) % 50 == 0:
            print(f"[{ok+failed}/{total}] {image_name}... [EXISTS]")
        continue
    
    # Get URL
    if provider not in image_patterns:
        progress['failed'].append(image_name)
        failed += 1
        continue
    
    image_url = image_patterns[provider].format(slug=slug)
    
    try:
        response = requests.get(image_url, timeout=15)
        
        if response.status_code == 200:
            Path("public/images").mkdir(parents=True, exist_ok=True)
            
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            progress['completed'].append(image_name)
            ok += 1
            
            if (ok + failed) % 50 == 0:
                print(f"[{ok+failed}/{total}] {image_name}... ✓")
        else:
            progress['failed'].append(image_name)
            failed += 1
    
    except Exception as e:
        progress['failed'].append(image_name)
        failed += 1
    
    # Save progress every 50 images
    if (ok + failed) % 50 == 0:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)
    
    # Small delay
    if (ok + failed) % 10 == 0:
        time.sleep(0.3)

# Final save
with open(PROGRESS_FILE, 'w') as f:
    json.dump(progress, f)

print(f"\n{'='*60}")
print(f"✓ Downloaded: {ok}/{total}")
print(f"✗ Failed: {failed}/{total}")
print(f"⊘ Skipped (already done): {skipped}")
print(f"Success rate: {100*ok//total}%")
print(f"\nProgress saved to {PROGRESS_FILE}")
