"""
Inspect NoLimit City slots page structure
"""
import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.gamingslots.com/slots/nolimitcity/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=" * 60)
print("Inspecting NoLimit City slots page")
print("=" * 60)

response = requests.get(URL, headers=HEADERS, timeout=30)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to individual slot pages
slot_links = soup.find_all('a', href=re.compile(r'/slots/nolimitcity/[^/]+-slot/?$'))
print(f"\nFound {len(slot_links)} slot links")

# Get unique URLs
unique_urls = set()
for link in slot_links:
    unique_urls.add(link['href'])

print(f"Unique slot URLs: {len(unique_urls)}")
print("\nFirst 10 slots:")
for i, url in enumerate(sorted(unique_urls)[:10], 1):
    # Extract slot name from URL
    name = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    name = name.replace('-slot', '').replace('-', ' ').title()
    print(f"  {i}. {name}")

# Check if there's pagination
pagination = soup.find_all('a', class_=re.compile(r'page'))
nav_links = soup.find_all('a', href=re.compile(r'page/\d+'))
print(f"\nPagination links found: {len(nav_links)}")

# Look for any element that might indicate total count
all_text = soup.get_text()
count_match = re.search(r'(\d+)\s*slots?', all_text, re.IGNORECASE)
if count_match:
    print(f"Possible total count mentioned: {count_match.group(0)}")

# Print all URLs for reference
print("\n" + "=" * 60)
print("All unique slot URLs:")
print("=" * 60)
for url in sorted(unique_urls):
    print(url)
