import requests
from bs4 import BeautifulSoup
import re

# Test a real Play'n'GO slot from the list
slot_name = "Agent Destiny"
slug = "agent-destiny"  # Use the slug from gamingslots.com

url = f"https://www.gamingslots.com/slots/playn-go/{slug}-slot/"
print(f"Testing: {slot_name}")
print(f"URL: {url}\n")

resp = requests.get(url, timeout=10)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    # Find all image URLs
    soup = BeautifulSoup(resp.content, 'html.parser')
    img_tags = soup.find_all('img')
    
    # Look for gamingslots image URLs
    jpg_urls = []
    for img in img_tags:
        src = img.get('src', '')
        if ('jpg' in src.lower() or 'png' in src.lower()) and 'gamingslots' in src.lower():
            jpg_urls.append(src)
    
    print(f"Found {len(jpg_urls)} image URLs\n")
    print("Image URLs:")
    for i, url in enumerate(jpg_urls[:8], 1):
        # Show last 80 chars
        display = url[-80:] if len(url) > 80 else url
        print(f"  {i}. {display}")
else:
    print(f"Page not found or error")
