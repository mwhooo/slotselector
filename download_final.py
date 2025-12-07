#!/usr/bin/env python3
"""
Download all slot images using urllib (more stable).
Provider-prefixed filenames to prevent overwrites.
"""

import json
import os
import urllib.request
import time
from pathlib import Path

# Load providers with provider-prefixed image names
with open('slot_providers.json', 'r') as f:
    providers_data = json.load(f)

print(f"Total slots to download: {len(providers_data)}")

# URL patterns for each provider
image_urls = {
    'Pragmatic Play': 'https://www.gamingslots.com/images/slots/pragmatic-play/{slug}-slot-logo.jpg',
    'NetEnt': 'https://www.gamingslots.com/images/slots/netent/{slug}-slot-logo.jpg',
    'Hacksaw Gaming': 'https://www.gamingslots.com/images/slots/hacksaw-gaming/{slug}-logo-hacksaw-gaming.png',
    'Play\'n GO': 'https://www.gamingslots.com/images/slots/play-n-go/{slug}-slot-logo.jpg',
    'Red Tiger': 'https://www.gamingslots.com/images/slots/red-tiger/{slug}-slot-logo.jpg',
}

def name_to_slug(name):
    """Convert slot name to URL slug"""
    slug = name.lower()
    slug = slug.replace("'", "").replace("â€™", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    return slug

# Create output directory
Path("public/images").mkdir(parents=True, exist_ok=True)

# Statistics
ok = 0
failed = 0
skipped = 0

print("Starting download...\n")

for i, (image_name, provider) in enumerate(providers_data.items(), 1):
    image_path = f"public/images/{image_name}"
    
    # Skip if already exists
    if os.path.exists(image_path):
        skipped += 1
        continue
    
    # Extract slot name from image filename
    prefix = provider.lower().replace("'", "").replace(" ", "-")
    slot_name = image_name.replace(f"{prefix}-", "").replace(".jpg", "").replace(".png", "")
    
    # Create slug
    slug = name_to_slug(slot_name)
    
    # Get image URL
    if provider not in image_urls:
        failed += 1
        continue
    
    image_url = image_urls[provider].format(slug=slug)
    
    try:
        urllib.request.urlretrieve(image_url, image_path)
        ok += 1
        
        if i % 50 == 0:
            print(f"[{i}/{len(providers_data)}] OK: {ok}, Failed: {failed}, Skipped: {skipped}")
    
    except Exception as e:
        # Delete failed file
        if os.path.exists(image_path):
            os.remove(image_path)
        failed += 1
    
    # Rate limiting
    if i % 20 == 0:
        time.sleep(0.5)

print(f"\n{'='*50}")
print(f"✓ Downloaded: {ok}")
print(f"✗ Failed: {failed}")
print(f"⊘ Skipped (existed): {skipped}")
print(f"{'='*50}")

total_images = ok + skipped
pct = 100*total_images//len(providers_data) if len(providers_data) > 0 else 0
print(f"Total images: {total_images}/{len(providers_data)} ({pct}%)")
