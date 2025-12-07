#!/usr/bin/env python3
"""
Test scraping: Get first 10 Pragmatic Play slots and their image URLs
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gamingslots.com/slots/pragmatic-play/"

print("Fetching Pragmatic Play page...")
response = requests.get(url, timeout=30)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# Find all slot links
slot_links = soup.find_all('a', href=re.compile(r'/slots/pragmatic-play/[^/]+-slot/'))

print(f"Found {len(slot_links)} slot links\n")

# Extract first 10
slots = []
for link in slot_links[:10]:
    href = link.get('href')
    match = re.search(r'/slots/pragmatic-play/([^/]+)-slot/', href)
    if match:
        slug = match.group(1)
        name = slug.replace('-', ' ').title()
        slots.append({'name': name, 'slug': slug, 'url': href})

print("First 10 slots:")
for i, slot in enumerate(slots, 1):
    print(f"\n{i}. {slot['name']}")
    print(f"   Slug: {slot['slug']}")
    print(f"   URL: https://www.gamingslots.com{slot['url']}")
    print(f"   Image URL: https://www.gamingslots.com/images/slots/pragmatic-play/{slot['slug']}-slot-logo.jpg")
