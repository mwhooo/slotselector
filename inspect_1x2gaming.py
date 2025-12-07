#!/usr/bin/env python3
"""
Inspect the HTML structure of a 1x2gaming slot page to find image locations
"""

import requests
from bs4 import BeautifulSoup
import json

# Load slot names
with open('1x2gaming_slots.json', 'r') as f:
    slots = json.load(f)

base_url = "https://www.gamingslots.com/slots/1x2gaming/"

# Test with the first slot
slot_name = slots[0]
slug = slot_name.lower().replace(' ', '-')
slot_url = f"{base_url}{slug}-slot/"

print(f"Inspecting: {slot_name}")
print(f"URL: {slot_url}")
print("="*60)

try:
    response = requests.get(slot_url, timeout=10)
    print(f"Status: {response.status_code}\n")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all img tags and print them
    print("All <img> tags found:")
    print("-"*60)
    imgs = soup.find_all('img')
    for i, img in enumerate(imgs[:10], 1):  # Show first 10
        src = img.get('src', 'NO SRC')
        alt = img.get('alt', 'NO ALT')
        classes = img.get('class', [])
        print(f"\n[{i}] <img src=\"{src}\"")
        print(f"    alt=\"{alt}\"")
        print(f"    class=\"{' '.join(classes)}\"")
    
    print("\n" + "="*60)
    print("\nSearching for common image patterns...")
    
    # Look for picture tags
    pictures = soup.find_all('picture')
    print(f"Found {len(pictures)} <picture> tags")
    
    # Look for divs with background images
    divs_with_bg = soup.find_all('div', style=lambda x: x and 'background' in x.lower())
    print(f"Found {len(divs_with_bg)} <div> tags with background styles")
    
    # Look for specific class patterns
    for class_pattern in ['slot-image', 'game-image', 'thumbnail', 'screenshot', 'preview']:
        elements = soup.find_all(class_=class_pattern)
        if elements:
            print(f"Found {len(elements)} elements with class '{class_pattern}'")
    
    # Print the full HTML of a potential image container
    print("\n" + "="*60)
    print("Looking for game/slot content sections...\n")
    
    # Try to find the main slot content area
    for tag_name in ['article', 'main', 'section']:
        content = soup.find(tag_name)
        if content:
            print(f"Found <{tag_name}> tag")
            # Print first 1000 chars
            print(str(content)[:1000])
            break

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
