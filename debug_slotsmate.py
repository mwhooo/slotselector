"""
Debug: inspect slotsmate page structure
"""
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.slotsmate.com/software/nolimit-city"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")

# Look for any links
all_links = soup.find_all('a', href=True)
print(f"\nTotal links: {len(all_links)}")

# Find nolimit city related links
nlc_links = [a for a in all_links if 'nolimit' in a.get('href', '').lower()]
print(f"Links with 'nolimit': {len(nlc_links)}")

for link in nlc_links[:20]:
    print(f"  {link.get('href')}")

# Look for game names in text
game_names = re.findall(r'Dead Men Walking|Mental|Tombstone|San Quentin|Fire in the Hole', response.text)
print(f"\nKnown game names found: {len(game_names)}")
for name in set(game_names):
    print(f"  - {name}")

# Check for script tags with game data
scripts = soup.find_all('script')
for script in scripts:
    text = script.string or ''
    if 'nolimit' in text.lower() and len(text) > 50:
        print(f"\nScript with nolimit mention: {text[:300]}...")
