#!/usr/bin/env python3
"""
Download images for all slots with provider-prefixed names.
Uses the gamingslots.com image patterns for each provider.
"""

import json
import os
import requests
import time
from pathlib import Path

# Load providers
with open('slot_providers.json', 'r') as f:
    providers_data = json.load(f)

# URL patterns for each provider
url_patterns = {
    'Pragmatic Play': 'https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/',
    'NetEnt': 'https://www.gamingslots.com/slots/netent/{slug}-slot/',
    'Hacksaw Gaming': 'https://www.gamingslots.com/slots/hacksaw-gaming/{slug}-slot/',
    'Play\'n GO': 'https://www.gamingslots.com/slots/play-n-go/{slug}-slot/',
    'Red Tiger': 'https://www.gamingslots.com/slots/red-tiger/{slug}-slot/',
}

# Image URL patterns for each provider
image_patterns = {
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

# Stats
ok = 0
failed = 0
total = len(providers_data)

print(f"Downloading {total} slot images with provider-prefixed names...\n")

for i, (image_name, provider) in enumerate(providers_data.items(), 1):
    # Extract slot name from image filename (remove provider prefix)
    prefix = provider.lower().replace("'", "").replace(" ", "-")
    slot_name = image_name.replace(f"{prefix}-", "").replace(".jpg", "").replace(".png", "")
    
    # Check if image already exists
    image_path = f"public/images/{image_name}"
    if os.path.exists(image_path):
        if i % 50 == 0:
            print(f"[{i}/{total}] {image_name}... [EXISTS]")
        ok += 1
        continue
    
    # Create slug for URL
    slug = name_to_slug(slot_name)
    
    # Get image URL pattern
    if provider not in image_patterns:
        if i % 50 == 0:
            print(f"[{i}/{total}] {image_name}... [UNKNOWN PROVIDER]")
        failed += 1
        continue
    
    image_url = image_patterns[provider].format(slug=slug)
    
    try:
        # Attempt to download
        response = requests.get(image_url, timeout=10)
        
        if response.status_code == 200:
            # Ensure directory exists
            Path("public/images").mkdir(parents=True, exist_ok=True)
            
            # Save image
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            ok += 1
            
            if i % 50 == 0:
                print(f"[{i}/{total}] {image_name}... ✓")
        else:
            failed += 1
            if i % 50 == 0:
                print(f"[{i}/{total}] {image_name}... [404]")
    
    except Exception as e:
        failed += 1
        if i % 50 == 0:
            print(f"[{i}/{total}] {image_name}... [ERROR: {type(e).__name__}]")
    
    # Small delay to avoid hammering server
    if i % 10 == 0:
        time.sleep(0.2)

print(f"\n{'='*50}")
print(f"Downloaded: {ok}/{total}")
print(f"Failed: {failed}/{total}")
print(f"Success rate: {100*ok//total}%")
