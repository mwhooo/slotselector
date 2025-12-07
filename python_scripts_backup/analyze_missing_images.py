import json
import requests
from bs4 import BeautifulSoup
import re
import time

# Load providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get missing slots
missing = []
for slot_name in providers.keys():
    import os
    image_path = f"public/images/{slot_name}.jpg"
    if not os.path.exists(image_path):
        missing.append(slot_name)

print(f"Analyzing image URLs on missing slot pages...\n")

# Check first 5 missing
for slot_name in missing[:5]:
    slug = slot_name.lower()
    slug = slug.replace("'", "").replace("â€™", "")
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split())
    
    url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Find all image sources
            img_tags = soup.find_all('img')
            jpg_urls = []
            
            for img in img_tags:
                src = img.get('src', '')
                if '.jpg' in src.lower() or '.png' in src.lower():
                    # Get full URL if relative
                    if src.startswith('/'):
                        src = 'https://www.gamingslots.com' + src
                    if src.startswith('http'):
                        jpg_urls.append(src)
            
            print(f"\n{slot_name}:")
            print(f"  URL: {url}")
            print(f"  Found {len(jpg_urls)} image URLs")
            
            # Show first 3 unique URLs
            unique = set(jpg_urls)
            for i, img_url in enumerate(list(unique)[:3], 1):
                # Shorten for display
                display = img_url.replace('https://www.gamingslots.com/wp-content/uploads/', '')
                print(f"    {i}. .../{display[-60:]}")
        
        time.sleep(0.2)
    except Exception as e:
        print(f"\n{slot_name}: ERROR - {e}")
