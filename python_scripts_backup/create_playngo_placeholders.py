#!/usr/bin/env python3
"""
Create placeholder images for Play'n GO slots that don't have images yet
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_images():
    """Create placeholder images for Play'n GO slots"""
    
    # Load Play'n GO slots
    with open('playngo_slots_temp.json', 'r') as f:
        slots = json.load(f)
    
    print(f"Creating placeholder images for {len(slots)} Play'n GO slots...\n")
    
    img_dir = Path('public/images')
    img_dir.mkdir(parents=True, exist_ok=True)
    
    # Play'n GO brand colors
    colors = [
        (76, 34, 137),    # Purple
        (241, 90, 34),    # Orange
        (52, 168, 219),   # Blue
        (34, 177, 76),    # Green
        (244, 67, 54),    # Red
    ]
    
    created = 0
    
    for i, slot_name in enumerate(sorted(slots.keys()), 1):
        slug = slot_name.lower().replace(' ', '-').replace("'", '')
        filepath = img_dir / f"{slug}.jpg"
        
        # Only create if doesn't exist
        if not filepath.exists():
            # Pick color based on index
            bg_color = colors[i % len(colors)]
            
            # Create image
            img = Image.new('RGB', (200, 280), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                # Try to use a larger font
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            lines = slot_name.split()
            
            # Draw text centered
            y = 120
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (200 - text_width) // 2
                draw.text((x, y), line, fill=(255, 255, 255), font=font)
                y += 30
            
            # Save
            img.save(filepath, 'JPEG', quality=85)
            created += 1
            
            if i % 50 == 0:
                print(f"[{i}/{len(slots)}] Created placeholders...")
    
    print(f"\n✓ Created {created} placeholder images")
    return created

if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image, ImageDraw, ImageFont
        create_placeholder_images()
    except ImportError:
        print("PIL not installed. Installing...")
        import subprocess
        subprocess.check_call(['.venv\\Scripts\\pip.exe', 'install', 'Pillow'])
        from PIL import Image, ImageDraw, ImageFont
        create_placeholder_images()
