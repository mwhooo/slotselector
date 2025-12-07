#!/usr/bin/env python3
"""Create placeholder images for Play'n GO slots missing images"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

# Load slots
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

img_dir = Path('public/images')
playngo_slots = [k for k, v in slots.items() if v == "Play'n GO"]

missing = []
for slot_name in playngo_slots:
    img_file = img_dir / f'{slot_name}.jpg'
    if not img_file.exists():
        missing.append(slot_name)

print(f"Creating {len(missing)} placeholder images for Play'n GO...")

# Play'n GO brand colors
colors = [
    (76, 34, 137),     # Play'n GO Purple
    (241, 90, 34),     # Play'n GO Orange
    (52, 168, 219),    # Play'n GO Blue
    (34, 177, 76),     # Green
    (244, 67, 54),     # Red
    (255, 193, 7),     # Amber
    (156, 39, 176),    # Deep Purple
]

created = 0

for i, slot_name in enumerate(sorted(missing)):
    img_file = img_dir / f'{slot_name}.jpg'
    
    # Pick color based on index
    bg_color = colors[i % len(colors)]
    
    # Create placeholder image
    img = Image.new('RGB', (200, 280), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw "N" for Play'n GO
    from PIL import ImageFont
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((85, 130), "N", fill=(255, 255, 255), font=font)
    
    # Save
    img.save(img_file, 'JPEG', quality=85)
    created += 1
    
    if created % 50 == 0:
        print(f"Created {created}/{len(missing)}...")

print(f"\n✓ Created {created} placeholder images")
