import requests

# Try to get available providers list
url = "https://www.gamingslots.com/slots/"
resp = requests.get(url, timeout=10)

# Find all /slots/ paths
import re
matches = re.findall(r'/slots/([a-z-]+)/', resp.text)
providers = sorted(set(matches))

print(f"Found {len(providers)} providers:")
for p in providers:
    print(f"  {p}")
