"""
Inspect gamingslots.com Playson page to see what's available
"""
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.gamingslots.com/slots/playson/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 60)
print("Checking gamingslots.com for Playson slots")
print("=" * 60)

response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Status: {response.status_code}")

# Find all slot page links for playson
slot_links = soup.find_all('a', href=re.compile(r'/slots/playson/[^/]+-slot/?$'))
unique_urls = set()
for link in slot_links:
    unique_urls.add(link['href'])

print(f"\nFound {len(unique_urls)} Playson slot URLs on gamingslots.com")

if unique_urls:
    print("\nSlots available:")
    for i, url in enumerate(sorted(unique_urls), 1):
        name = url.rstrip('/').split('/')[-1].replace('-slot', '').replace('-', ' ').title()
        print(f"  {i}. {name}")
else:
    print("\nNo Playson slots found on gamingslots.com!")
    print("This provider might not be available there.")
