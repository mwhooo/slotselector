#!/usr/bin/env python3
"""Check image coverage by provider"""
import json
from pathlib import Path

# Load slots
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

# Get all providers
providers = {}
for slot_name, provider in slots.items():
    if provider not in providers:
        providers[provider] = {'total': 0, 'with_images': 0, 'missing': []}
    providers[provider]['total'] += 1
    
    img_file = Path(f'public/images/{slot_name}.jpg')
    if img_file.exists():
        providers[provider]['with_images'] += 1
    else:
        providers[provider]['missing'].append(slot_name)

# Print summary
print('Provider Coverage:')
print('-' * 70)
for provider in sorted(providers.keys(), key=lambda x: providers[x]['with_images'] / providers[x]['total'] if providers[x]['total'] > 0 else 0):
    total = providers[provider]['total']
    with_img = providers[provider]['with_images']
    pct = (with_img / total * 100) if total > 0 else 0
    status = '✓' if pct == 100 else '✗'
    print(f'{status} {provider:20} {with_img:3}/{total:3} ({pct:5.1f}%)')
    
    if providers[provider]['missing']:
        print(f'   Missing images ({len(providers[provider]["missing"])}):')
        for slot in sorted(providers[provider]['missing'])[:10]:
            print(f'     - {slot}')
        if len(providers[provider]['missing']) > 10:
            print(f'     ... and {len(providers[provider]["missing"]) - 10} more')
        print()

# Total summary
total_slots = sum(p['total'] for p in providers.values())
total_with_images = sum(p['with_images'] for p in providers.values())
total_pct = (total_with_images / total_slots * 100) if total_slots > 0 else 0

print('-' * 70)
print(f'TOTAL: {total_with_images}/{total_slots} ({total_pct:.1f}%)')
