import requests
from bs4 import BeautifulSoup
import re
import json

# Load Relax Gaming slots
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

relaxgaming_slots = [name for name, provider in providers.items() if provider == 'Relax Gaming']

# Check which ones don't have images
import os
missing_images = []
for slot in relaxgaming_slots:
    if not os.path.exists(f"public/images/{slot}.jpg"):
        missing_images.append(slot)

print(f"Total Relax Gaming slots: {len(relaxgaming_slots)}")
print(f"Missing images: {len(missing_images)}")
print(f"\nTesting first 10 missing slots for image patterns:\n")

# Test first 10 missing
for test_slot in missing_images[:10]:
    slug = test_slot.lower()
    slug = slug.replace("'", "").replace("â€™", "")
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split())
    
    url = f"https://www.gamingslots.com/slots/relax-gaming/{slug}-slot/"
    
    print(f"Testing: {test_slot}")
    print(f"  Slug: {slug}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Find all image URLs with the slug in them
            pattern = f'https://www\.gamingslots\.com/wp-content/uploads/[^"]*{re.escape(slug)}[^"]*\.(?:jpg|png|webp)'
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            
            if matches:
                print(f"  ✓ Found {len(set(matches))} image(s):")
                for match in list(set(matches))[:2]:
                    print(f"    - {match}")
            else:
                # Try to find ANY image on the page
                all_images = re.findall(r'https://www\.gamingslots\.com/wp-content/uploads/[^"]+\.(?:jpg|png|webp)', response.text, re.IGNORECASE)
                
                if all_images:
                    # Filter for slot-related images
                    slot_images = [img for img in all_images if 'slot' in img.lower() or 'logo' in img.lower()]
                    
                    if slot_images:
                        unique = list(set(slot_images))
                        print(f"  ~ Found {len(unique)} potential slot/logo image(s):")
                        for img in unique[:2]:
                            print(f"    - {img}")
                    else:
                        print(f"  ✗ No slot/logo images found (found {len(set(all_images))} other images)")
                else:
                    print(f"  ✗ No images found on page")
        else:
            print(f"  ✗ Page not found (status {response.status_code})")
            
            # Try variations
            print(f"    Trying alternate URLs...")
            alt_slugs = [
                slug.replace('-', ''),  # No dashes
                slug.split('-')[0],      # First word only
            ]
            for alt_slug in alt_slugs:
                alt_url = f"https://www.gamingslots.com/slots/relax-gaming/{alt_slug}-slot/"
                alt_resp = requests.get(alt_url, timeout=5)
                if alt_resp.status_code == 200:
                    print(f"      ✓ Found alternate: {alt_slug}")
                    break
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
