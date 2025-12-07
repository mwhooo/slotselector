#!/usr/bin/env python3
"""
Add 1x2gaming slots to slot_providers.json
"""

import json
from pathlib import Path

# Load existing providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Load 1x2gaming slot names
with open('1x2gaming_slots.json', 'r') as f:
    slots = json.load(f)

# Get list of 1x2gaming images
images_dir = Path('public/images')
image_files = {f.name for f in images_dir.glob('1x2gaming-*')}

print(f"Found {len(image_files)} 1x2gaming images")

# Add to providers
added = 0
for image_file in sorted(image_files):
    if image_file not in providers:
        providers[image_file] = "1x2gaming"
        added += 1

print(f"Added {added} new entries to slot_providers.json")

# Save updated providers
with open('slot_providers.json', 'w') as f:
    json.dump(providers, f, indent=2)

print(f"Total entries in slot_providers.json: {len(providers)}")
