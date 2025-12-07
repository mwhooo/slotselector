import urllib.request
import re

slots_to_test = ["Anaconda Gold", "Ancient Egypt", "Bee Keeper"]

for slot_name in slots_to_test:
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        print(f"\nTesting: {slot_name}")
        print(f"Slug: {slug}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        # Look for the pattern
        pattern = rf'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*{re.escape(slug)}-slot-logo\.jpg'
        match = re.search(pattern, content)
        
        if match:
            print(f"✓ Found: {match.group(0).split('/')[-1]}")
        else:
            print(f"✗ Pattern not found")
            
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")
