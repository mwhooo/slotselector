#!/usr/bin/env python3
"""
Test scraping Pragmatic Play games from onlineslotcentral.com
Start small - get just 5 games and their images to understand the structure
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://onlineslotcentral.com/free-slots/?sl-provider=pragmatic-play"

print("Fetching Pragmatic Play games from onlineslotcentral.com...")

response = requests.get(url, timeout=20)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find game links - they appear to be in divs with game info
    # Looking for the pattern: /games/{slug}/
    game_links = soup.find_all('a', href=re.compile(r'^/games/[^/]+/$'))
    
    print(f"Found {len(game_links)} game links\n")
    
    # Extract unique games (first 10)
    games = {}
    for link in game_links[:10]:
        href = link.get('href')
        game_name = link.text.strip()
        if game_name and href:
            games[game_name] = href
    
    print("Games found:")
    for name, href in games.items():
        print(f"  {name}: {href}")
        
    print(f"\nNow checking individual game pages for images...")
    
    # Check first game's page
    if games:
        first_game = list(games.values())[0]
        game_url = "https://onlineslotcentral.com" + first_game
        print(f"\nFetching: {game_url}")
        
        game_response = requests.get(game_url, timeout=20)
        game_soup = BeautifulSoup(game_response.text, 'html.parser')
        
        # Look for images
        images = game_soup.find_all('img')
        print(f"Found {len(images)} images on page")
        
        # Print image URLs
        for img in images[:5]:
            src = img.get('src') or img.get('data-src')
            alt = img.get('alt')
            if src:
                print(f"  {alt}: {src}")
else:
    print(f"Error: Status {response.status_code}")
