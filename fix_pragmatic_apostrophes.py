#!/usr/bin/env python3
"""Fix corrupted apostrophes in slot_providers.json"""
import json

with open('slot_providers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix corrupted apostrophes
fixed_data = {}
fixes = 0

for key, value in data.items():
    # Replace corrupted smart quotes with regular apostrophe
    new_key = key.replace('\u00e2\u20ac\u2122', "'")
    if new_key != key:
        fixes += 1
        print(f'Fixed: {key} -> {new_key}')
    fixed_data[new_key] = value

# Save back in sorted order
sorted_data = dict(sorted(fixed_data.items()))

with open('slot_providers.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, indent=2, ensure_ascii=False)

print(f'\nTotal slots fixed: {fixes}')
