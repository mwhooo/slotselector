#!/usr/bin/env python3
"""
Inspect Kalamba Games page structure first
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gamingslots.com/slots/kalamba-games/"

print("="*60)
print("Inspecting Kalamba Games page structure")
print("="*60)
print()

try:
    print(f"Fetching: {url}")
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all slot links
    all_links = soup.find_all('a', href=re.compile(r'/slots/kalamba-games/'))
    
    unique_hrefs = set()
    for link in all_links:
        href = link.get('href')
        if href and '-slot/' in href:
            unique_hrefs.add(href)
    
    print(f"Found {len(unique_hrefs)} unique slot URLs\n")
    print("First 5 URLs:")
    for i, href in enumerate(sorted(unique_hrefs)[:5], 1):
        print(f"  {i}. {href}")
    
    # Check one slot page
    slot_url = sorted(unique_hrefs)[0] if unique_hrefs else None
    if slot_url:
        if not slot_url.startswith('http'):
            slot_url = "https://www.gamingslots.com" + slot_url
        
        print(f"\nChecking: {slot_url}")
        slot_response = requests.get(slot_url, timeout=30)
        slot_soup = BeautifulSoup(slot_response.text, 'html.parser')
        
        game_frame = slot_soup.find('div', id='fpgame-frame')
        if game_frame:
            style = game_frame.get('style', '')
            if 'url(' in style:
                start = style.find('url(') + 4
                end = style.find(')', start)
                img_url = style[start:end].strip('\'"')
                print(f"✓ Image URL found: {img_url[:80]}...")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
