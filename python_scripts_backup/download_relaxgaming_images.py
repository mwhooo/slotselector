import json
import os
import requests
import time
import re
from PIL import Image
from io import BytesIO

# Load providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get Relax Gaming slots (only new ones)
relaxgaming_slots = {name: provider for name, provider in providers.items() if provider == 'Relax Gaming'}

print(f"Downloading Relax Gaming slot images ({len(relaxgaming_slots)} slots)...\n")

ok = 0
failed = 0
not_found = 0

for i, slot_name in enumerate(relaxgaming_slots.keys(), 1):
    # Check if image already exists
    image_path = f"public/images/{slot_name}.jpg"
    if os.path.exists(image_path):
        if i % 25 == 0:
            print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [EXISTS]")
        continue
    
    # Create slug
    slug = slot_name.lower()
    slug = slug.replace("'", "").replace("â€™", "")
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split())
    
    # Try to find image on gamingslots.com
    url = f"https://www.gamingslots.com/slots/relax-gaming/{slug}-slot/"
    
    try:
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 404:
            if i % 25 == 0:
                print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [404]")
            not_found += 1
        elif resp.status_code == 200:
            # Try multiple patterns for Relax Gaming
            # Pattern 1: {slug}-slot-logo.jpg
            pattern1 = f'https://www.gamingslots.com/wp-content/uploads/[^"]+{slug}-slot-logo.jpg'
            matches = re.findall(pattern1, resp.text)
            
            # Pattern 2: {slug}-slot-game.jpg
            if not matches:
                pattern2 = f'https://www.gamingslots.com/wp-content/uploads/[^"]+{slug}-slot-game.jpg'
                matches = re.findall(pattern2, resp.text)
            
            # Pattern 3: {slug}-logo-relax-gaming.png
            if not matches:
                pattern3 = f'https://www.gamingslots.com/wp-content/uploads/[^"]+{slug}-logo-relax-gaming.png'
                matches = re.findall(pattern3, resp.text)
            
            if matches:
                img_url = matches[0]
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code == 200:
                    try:
                        img = Image.open(BytesIO(img_resp.content))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        os.makedirs('public/images', exist_ok=True)
                        img.save(image_path, 'JPEG', quality=85)
                        
                        if i % 25 == 0:
                            print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [OK]")
                        ok += 1
                    except Exception as e:
                        if i % 25 == 0:
                            print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [ERR]")
                        failed += 1
                else:
                    if i % 25 == 0:
                        print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [FAILED]")
                    failed += 1
            else:
                if i % 25 == 0:
                    print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [NOT FOUND]")
                not_found += 1
        
        time.sleep(0.1)
        
    except Exception as e:
        if i % 25 == 0:
            print(f"[{i}/{len(relaxgaming_slots)}] {slot_name}... [ERR]")
        failed += 1

print(f"\n========================================")
print(f"OK: {ok}")
print(f"FAILED: {failed}")
print(f"NOT FOUND: {not_found}")
