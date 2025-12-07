#!/usr/bin/env python3
"""
Inspect ELK Studios page structure to understand URLs and image locations
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gamingslots.com/slots/elk-studios/"

print("="*60)
print("Inspecting ELK Studios page structure")
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
    
    all_links = soup.find_all('a', href=re.compile(r'/slots/elk-studios/'))
    print(f"Found {len(all_links)} links containing '/slots/elk-studios/'\n")
    
    # Show unique hrefs
    unique_hrefs = set()
    for link in all_links:
        href = link.get('href')
        if href and href not in unique_hrefs:
            unique_hrefs.add(href)
    
    print(f"Unique URLs: {len(unique_hrefs)}")
    print("\nFirst 10 unique URLs found:")
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
            print(f"Style attribute (first 300 chars): {style[:300]}...")
            
            # Extract URL
            if 'url(' in style:
                start = style.find('url(') + 4
                end = style.find(')', start)
                img_url = style[start:end].strip('\'"')
                print(f"\n✓ Extracted image URL: {img_url}")
        else:
            print("No game frame div found")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
