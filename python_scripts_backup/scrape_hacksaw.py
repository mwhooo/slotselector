import requests
import json
import re

print("Scraping Hacksaw Gaming slots from gamingslots.com...")

# Get provider page
url = "https://www.gamingslots.com/slots/hacksaw-gaming/"
resp = requests.get(url, timeout=10)

# Extract all hacksaw-gaming slot links
all_links = re.findall(r'/slots/hacksaw-gaming/([^/\s"\']+)(?:-slot)?/?', resp.text)

slots = {}
for link_text in all_links:
    # Clean up the slug back to a readable name
    slot_name = link_text.replace('-', ' ').title()
    if slot_name and len(slot_name) > 2 and not slot_name.startswith('Http'):
        slots[slot_name] = 'Hacksaw Gaming'

# Remove duplicates
unique_slots = dict(sorted(set(slots.items())))

print(f"Found {len(unique_slots)} unique Hacksaw Gaming slots")
print("\nFirst 15 slots:")
for i, (name, provider) in enumerate(list(unique_slots.items())[:15], 1):
    print(f"  {i}. {name}")

# Save to file
with open('hacksaw_slots.json', 'w') as f:
    json.dump(unique_slots, f, indent=2)

print(f"\nSaved {len(unique_slots)} Hacksaw Gaming slots")
