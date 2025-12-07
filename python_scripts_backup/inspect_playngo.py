#!/usr/bin/env python3
"""
Inspect gamingslots.com Play'n GO page structure
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.gamingslots.com/slots/playngo/"
print(f"Fetching {url}...")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print all links with 'slot' or 'game' in class
    print("\n=== Links with relevant classes ===")
    for link in soup.find_all('a')[:20]:
        classes = link.get('class', [])
        text = link.get_text(strip=True)[:50]
        href = link.get('href', '')
        if any(x in str(classes).lower() for x in ['slot', 'game', 'play']) or 'slots' in href:
            print(f"Classes: {classes}, Text: {text}, Href: {href[:80]}")
    
    # Print all divs with 'game' or 'slot'
    print("\n=== Divs with game/slot classes ===")
    for div in soup.find_all('div', class_=lambda x: x and any(w in x.lower() for w in ['game', 'slot'])):
        print(f"Class: {div.get('class')}")
    
    # Check entire page structure
    print("\n=== Full HTML (first 3000 chars) ===")
    print(response.text[:3000])
    
except Exception as e:
    print(f"Error: {e}")
