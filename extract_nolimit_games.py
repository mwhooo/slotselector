"""
Extract all games from NoLimit City official website
"""
import requests
from bs4 import BeautifulSoup
import json

URL = "https://nolimitcity.com/games/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 60)
print("Extracting NoLimit City games from official website")
print("=" * 60)

response = requests.get(URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Get Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    
    # Navigate to find games
    page_props = data.get('props', {}).get('pageProps', {})
    
    print(f"\nPage props keys: {page_props.keys()}")
    
    # Check for games array
    games = page_props.get('games', [])
    print(f"\n'games' array: {len(games)} items")
    
    # Check latestGame structure
    latest = page_props.get('latestGame', {})
    if latest:
        print(f"\nLatest game structure:")
        for k, v in latest.items():
            if not isinstance(v, (dict, list)):
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: <{type(v).__name__}>")
    
    # Look for all games in any nested structure
    def find_all_games(obj, games_found=[]):
        if isinstance(obj, dict):
            if 'name' in obj and ('releaseDate' in obj or 'id' in obj):
                games_found.append(obj)
            for v in obj.values():
                find_all_games(v, games_found)
        elif isinstance(obj, list):
            for item in obj:
                find_all_games(item, games_found)
        return games_found
    
    all_games = find_all_games(data, [])
    print(f"\nAll game-like objects found: {len(all_games)}")
    
    # Remove duplicates by name
    unique_games = {}
    for g in all_games:
        name = g.get('name')
        if name and name not in unique_games:
            unique_games[name] = g
    
    print(f"Unique games: {len(unique_games)}")
    print("\nFirst 20 games:")
    for i, (name, game) in enumerate(sorted(unique_games.items())[:20], 1):
        release = game.get('releaseDate', 'N/A')[:10] if game.get('releaseDate') else 'N/A'
        print(f"  {i}. {name} ({release})")
    
    # Save all game names
    with open('nolimit_games_official.json', 'w') as f:
        json.dump(list(unique_games.keys()), f, indent=2)
    print(f"\nSaved {len(unique_games)} game names to nolimit_games_official.json")
    
else:
    print("No Next.js data found!")
