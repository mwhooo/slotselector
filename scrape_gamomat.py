#!/usr/bin/env python3
"""
Scrape Gamomat slots from gamingslots.com
- Show progress for each slot
- Small pause between requests (avoid hammering server)
- Stop if error rate gets too high
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

url = "https://www.gamingslots.com/slots/gamomat/"

print("="*60)
print("Scraping Gamomat slots from gamingslots.com")
print("="*60)
print()

try:
    print("1. Fetching slots list page...")
    response = requests.get(url, timeout=30)
    
    if response.status_code != 200:
        print(f"   ERROR: Status {response.status_code}")
        exit(1)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all slot links
    slot_links = soup.find_all('a', href=re.compile(r'/slots/gamomat/[^/]+-slot/'))
    print(f"   ✓ Found {len(slot_links)} slot links\n")
    
    # Extract slots
    slots = {}
    errors = 0
    success = 0
    
    for i, link in enumerate(slot_links, 1):
        href = link.get('href')
        match = re.search(r'/slots/gamomat/([^/]+)-slot/', href)
        
        if match:
            slug = match.group(1)
            name = slug.replace('-', ' ').title()
            slots[name] = slug
            
            print(f"[{i}/{len(slot_links)}] {name}")
            
            # Small pause to avoid hammering server
            if i % 5 == 0:
                print(f"      ... pausing briefly ...")
                time.sleep(0.5)
        else:
            errors += 1
            print(f"[{i}] ERROR: Could not parse link")
            if errors > 10:
                print(f"\n   Too many errors ({errors}). Quitting.")
                break
        
        success += 1
    
    print()
    print("="*60)
    print(f"Total slots found: {len(slots)}")
    print(f"Success: {success}, Errors: {errors}")
    print("="*60)
    
    # Save to JSON file
    with open('gamomat_slots.json', 'w') as f:
        json.dump(list(slots.keys()), f, indent=2)
    
    print(f"\n✓ Saved {len(slots)} slots to gamomat_slots.json")

except Exception as e:
    print(f"\nFATAL ERROR: {type(e).__name__}: {e}")
    exit(1)
