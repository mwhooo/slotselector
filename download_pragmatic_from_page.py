#!/usr/bin/env python3
"""
Download Pragmatic Play images by extracting from the page HTML
"""

import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import os
from pathlib import Path

url = "https://www.gamingslots.com/slots/pragmatic-play/"

print("Fetching Pragmatic Play page...")
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all slot links
slot_links = soup.find_all('a', href=re.compile(r'/slots/pragmatic-play/[^/]+-slot/'))

print(f"Found {len(slot_links)} slots. Processing first 10...\n")

Path("public/images").mkdir(parents=True, exist_ok=True)

ok = 0
failed = 0

for link in slot_links[:10]:
    href = link.get('href')
    match = re.search(r'/slots/pragmatic-play/([^/]+)-slot/', href)
    if not match:
        continue
    
    slug = match.group(1)
    slot_url = f"https://www.gamingslots.com{href}"
    
    # Fetch slot page to get image
    try:
        slot_response = requests.get(slot_url, timeout=30)
        slot_soup = BeautifulSoup(slot_response.text, 'html.parser')
        
        # Find image - look for pattern {slug}-slot-logo
        images = slot_soup.find_all('img')
        image_url = None
        
        for img in images:
            src = img.get('src', '')
            if f'{slug}-slot-logo' in src and (src.endswith('.jpg') or src.endswith('.png')):
                image_url = src
                break
        
        if image_url:
            # Create filename: pragmatic-{slug}.{ext}
            ext = 'jpg' if image_url.endswith('.jpg') else 'png'
            image_name = f"pragmatic-{slug}.{ext}"
            image_path = f"public/images/{image_name}"
            
            print(f"Downloading: {image_name}")
            urllib.request.urlretrieve(image_url, image_path)
            print(f"  ✓ OK")
            ok += 1
        else:
            print(f"Downloading: pragmatic-{slug} - Image URL not found")
            failed += 1
    
    except Exception as e:
        print(f"Error: {type(e).__name__}")
        failed += 1

print(f"\n{'='*50}")
print(f"✓ Downloaded: {ok}")
print(f"✗ Failed: {failed}")
