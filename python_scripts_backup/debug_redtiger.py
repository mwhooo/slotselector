import requests
import re

# Check what URL patterns exist for red-tiger
url = "https://www.gamingslots.com/slots/red-tiger/"
resp = requests.get(url, timeout=10)

# Find all references to red-tiger in different patterns
patterns = [
    r'/slots/red-tiger-gaming/([^/\s"\']+)',
    r'/slots/red-tiger/([^/\s"\']+)',
    r'red-tiger.*?slot',
]

print("Checking different URL patterns for Red Tiger...\n")

for pattern in patterns:
    matches = re.findall(pattern, resp.text, re.IGNORECASE)
    if matches:
        print(f"Pattern: {pattern}")
        print(f"Found {len(set(matches))} matches")
        for match in list(set(matches))[:5]:
            print(f"  - {match}")
        print()

# Also check if red-tiger-gaming exists
url2 = "https://www.gamingslots.com/slots/red-tiger-gaming/"
resp2 = requests.get(url2, timeout=10)
if resp2.status_code == 200:
    print(f"\nred-tiger-gaming URL exists! Status: {resp2.status_code}")
    matches = re.findall(r'/slots/red-tiger-gaming/([^/\s"\']+)', resp2.text)
    print(f"Found {len(set(matches))} slots")
else:
    print(f"\nred-tiger-gaming URL: Status {resp2.status_code}")
