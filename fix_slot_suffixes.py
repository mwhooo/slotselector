#!/usr/bin/env python3
"""Fix image filename mismatches for Red Tiger and Hacksaw Gaming"""
import json
from pathlib import Path
import shutil

with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

img_dir = Path('public/images')

# Red Tiger and Hacksaw slots have " Slot" suffix in database but not in filenames
# We need to rename images to match the slot names

red_tiger_slots = [k for k, v in slots.items() if v == 'Red Tiger']
hacksaw_slots = [k for k, v in slots.items() if v == 'Hacksaw Gaming']

renamed = 0

print("Processing Red Tiger slots...")
for slot_name in red_tiger_slots:
    # Expected image file
    expected_path = img_dir / f'{slot_name}.jpg'
    
    if expected_path.exists():
        print(f"✓ {slot_name}")
        continue
    
    # Try to find image without " Slot" suffix
    base_name = slot_name.replace(' Slot', '')
    alt_path = img_dir / f'{base_name}.jpg'
    
    if alt_path.exists():
        try:
            alt_path.rename(expected_path)
            print(f"→ Renamed: {base_name} → {slot_name}")
            renamed += 1
        except Exception as e:
            print(f"✗ Error renaming {base_name}: {e}")

print("\nProcessing Hacksaw Gaming slots...")
for slot_name in hacksaw_slots:
    # Expected image file
    expected_path = img_dir / f'{slot_name}.jpg'
    
    if expected_path.exists():
        print(f"✓ {slot_name}")
        continue
    
    # Try to find image without " Slot" suffix
    base_name = slot_name.replace(' Slot', '')
    alt_path = img_dir / f'{base_name}.jpg'
    
    if alt_path.exists():
        try:
            alt_path.rename(expected_path)
            print(f"→ Renamed: {base_name} → {slot_name}")
            renamed += 1
        except Exception as e:
            print(f"✗ Error renaming {base_name}: {e}")

print(f"\nTotal files renamed: {renamed}")
