#!/usr/bin/env python3
"""
Map backed-up images to new provider-prefixed names.
This uses the original backup and matches them to new naming scheme.
"""

import json
import os
import shutil
from pathlib import Path

# Load current providers (with provider-prefixed names)
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get list of backup images
backup_dir = 'public/images_backup'
backup_images = set(f.replace('.jpg', '').replace('.png', '') for f in os.listdir(backup_dir))

print(f"Backup images available: {len(backup_images)}")
print(f"Slots to restore: {len(providers)}")

def name_to_slug(name):
    """Convert slot name to URL slug"""
    slug = name.lower()
    slug = slug.replace("'", "").replace("â€™", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    return slug

found = 0
not_found = []

for image_name, provider in providers.items():
    # Try to find matching backup image
    # Remove provider prefix to get slot name
    prefix = provider.lower().replace("'", "").replace(" ", "-")
    slot_name = image_name.replace(f"{prefix}-", "").replace(".jpg", "").replace(".png", "")
    
    # Try different slug variations
    slug = name_to_slug(slot_name)
    
    # Check if backup image exists (with either name)
    if slug in backup_images:
        src = os.path.join(backup_dir, f"{slug}.jpg")
        if not os.path.exists(src):
            src = os.path.join(backup_dir, f"{slug}.png")
        
        dst = os.path.join('public/images', image_name)
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            found += 1
            if found % 100 == 0:
                print(f"[{found}] Restored {image_name}")
    else:
        not_found.append((image_name, slot_name, slug))

print(f"\n{'='*50}")
print(f"✓ Restored: {found}/{len(providers)}")
print(f"✗ Not found: {len(not_found)}")

if not_found and len(not_found) <= 20:
    print("\nNot found:")
    for img_name, slot_name, slug in not_found:
        print(f"  {img_name} (looking for: {slug})")
