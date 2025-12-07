#!/usr/bin/env python3
"""Filter slot_providers.json to only include slots with existing images."""

import json
from pathlib import Path

def main():
    # Load slot providers
    with open('slot_providers.json', 'r', encoding='utf-8') as f:
        slots = json.load(f)
    
    # Get list of existing images
    images_dir = Path('public/images')
    existing_images = set()
    for img in images_dir.glob('*.jpg'):
        # Image name matches slot name
        slot_name = img.stem  # filename without .jpg
        existing_images.add(slot_name)
    
    print(f"Total slots in data: {len(slots)}")
    print(f"Total images available: {len(existing_images)}")
    
    # Filter slots to only those with images
    filtered_slots = {}
    missing_count = 0
    for slot_name, provider in slots.items():
        if slot_name in existing_images:
            filtered_slots[slot_name] = provider
        else:
            missing_count += 1
    
    print(f"Slots with images: {len(filtered_slots)}")
    print(f"Slots without images: {missing_count}")
    
    # Count by provider in filtered set
    providers = {}
    for slot, provider in filtered_slots.items():
        providers[provider] = providers.get(provider, 0) + 1
    
    print("\nProvider breakdown (with images):")
    for provider, count in sorted(providers.items()):
        print(f"  {provider}: {count} slots")
    
    # Save filtered file
    sorted_filtered = dict(sorted(filtered_slots.items()))
    with open('slot_providers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_filtered, f, indent=2, ensure_ascii=False)
    
    print("\nSaved filtered slot_providers.json")
if __name__ == '__main__':
    main()
