import json
import os
import requests
from bs4 import BeautifulSoup
import time

# Load providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get missing slots
missing = []
for slot_name in providers.keys():
    image_path = f"public/images/{slot_name}.jpg"
    if not os.path.exists(image_path):
        missing.append(slot_name)

print(f"Testing {len(missing)} missing slots for page existence...\n")

found_pages = []
no_pages = []

for i, slot_name in enumerate(missing[:20], 1):  # Test first 20
    slug = slot_name.lower()
    slug = slug.replace("'", "").replace("â€™", "")  # Remove apostrophes
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split())
    
    url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            found_pages.append((slot_name, url))
            print(f"[{i:2}] ✓ {slot_name}")
        else:
            no_pages.append((slot_name, resp.status_code))
            print(f"[{i:2}] ✗ {slot_name} ({resp.status_code})")
        time.sleep(0.1)
    except Exception as e:
        no_pages.append((slot_name, str(e)))
        print(f"[{i:2}] ✗ {slot_name} ({type(e).__name__})")

print(f"\nFound pages: {len(found_pages)}")
print(f"No pages: {len(no_pages)}")
