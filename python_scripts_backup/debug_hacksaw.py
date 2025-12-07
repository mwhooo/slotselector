import requests
from bs4 import BeautifulSoup
import re

slot_name = "Army Of Ares"
slug = slot_name.lower()
slug = slug.replace("'", "")
slug = ''.join(c if c.isalnum() else '-' for c in slug)
slug = '-'.join(slug.split())

url = f"https://www.gamingslots.com/slots/hacksaw-gaming/{slug}-slot/"
print(f"Testing: {url}\n")

resp = requests.get(url, timeout=10)
print(f"Status: {resp.status_code}\n")

if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Find all image URLs
    img_tags = soup.find_all('img')
    print(f"Found {len(img_tags)} image tags\n")
    
    # Look for JPG/PNG sources with gamingslots.com
    jpg_urls = []
    for img in img_tags:
        src = img.get('src', '')
        if '.jpg' in src.lower() or '.png' in src.lower():
            if 'gamingslots' in src.lower():
                jpg_urls.append(src)
    
    print(f"Found {len(jpg_urls)} image URLs from gamingslots.com:")
    for i, url in enumerate(jpg_urls[:10], 1):
        # Show last 80 chars
        display = url[-80:] if len(url) > 80 else url
        print(f"  {i}. {display}")
