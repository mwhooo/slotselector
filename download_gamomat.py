#!/usr/bin/env python3
"""
Download Gamomat slot images by extracting from each game page
Shows progress, pauses, quits on too many errors
"""

import json
import requests
from bs4 import BeautifulSoup
import urllib.request
import os
import time
from pathlib import Path

# Load slots
with open('gamomat_slots.json', 'r') as f:
    slot_names = json.load(f)

print("="*60)
print(f"Downloading images for {len(slot_names)} Gamomat slots")
print("="*60)
print()

# Create output directory
Path("public/images").mkdir(parents=True, exist_ok=True)

ok = 0
failed = 0

for i, name in enumerate(slot_names, 1):
    # Create slug from name
    slug = name.lower().replace("'", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    
    # Game page URL
    game_url = f"https://www.gamingslots.com/slots/gamomat/{slug}-slot/"
    
    # Filename: gamomat-{slug}.jpg (or .png)
    image_name = f"gamomat-{slug}"
    
    try:
        print(f"[{i:2d}/{len(slot_names)}] {name}...", end=" ", flush=True)
        
        # Fetch game page
        game_response = requests.get(game_url, timeout=20)
        soup = BeautifulSoup(game_response.text, 'html.parser')
        
        # Find image with slot-logo pattern
        images = soup.find_all('img')
        image_url = None
        ext = 'jpg'
        
        for img in images:
            src = img.get('src', '')
            if 'slot-logo' in src and src.endswith(('.jpg', '.png')):
                image_url = src
                ext = 'png' if src.endswith('.png') else 'jpg'
                break
        
        if image_url:
            # Download image
            image_path = f"public/images/{image_name}.{ext}"
            urllib.request.urlretrieve(image_url, image_path)
            print("✓")
            ok += 1
        else:
            print("✗ (no image found)")
            failed += 1
    
    except Exception as e:
        print(f"✗ ({type(e).__name__})")
        failed += 1
    
    # Pause every 5 downloads
    if i % 5 == 0:
        time.sleep(0.3)
    
    # Quit if too many errors
    if failed > 15:
        print(f"\n⚠️  Too many errors ({failed}). Stopping.")
        break

print()
print("="*60)
print(f"✓ Downloaded: {ok}")
print(f"✗ Failed: {failed}")
print("="*60)
