#!/usr/bin/env python3
"""Smart filter to match slot names to images, handling naming variations."""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize a slot name for comparison."""
    # Remove common suffixes
    normalized = re.sub(r'\s+Slot\s*$', '', name, flags=re.IGNORECASE)
    normalized = re.sub(r'\s+Abyssways\s*$', '', normalized, flags=re.IGNORECASE)
    # Remove special chars and normalize spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized.strip()).lower()
    return normalized

def find_matching_image(slot_name, image_stems):
    """Find matching image for a slot, handling variations."""
    exact = slot_name in image_stems
    if exact:
        return slot_name
    
    # Try normalized match
    normalized_slot = normalize_name(slot_name)
    for img_name in image_stems:
        if normalized_slot == normalize_name(img_name):
            return img_name
    
    # Try fuzzy matching as fallback
    best_match = None
    best_ratio = 0
    for img_name in image_stems:
        ratio = SequenceMatcher(None, normalized_slot, normalize_name(img_name)).ratio()
        if ratio > best_ratio and ratio > 0.85:  # 85% match threshold
            best_ratio = ratio
            best_match = img_name
    
    return best_match

def main():
    # Load slots
    with open('slot_providers.json', 'r', encoding='utf-8') as f:
        slots = json.load(f)
    
    # Get image filenames
    images_dir = Path('public/images')
    image_stems = {img.stem for img in images_dir.glob('*.jpg')}
    
    print(f"Total slots in database: {len(slots)}")
    print(f"Total image files: {len(image_stems)}\n")
    
    # Filter and match
    matched_slots = {}
    unmatched = []
    
    for slot_name, provider in slots.items():
        # Skip problematic entries
        if slot_name.startswith('#'):
            continue
        
        matched_image = find_matching_image(slot_name, image_stems)
        if matched_image:
            # Use the actual slot name key, not the image name
            matched_slots[slot_name] = provider
        else:
            unmatched.append((slot_name, provider))
    
    print(f"Matched slots with images: {len(matched_slots)}")
    print(f"Unmatched slots: {len(unmatched)}\n")
    
    # Show breakdown by provider
    provider_counts = {}
    for slot, provider in matched_slots.items():
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    
    print("Matched slots by provider:")
    for provider, count in sorted(provider_counts.items()):
        total = sum(1 for s, p in slots.items() if p == provider and not s.startswith('#'))
        pct = int(100 * count / total) if total > 0 else 0
        print(f"  {provider}: {count}/{total} ({pct}%)")
    
    # Save matched slots
    sorted_matched = dict(sorted(matched_slots.items()))
    with open('slot_providers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_matched, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(matched_slots)} matched slots to slot_providers.json")
    
    # Show some unmatched examples
    if unmatched:
        print(f"\nFirst 10 unmatched slots:")
        for slot_name, provider in unmatched[:10]:
            print(f"  {provider}: {slot_name}")

if __name__ == '__main__':
    main()
