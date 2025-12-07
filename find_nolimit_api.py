"""
Find and use NoLimit City API
"""
import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Try common API patterns
apis_to_try = [
    "https://nolimitcity.com/api/games",
    "https://api.nolimitcity.com/games",
    "https://playin.com/api/games",
    "https://playin.com/api/games?studios=nolimitcity",
    "https://nolimitcity.com/_next/data/",
]

print("=" * 60)
print("Trying to find NoLimit City API")
print("=" * 60)

for api in apis_to_try:
    try:
        print(f"\nTrying: {api}")
        resp = requests.get(api, headers=HEADERS, timeout=10)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            content = resp.text[:500]
            print(f"  Content preview: {content[:200]}...")
    except Exception as e:
        print(f"  Error: {e}")

# Try playin.com which seems to be their game portal
print("\n" + "=" * 60)
print("Checking playin.com games page")
print("=" * 60)

from bs4 import BeautifulSoup

resp = requests.get("https://playin.com/games", headers=HEADERS, timeout=30)
print(f"Status: {resp.status_code}")
soup = BeautifulSoup(resp.text, 'html.parser')

# Check for Next.js data
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    page_props = data.get('props', {}).get('pageProps', {})
    print(f"Page props keys: {list(page_props.keys())}")
    
    games = page_props.get('games', [])
    if games:
        print(f"Found {len(games)} games!")
        print("\nFirst 5:")
        for g in games[:5]:
            print(f"  - {g.get('name', 'N/A')}")
