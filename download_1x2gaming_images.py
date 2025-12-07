#!/usr/bin/env python3
"""
Download 1x2gaming slot images from gamingslots.com
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pathlib import Path

# Load slot names from JSON
with open('1x2gaming_slots.json', 'r') as f:
    slots = json.load(f)

base_url = "https://www.gamingslots.com/slots/1x2gaming/"
images_dir = Path("public/images")
images_dir.mkdir(exist_ok=True)

print("="*60)
print("Downloading 1x2gaming slot images")
print("="*60)
print()

downloaded = 0
failed = 0

for i, slot_name in enumerate(slots, 1):
    # Convert slot name to slug
    slug = slot_name.lower().replace(' ', '-')
    slot_url = f"{base_url}{slug}-slot/"
    
    try:
        print(f"[{i}/{len(slots)}] {slot_name}...", end=" ", flush=True)
        
        # Fetch the slot page
        response = requests.get(slot_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            failed += 1
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the game frame div with background image
        img_url = None
        game_frame = soup.find('div', id='fpgame-frame')
        
        if game_frame:
            # Extract URL from style attribute background-image
            style = game_frame.get('style', '')
            if 'url(' in style:
                # Extract the URL between url( and )
                start = style.find('url(') + 4
                end = style.find(')', start)
                if end > start:
                    img_url = style[start:end].strip('\'"')
        
        # Fallback: try to find an img tag with class containing 'gamethumb'
        if not img_url:
            img_tag = soup.find('img', class_=lambda x: x and 'gamethumb' in x)
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
        
        if not img_url:
            print("❌ No image found")
            failed += 1
            continue
        
        # Handle relative URLs
        if img_url.startswith('/'):
            img_url = "https://www.gamingslots.com" + img_url
        elif not img_url.startswith('http'):
            img_url = base_url + img_url
        
        # Download the image
        img_response = requests.get(img_url, timeout=10)
        
        if img_response.status_code != 200:
            print(f"❌ Failed to download image")
            failed += 1
            continue
        
        # Determine file extension
        content_type = img_response.headers.get('content-type', '').lower()
        if 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'
        
        # Save the image
        filename = f"1x2gaming-{slug}{ext}"
        filepath = images_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(img_response.content)
        
        print(f"✓ {filename}")
        downloaded += 1
        
        # Small pause to avoid hammering the server
        if i % 5 == 0:
            time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ {type(e).__name__}: {str(e)[:50]}")
        failed += 1
        continue

print()
print("="*60)
print(f"Downloaded: {downloaded}/{len(slots)}")
print(f"Failed: {failed}")
print("="*60)
