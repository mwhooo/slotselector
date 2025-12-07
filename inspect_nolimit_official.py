"""
Inspect NoLimit City official website for full game list
"""
import requests
from bs4 import BeautifulSoup
import re
import json

# Try the official games page
URL = "https://nolimitcity.com/games/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 60)
print("Inspecting NoLimit City official website")
print("=" * 60)

response = requests.get(URL, headers=HEADERS, timeout=30)
print(f"Status: {response.status_code}")
print(f"URL after redirect: {response.url}")

# Check content length
print(f"Content length: {len(response.text)} chars")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for any game-related elements
print("\n--- Looking for game elements ---")

# Check for JSON data in script tags
scripts = soup.find_all('script')
for script in scripts:
    text = script.string or ''
    if 'game' in text.lower() and len(text) > 100:
        print(f"Found script with 'game': {text[:200]}...")

# Check for Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    print("\nFound Next.js data!")
    try:
        data = json.loads(next_data.string)
        print(f"Keys: {data.keys()}")
        # Look for games
        def find_games(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if 'game' in k.lower():
                        print(f"  Found '{k}' at {path}")
                        if isinstance(v, list):
                            print(f"    List of {len(v)} items")
                    find_games(v, f"{path}.{k}")
            elif isinstance(obj, list) and len(obj) > 0:
                find_games(obj[0], f"{path}[0]")
        find_games(data)
    except Exception as e:
        print(f"Error parsing: {e}")

# Look for any API endpoints
api_patterns = re.findall(r'(https?://[^"\']+api[^"\']*)', response.text, re.IGNORECASE)
print(f"\nAPI patterns found: {len(set(api_patterns))}")
for api in set(api_patterns)[:5]:
    print(f"  {api}")

# Check for image URLs that might indicate game names
img_urls = re.findall(r'https?://[^"\']+\.(png|jpg|webp)', response.text)
print(f"\nImage URLs found: {len(img_urls)}")
for img in img_urls[:5]:
    print(f"  {img}")
