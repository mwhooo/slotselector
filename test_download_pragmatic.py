#!/usr/bin/env python3
"""
Download the 10 test Pragmatic Play images with provider prefix.
Use SLUG for URL, but PROPER NAME for saved filename.
"""

import urllib.request
import os
from pathlib import Path

# Test slots: (slug_for_url, nice_name_for_filename)
slots = [
    ('3-buzzing-wilds', '3 Buzzing Wilds'),
    ('3-dancing-monkeys', '3 Dancing Monkeys'),
    ('3-genie-wishes', '3 Genie Wishes'),
    ('3-kingdoms-battle-of-red-cliffs', '3 Kingdoms Battle Of Red Cliffs'),
    ('5-frozen-charms-megaways', '5 Frozen Charms Megaways'),
    ('5-lions', '5 Lions'),
    ('5-lions-dance', '5 Lions Dance'),
    ('5-lions-gold', '5 Lions Gold'),
    ('5-lions-megaways', '5 Lions Megaways'),
    ('7-monkeys', '7 Monkeys'),
]

# Create images directory
Path("public/images").mkdir(parents=True, exist_ok=True)

print("Downloading 10 test Pragmatic Play images...\n")

ok = 0
failed = 0

for slug, name in slots:
    # Image filename: pragmatic-{name}.jpg
    image_name = f"pragmatic-{name}.jpg"
    image_path = f"public/images/{image_name}"
    
    # Image URL (use SLUG)
    image_url = f"https://www.gamingslots.com/images/slots/pragmatic-play/{slug}-slot-logo.jpg"
    
    try:
        print(f"Downloading: {image_name}")
        urllib.request.urlretrieve(image_url, image_path)
        print(f"  ✓ OK")
        ok += 1
    except Exception as e:
        print(f"  ✗ Failed: {type(e).__name__}: {str(e)[:50]}")
        failed += 1

print(f"\n{'='*50}")
print(f"✓ Downloaded: {ok}")
print(f"✗ Failed: {failed}")
