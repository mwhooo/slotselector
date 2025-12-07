import requests
from bs4 import BeautifulSoup
import re

# Test image URL pattern for Relax Gaming
test_slot = "10 Kings"
test_slug = test_slot.lower().replace(' ', '-')

url = f"https://www.gamingslots.com/slots/relax-gaming/{test_slug}-slot/"

print(f"Testing Relax Gaming image pattern for '{test_slot}'...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        # Look for image URLs
        pattern = r'https://www\.gamingslots\.com/wp-content/uploads/[^"]+' + test_slug + r'[^"]*(?:slot-logo|logo)\.(?:jpg|png)'
        matches = re.findall(pattern, response.text, re.IGNORECASE)
        
        if matches:
            print(f"Found {len(matches)} image URLs:")
            for match in matches[:5]:
                print(f"  - {match}")
        else:
            # Try broader pattern
            print("Trying broader pattern...")
            pattern2 = r'https://www\.gamingslots\.com/wp-content/uploads/[^"]+' + test_slug
            matches2 = re.findall(pattern2, response.text, re.IGNORECASE)
            
            if matches2:
                print(f"Found {len(matches2[:5])} potential image URLs:")
                for match in matches2[:5]:
                    print(f"  - {match}")
            else:
                print("No image URLs found with standard patterns")
                
                # Check what's in the page
                print("\nSearching for any image patterns in page...")
                all_images = re.findall(r'https://www\.gamingslots\.com/wp-content/uploads/[^"\s]+', response.text)
                
                if all_images:
                    print(f"Found {len(set(all_images))} unique image URLs total")
                    # Filter for ones that look like logos
                    logos = [img for img in all_images if 'logo' in img.lower() or 'slot' in img.lower()]
                    if logos:
                        print("\nPotential logo images:")
                        for logo in logos[:5]:
                            print(f"  - {logo}")
    else:
        print(f"Error: Status code {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
