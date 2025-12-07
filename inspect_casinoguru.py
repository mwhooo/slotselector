"""
Inspect casino.guru Playson page structure
"""
import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://casino.guru/free-casino-games/slots/playson"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

print("=" * 60)
print("Inspecting casino.guru Playson page")
print("=" * 60)

response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for game links
game_links = soup.find_all('a', href=re.compile(r'slot-play-free'))
print(f"\nFound {len(game_links)} slot links")

# Extract unique game URLs and names
unique_games = {}
for link in game_links:
    href = link.get('href', '')
    if href and 'slot-play-free' in href:
        # Extract game name from link text or href
        text = link.get_text(strip=True)
        if text and 'by Playson' in text:
            name = text.replace(' by Playson', '').strip()
            unique_games[href] = name
        elif text and len(text) > 2:
            unique_games[href] = text

print(f"Unique games: {len(unique_games)}")

print("\nFirst 20 games:")
for i, (url, name) in enumerate(list(unique_games.items())[:20], 1):
    print(f"  {i}. {name}")
    print(f"      {url}")

# Check for image URLs
images = soup.find_all('img')
game_images = [img for img in images if img.get('src') and 'static.casino.guru' in img.get('src', '')]
print(f"\nFound {len(game_images)} casino.guru images")

# Look for data attributes
cards = soup.find_all(['div', 'a'], class_=re.compile(r'game|card|slot', re.I))
print(f"\nFound {len(cards)} game-related elements")

# Check pagination
pagination = soup.find_all('a', href=re.compile(r'/slots/\d+'))
print(f"Pagination links: {len(pagination)}")
for p in pagination[:5]:
    print(f"  {p.get('href')}")
