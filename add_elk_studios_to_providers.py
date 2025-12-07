#!/usr/bin/env python3
"""
Add ELK Studios slots to slot_providers.json
"""

import json
from pathlib import Path

# Load existing providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get list of elk studios images
images_dir = Path('public/images')
image_files = {f.name for f in images_dir.glob('elkstudios-*')}

print(f"Found {len(image_files)} ELK Studios images")

# Add to providers
added = 0
for image_file in sorted(image_files):
    if image_file not in providers:
        providers[image_file] = "ELK Studios"
        added += 1

print(f"Added {added} new entries to slot_providers.json")

# Save updated providers
with open('slot_providers.json', 'w') as f:
    json.dump(providers, f, indent=2)

print(f"Total entries in slot_providers.json: {len(providers)}")
