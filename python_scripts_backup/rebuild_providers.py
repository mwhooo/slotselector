import json
import os
from pathlib import Path

# Get all image filenames
images_dir = "public/images"
image_files = [f[:-4] for f in os.listdir(images_dir) if f.endswith('.jpg')]

print(f"Found {len(image_files)} images")

# Load any existing provider data from backup files
providers = {}

# Try to load from individual provider JSON files if they exist
provider_files = {
    'pragmatic_play': 'slot_providers.json.pragmatic',
    'netent': 'netent_slots.json',
    'hacksaw': 'hacksaw_slots.json',
    'playngo': 'playngo_slots.json',
    'redtiger': 'redtiger_slots.json',
    'relaxgaming': 'relaxgaming_slots.txt'
}

# For now, just create entries for all images with unknown provider
# We'll manually assign providers based on the JSON files
for image_name in sorted(image_files):
    if image_name not in providers:
        providers[image_name] = "Unknown"

print(f"\nCreated entries for {len(providers)} slots")

# Try to load provider info from JSON files
if os.path.exists('netent_slots.json'):
    with open('netent_slots.json') as f:
        netent = json.load(f)
        for slot in netent.keys():
            if slot in providers:
                providers[slot] = 'NetEnt'
    print(f"  Assigned NetEnt provider to available slots")

if os.path.exists('hacksaw_slots.json'):
    with open('hacksaw_slots.json') as f:
        hacksaw = json.load(f)
        for slot in hacksaw.keys():
            if slot in providers:
                providers[slot] = 'Hacksaw Gaming'
    print(f"  Assigned Hacksaw Gaming provider to available slots")

# Save rebuilt file
with open('slot_providers.json', 'w') as f:
    json.dump(providers, f, indent=2)

print(f"\nRebuilt slot_providers.json with {len(providers)} slots")

# Show breakdown
from collections import Counter
counts = Counter(providers.values())
print("\nProvider breakdown:")
for provider, count in counts.most_common():
    print(f"  {provider}: {count}")
