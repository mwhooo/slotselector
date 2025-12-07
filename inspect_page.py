#!/usr/bin/env python3
"""
Inspect the actual page to find where images are
"""

import requests
from bs4 import BeautifulSoup

slot_url = "https://www.gamingslots.com/slots/pragmatic-play/3-buzzing-wilds-slot/"

print(f"Fetching: {slot_url}\n")
response = requests.get(slot_url, timeout=30)

soup = BeautifulSoup(response.text, 'html.parser')

# Look for img tags
images = soup.find_all('img')
print(f"Found {len(images)} img tags\n")

# Show first 5
for i, img in enumerate(images[:5]):
    src = img.get('src', 'NO SRC')
    alt = img.get('alt', '')
    print(f"{i+1}. src={src}")
    print(f"   alt={alt}\n")

# Look for common image patterns
print("\nLooking for logo/image tags:")
for img in images:
    src = img.get('src', '')
    if 'logo' in src.lower() or 'slot' in src.lower() or src.endswith(('.jpg', '.png')):
        print(f"  {src}")
