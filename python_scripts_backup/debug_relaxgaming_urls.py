import requests
from bs4 import BeautifulSoup
import re

# Test a few slots to see the actual image URL pattern
test_slots = ["Epic Dreams", "Amped", "Aztec Ascent", "10 Kings"]

for test_slot in test_slots:
    slug = test_slot.lower().replace(' ', '-')
    url = f"https://www.gamingslots.com/slots/relax-gaming/{slug}-slot/"
    
    print(f"\nTesting: {test_slot} ({slug})")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Find all image URLs in the page
            images = re.findall(r'https://www\.gamingslots\.com/wp-content/uploads/[^"]+\.(?:jpg|png)', response.text)
            
            if images:
                print(f"Found {len(set(images))} unique images:")
                for img in list(set(images))[:3]:
                    print(f"  - {img}")
            else:
                print("No images found")
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
