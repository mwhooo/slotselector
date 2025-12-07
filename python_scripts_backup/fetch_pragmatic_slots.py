import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.request
from PIL import Image
from io import BytesIO
import os

# Fetch Pragmatic Play slots page
print("Fetching Pragmatic Play slots from gamingslots.com...")

url = "https://www.gamingslots.com/slots/pragmatic-play/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all slot links and titles
    slots = {}
    slot_urls = {}
    
    # Look for slot game links
    for link in soup.find_all('a', href=re.compile(r'/slots/pragmatic-play/')):
        href = link.get('href')
        # Skip the main provider page
        if href == 'https://www.gamingslots.com/slots/pragmatic-play/':
            continue
        
        # Get slot name from link text and clean it
        slot_name = link.get_text(strip=True)
        # Remove "Pragmatic Play" prefix if present
        slot_name = slot_name.replace('Pragmatic Play', '').strip()
        
        if slot_name and slot_name not in slots:
            slots[slot_name] = "Pragmatic Play"
            slot_urls[slot_name] = href
    
    print(f"Found {len(slots)} Pragmatic Play slots")
    
    if slots:
        # Save slot providers
        with open('slot_providers.json', 'w', encoding='utf-8') as f:
            json.dump(slots, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(slots)} slots to slot_providers.json")
        
        # Print first 20 slots found
        print("\nFirst 20 slots found:")
        for i, (name, provider) in enumerate(list(slots.items())[:20], 1):
            print(f"  {i}. {name}")
    else:
        print("No slots found. Website structure may have changed.")
        
except Exception as e:
    print(f"Error: {str(e)}")
