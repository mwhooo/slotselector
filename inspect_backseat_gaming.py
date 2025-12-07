#!/usr/bin/env python3
"""
Inspect Backseat Gaming page structure to understand URLs and image locations
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gamingslots.com/slots/backseat-gaming/"

print("="*60)
print("Inspecting Backseat Gaming page structure")
print("="*60)
print()

try:
    print(f"Fetching: {url}")
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links that look like slot pages
    print("Looking for slot links...")
    print("-"*60)
    
    all_links = soup.find_all('a', href=re.compile(r'/slots/backseat-gaming/'))
    print(f"Found {len(all_links)} links containing '/slots/backseat-gaming/'\n")
    
    # Show first 10 unique hrefs
    unique_hrefs = set()
    for link in all_links:
        href = link.get('href')
        if href and href not in unique_hrefs:
            unique_hrefs.add(href)
    
    print("First 10 unique URLs found:")
    for i, href in enumerate(sorted(unique_hrefs)[:10], 1):
        print(f"  {i}. {href}")
    
    print("\n" + "="*60)
    print("Now checking one slot page to find image location...")
    print("="*60)
    
    # Find a slot URL to inspect
    slot_url = None
    for href in unique_hrefs:
        if '-slot/' in href and href != url:
            slot_url = href
            break
    
    if slot_url:
        if not slot_url.startswith('http'):
            slot_url = "https://www.gamingslots.com" + slot_url
        
        print(f"\nInspecting: {slot_url}")
        slot_response = requests.get(slot_url, timeout=30)
        print(f"Status: {slot_response.status_code}\n")
        
        slot_soup = BeautifulSoup(slot_response.text, 'html.parser')
        
        # Look for the game frame div with background image
        game_frame = slot_soup.find('div', id='fpgame-frame')
        if game_frame:
            style = game_frame.get('style', '')
            print("Found game frame div!")
            print(f"Style attribute: {style[:200]}...")
            
            # Extract URL
            if 'url(' in style:
                start = style.find('url(') + 4
                end = style.find(')', start)
                img_url = style[start:end].strip('\'"')
                print(f"\nExtracted image URL: {img_url}")
        else:
            print("No game frame div found, looking for images...")
            imgs = slot_soup.find_all('img')
            print(f"Found {len(imgs)} img tags. First 5:")
            for i, img in enumerate(imgs[:5], 1):
                src = img.get('src', 'NO SRC')
                alt = img.get('alt', '')
                print(f"  {i}. src={src[:80]}...")
                print(f"     alt={alt}")
    else:
        print("Could not find a slot URL to inspect")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
