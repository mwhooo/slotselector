import urllib.request
import re

# Test one of the missing ones
slot_name = "777 Rush"
slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
slug = re.sub(r'[^a-z0-9-]', '', slug)

url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
print(f"Testing: {slot_name}")
print(f"URL: {url}\n")

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        content = response.read().decode('utf-8', errors='ignore')
    
    # Look for slot-specific logo
    pattern = rf'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*{re.escape(slug)}-slot-logo\.jpg'
    match = re.search(pattern, content)
    
    if match:
        print(f"Found: {match.group(0)}")
    else:
        print("Pattern not found. Looking for alternatives...\n")
        # Show all jpg URLs
        pattern = r'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*\.jpg'
        matches = re.findall(pattern, content)
        matches = list(dict.fromkeys(matches))[:10]  # Unique, first 10
        for url in matches:
            filename = url.split('/')[-1]
            print(f"  {filename}")
            
except Exception as e:
    print(f"Error: {e}")
