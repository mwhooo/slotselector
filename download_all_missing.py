#!/usr/bin/env python3
"""Run all download scripts and check final coverage"""
import subprocess
import sys
import json
from pathlib import Path

print("=" * 70)
print("DOWNLOADING MISSING IMAGES")
print("=" * 70)

# Run Pragmatic download
print("\n[1/2] Downloading missing Pragmatic Play images...")
result1 = subprocess.run([sys.executable, 'download_missing_pragmatic.py'], 
                         capture_output=False)

# Run Play'n GO download
print("\n[2/2] Downloading missing Play'n GO images...")
result2 = subprocess.run([sys.executable, 'download_missing_playngo.py'], 
                         capture_output=False)

# Check final coverage
print("\n" + "=" * 70)
print("FINAL IMAGE COVERAGE")
print("=" * 70)

with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

providers = {}
for slot_name, provider in slots.items():
    if provider not in providers:
        providers[provider] = {'total': 0, 'with_images': 0}
    providers[provider]['total'] += 1
    
    img_file = Path(f'public/images/{slot_name}.jpg')
    if img_file.exists():
        providers[provider]['with_images'] += 1

# Print summary
for provider in sorted(providers.keys(), key=lambda x: providers[x]['with_images'] / providers[x]['total'] if providers[x]['total'] > 0 else 0):
    total = providers[provider]['total']
    with_img = providers[provider]['with_images']
    pct = (with_img / total * 100) if total > 0 else 0
    status = '✓' if pct == 100 else '✗'
    print(f'{status} {provider:20} {with_img:3}/{total:3} ({pct:5.1f}%)')

# Total summary
total_slots = sum(p['total'] for p in providers.values())
total_with_images = sum(p['with_images'] for p in providers.values())
total_pct = (total_with_images / total_slots * 100) if total_slots > 0 else 0

print("-" * 70)
print(f'TOTAL: {total_with_images}/{total_slots} ({total_pct:.1f}%)')
