#!/usr/bin/env python3
"""
Scrape Inspired Gaming slots from gamingslots.com
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from pathlib import Path

url = "https://www.gamingslots.com/slots/inspired-gaming/"
images_dir = Path("public/images")
images_dir.mkdir(exist_ok=True)

TIMEOUT = 45
PAUSE_EVERY = 3
PAUSE_SECONDS = 1.5

print("="*60)
print("Scraping Inspired Gaming slots from gamingslots.com")
print("="*60)
print()

try:
    print("1. Fetching slots list page...")
    response = requests.get(url, timeout=TIMEOUT)
    
    if response.status_code != 200:
        print(f"   ERROR: Status {response.status_code}")
        exit(1)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all slot links
    slot_links = soup.find_all('a', href=re.compile(r'/slots/inspired-gaming/[^/]+-slot/'))
    
    # Get unique URLs
    unique_urls = set()
    for link in slot_links:
        href = link.get('href')
        if href and '-slot/' in href:
            if not href.startswith('http'):
                href = "https://www.gamingslots.com" + href
            unique_urls.add(href)
    
    print(f"   ✓ Found {len(unique_urls)} unique slot URLs\n")
    
    slots = []
    downloaded = 0
    failed = 0
    
    for i, slot_url in enumerate(sorted(unique_urls), 1):
        match = re.search(r'/slots/inspired-gaming/([^/]+)-slot/', slot_url)
        if not match:
            continue
        
        slug = match.group(1)
        name = slug.replace('-', ' ').title()
        
        print(f"[{i}/{len(unique_urls)}] {name}...", end=" ", flush=True)
        
        try:
            slot_response = requests.get(slot_url, timeout=TIMEOUT)
            if slot_response.status_code != 200:
                print(f"❌ HTTP {slot_response.status_code}")
                failed += 1
                continue
            
            slot_soup = BeautifulSoup(slot_response.text, 'html.parser')
            
            img_url = None
            game_frame = slot_soup.find('div', id='fpgame-frame')
            
            if game_frame:
                style = game_frame.get('style', '')
                if 'url(' in style:
                    start = style.find('url(') + 4
                    end = style.find(')', start)
                    if end > start:
                        img_url = style[start:end].strip('\'"')
            
            if not img_url:
                img_tag = slot_soup.find('img', class_=lambda x: x and 'gamethumb' in x)
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
            
            if not img_url:
                print("❌ No image found")
                failed += 1
                continue
            
            img_response = requests.get(img_url, timeout=TIMEOUT)
            if img_response.status_code != 200:
                print("❌ Image download failed")
                failed += 1
                continue
            
            content_type = img_response.headers.get('content-type', '').lower()
            if 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'
            
            filename = f"inspiredgaming-{slug}{ext}"
            filepath = images_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            slots.append(name)
            downloaded += 1
            print(f"✓ {filename}")
            
            if i % PAUSE_EVERY == 0:
                print(f"      ... pausing {PAUSE_SECONDS}s ...")
                time.sleep(PAUSE_SECONDS)
                
        except requests.exceptions.Timeout:
            print("❌ Timeout")
            failed += 1
            time.sleep(2)
            continue
        except Exception as e:
            print(f"❌ {type(e).__name__}")
            failed += 1
            continue
    
    print()
    print("="*60)
    print(f"Downloaded: {downloaded}/{len(unique_urls)}")
    print(f"Failed: {failed}")
    print("="*60)
    
    with open('inspired_gaming_slots.json', 'w') as f:
        json.dump(slots, f, indent=2)
    
    print(f"\n✓ Saved {len(slots)} slots to inspired_gaming_slots.json")

except Exception as e:
    print(f"\nFATAL ERROR: {type(e).__name__}: {e}")
    exit(1)
