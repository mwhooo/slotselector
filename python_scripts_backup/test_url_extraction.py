import urllib.request
import re

slot_name = "3 Dancing Monkeys"
slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
slug = re.sub(r'[^a-z0-9-]', '', slug)

url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
print(f"Fetching: {url}\n")

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        content = response.read().decode('utf-8', errors='ignore')
    
    # Find all image URLs
    pattern = r'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*\.(?:jpg|png|webp)'
    matches = re.findall(pattern, content)
    
    print(f"Found {len(matches)} image URLs:\n")
    
    # Show unique URLs
    seen = set()
    for url in matches:
        if url not in seen:
            seen.add(url)
            # Show only the filename part for clarity
            filename = url.split('/')[-1]
            print(f"  {filename}")
            print(f"    Full: {url}\n")
            if len(seen) >= 5:
                break
                
except Exception as e:
    print(f"Error: {e}")
