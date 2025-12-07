#!/usr/bin/env python3
"""Create placeholder images for Pragmatic Play slots missing images"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

# Load slots
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

img_dir = Path('public/images')
pragmatic_slots = [k for k, v in slots.items() if v == 'Pragmatic Play']

missing = []
for slot_name in pragmatic_slots:
    img_file = img_dir / f'{slot_name}.jpg'
    if not img_file.exists():
        missing.append(slot_name)

print(f"Creating {len(missing)} placeholder images for Pragmatic Play...")

# Play'n GO brand colors for variety
colors = [
    (220, 20, 60),     # Crimson
    (30, 144, 255),    # Dodger Blue
    (50, 205, 50),     # Lime Green
    (255, 165, 0),     # Orange
    (147, 112, 219),   # Medium Purple
    (199, 21, 133),    # Medium Violet Red
    (34, 139, 34),     # Forest Green
]

created = 0

for i, slot_name in enumerate(sorted(missing)):
    img_file = img_dir / f'{slot_name}.jpg'
    
    # Pick color based on index
    bg_color = colors[i % len(colors)]
    
    # Create placeholder image
    img = Image.new('RGB', (200, 280), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw "P" for Pragmatic
    from PIL import ImageFont
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((85, 130), "P", fill=(255, 255, 255), font=font)
    
    # Save
    img.save(img_file, 'JPEG', quality=85)
    created += 1
    
    if created % 50 == 0:
        print(f"Created {created}/{len(missing)}...")

print(f"\n✓ Created {created} placeholder images")
