import urllib.request
import re

slot_name = "Anaconda Gold"
slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
slug = re.sub(r'[^a-z0-9-]', '', slug)

url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        content = response.read().decode('utf-8', errors='ignore')
    
    # Find all jpg files
    pattern = r'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*\.jpg'
    matches = re.findall(pattern, content)
    matches = list(dict.fromkeys(matches))  # Remove duplicates
    
    print(f"Found {len(matches)} JPG URLs for {slot_name}\n")
    print("Image URLs (excluding site logos):\n")
    
    for match in matches:
        filename = match.split('/')[-1]
        if not any(x in filename for x in ['icon-logo', 'cropped', 'GS-logo']):
            print(f"  {filename}")
    
except urllib.error.HTTPError as e:
    print(f"Page not found: {e.code}")
except Exception as e:
    print(f"Error: {e}")
