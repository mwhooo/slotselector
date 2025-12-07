import requests
import re

# Check if playn-go provider exists on gamingslots.com
url = "https://www.gamingslots.com/slots/playn-go/"
resp = requests.get(url, timeout=10)

print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    # Find all playn-go slot links
    matches = re.findall(r'/slots/playn-go/([^/\s"\']+)(?:-slot)?/?', resp.text)
    unique = sorted(set(matches))
    
    print(f"Found {len(unique)} unique Play'n'GO slots on gamingslots.com")
    print("\nFirst 10:")
    for slot in unique[:10]:
        print(f"  {slot}")
else:
    print("Page not accessible")
