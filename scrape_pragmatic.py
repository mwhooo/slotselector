#!/usr/bin/env python3
"""
Scrape Pragmatic Play slots from gamingslots.com
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time

def get_pragmatic_slots():
    """Get all Pragmatic Play slots from gamingslots.com"""
    url = "https://www.gamingslots.com/slots/pragmatic-play/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all slot links
    slot_links = soup.find_all('a', href=re.compile(r'/slots/pragmatic-play/[^/]+-slot/'))
    
    slots = {}
    for link in slot_links:
        href = link.get('href', '')
        match = re.search(r'/slots/pragmatic-play/([^/]+)/', href)
        if match:
            slug = match.group(1)
            slots[slug] = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}/"
    
    return slots

def download_slot_image(slug, url, output_dir):
    """Download image for a single slot"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        img_url = None
        
        # Method 1: Find the game frame with background image
        game_frame = soup.find('div', id='fpgame-frame')
        if game_frame:
            style = game_frame.get('style', '')
            match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if match:
                img_url = match.group(1)
        
        # Method 2: Look for slot logo/artwork in content
        if not img_url:
            slot_name = slug.replace('-slot', '')
            imgs = soup.find_all('img', src=re.compile(rf'{slot_name}.*\.(jpg|png|webp)', re.I))
            if imgs:
                img_url = imgs[0].get('src')
        
        # Method 3: Look for wp-content uploads images
        if not img_url:
            imgs = soup.find_all('img', src=re.compile(r'wp-content/uploads.*slot.*\.(jpg|png|webp)', re.I))
            if imgs:
                img_url = imgs[0].get('src')
        
        # Method 4: Look for any game-related image in the article
        if not img_url:
            article = soup.find('article') or soup.find('main')
            if article:
                imgs = article.find_all('img', src=re.compile(r'\.(jpg|png|webp)', re.I))
                for img in imgs:
                    src = img.get('src', '')
                    if 'icon' not in src.lower() and 'logo' not in src.lower() and 'avatar' not in src.lower():
                        img_url = src
                        break
        
        if img_url:
            img_response = requests.get(img_url, headers=headers, timeout=30)
            if img_response.status_code == 200 and len(img_response.content) > 5000:
                ext = 'jpg'
                if '.png' in img_url.lower():
                    ext = 'png'
                elif '.webp' in img_url.lower():
                    ext = 'webp'
                filename = slug.replace('-slot', '').replace('-', '_') + '.' + ext
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"  Downloaded: {filename}")
                return filename
        
        print(f"  No image found for {slug}")
        return None
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    output_dir = "public/images"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Fetching Pragmatic Play slots from gamingslots.com...")
    slots = get_pragmatic_slots()
    print(f"Found {len(slots)} Pragmatic Play slots\n")
    
    # Download images
    downloaded = []
    for i, (slug, url) in enumerate(slots.items(), 1):
        print(f"[{i}/{len(slots)}] {slug}")
        filename = download_slot_image(slug, url, output_dir)
        if filename:
            downloaded.append(filename)
        time.sleep(0.3)
    
    print(f"\nDownloaded {len(downloaded)} images")
    
    # Update slot_providers.json
    providers_file = "slot_providers.json"
    if os.path.exists(providers_file):
        with open(providers_file, 'r') as f:
            providers = json.load(f)
    else:
        providers = {}
    
    for filename in downloaded:
        providers[filename] = "Pragmatic Play"
    
    with open(providers_file, 'w') as f:
        json.dump(providers, f, indent=2)
    
    print(f"Updated {providers_file} with {len(downloaded)} Pragmatic Play entries")

if __name__ == "__main__":
    main()
