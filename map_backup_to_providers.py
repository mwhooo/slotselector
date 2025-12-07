#!/usr/bin/env python3
"""
Map backup images to provider-prefixed names by matching slugs.
"""

import json
import os
import shutil
from pathlib import Path

# Load current providers (provider-prefixed names)
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get backup images
backup_dir = 'public/images_backup'
backup_images = {f.replace('.jpg', '').replace('.png', ''): f for f in os.listdir(backup_dir)}

print(f"Providers to fill: {len(providers)}")
print(f"Backup images available: {len(backup_images)}\n")

def name_to_slug(name):
    """Convert slot name to URL slug"""
    slug = name.lower()
    slug = slug.replace("'", "").replace("â€™", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    return slug

found = 0
not_found = 0
failed_list = []

for image_name, provider in providers.items():
    # Extract slot name
    prefix = provider.lower().replace("'", "").replace(" ", "-")
    slot_name = image_name.replace(f"{prefix}-", "").replace(".jpg", "").replace(".png", "")
    
    # Create slug
    slug = name_to_slug(slot_name)
    
    # Try to find in backup
    # First try exact slug match (hyphenated)
    if slug in backup_images:
        backup_file = backup_images[slug]
        src = os.path.join(backup_dir, backup_file)
        dst = os.path.join('public/images', image_name)
        shutil.copy2(src, dst)
        found += 1
        if found % 100 == 0:
            print(f"[{found}] Copied {image_name}")
    else:
        # Try space version
        space_name = slug.replace('-', ' ').title()
        if space_name in backup_images:
            backup_file = backup_images[space_name]
            src = os.path.join(backup_dir, backup_file)
            dst = os.path.join('public/images', image_name)
            shutil.copy2(src, dst)
            found += 1
            if found % 100 == 0:
                print(f"[{found}] Copied {image_name}")
        else:
            not_found += 1
            if not_found <= 20:
                failed_list.append((image_name, slot_name, slug, space_name))

print(f"\n{'='*50}")
print(f"✓ Matched & copied: {found}/{len(providers)}")
print(f"✗ Not found: {not_found}")
print(f"{'='*50}")

if failed_list:
    print("\nNot found (first 20):")
    for img_name, slot, slug, space in failed_list:
        print(f"  Looking for: '{slug}' or '{space}'")
