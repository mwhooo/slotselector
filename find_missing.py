#!/usr/bin/env python3
"""
Find slots that are missing images and save them for targeted download.
"""

import json
import os

# Load providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Check which have images
missing = []
for image_name, provider in providers.items():
    image_path = f"public/images/{image_name}"
    if not os.path.exists(image_path):
        missing.append((image_name, provider))

print(f"Missing images: {len(missing)}")
print(f"With images: {len(providers) - len(missing)}")
print(f"Percentage complete: {100 * (len(providers) - len(missing)) // len(providers)}%\n")

# Save missing list
with open('missing_images.json', 'w') as f:
    json.dump(missing, f, indent=2)

print("Saved missing image list to missing_images.json")

# Show first 20
print("\nFirst 20 missing:")
for img_name, provider in missing[:20]:
    print(f"  {img_name} ({provider})")
