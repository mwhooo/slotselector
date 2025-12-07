import requests
from bs4 import BeautifulSoup
import json
import time
import re

print("Scraping NetEnt slots from gamingslots.com...")

# Get provider page
url = "https://www.gamingslots.com/slots/netent/"
resp = requests.get(url, timeout=10)
soup = BeautifulSoup(resp.content, 'html.parser')

# Find all slot links - look for any /slots/netent/ links
slots = {}

# Extract all href attributes containing netent
all_links = re.findall(r'/slots/netent/([^/\s"\']+)(?:-slot)?/?', resp.text)

for link_text in all_links:
    # Clean up the slug back to a readable name
    slot_name = link_text.replace('-', ' ').title()
    if slot_name and len(slot_name) > 2:
        # Avoid duplicates and special entries
        if slot_name not in slots and not slot_name.startswith('Http'):
            slots[slot_name] = 'NetEnt'

print(f"Found {len(slots)} unique NetEnt slots")
print("\nFirst 15 slots:")
for i, name in enumerate(sorted(set(slots.keys()))[:15], 1):
    print(f"  {i}. {name}")

# Save to file
if slots:
    with open('netent_slots.json', 'w') as f:
        json.dump(dict(sorted(set(slots.items()))), f, indent=2)
    print(f"\nSaved {len(slots)} slots to netent_slots.json")
