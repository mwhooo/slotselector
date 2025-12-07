import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
from PIL import Image
from io import BytesIO

# Load ALL Relax Gaming slots (including ones we filtered out)
with open('relaxgaming_slots.txt', 'r') as f:
    all_relaxgaming_slots = [line.strip() for line in f if line.strip()]

# Load current providers to see which ones have images
with open('slot_providers.json', 'r') as f:
    current_providers = json.load(f)

existing_images = set()
for name in all_relaxgaming_slots:
    if os.path.exists(f"public/images/{name}.jpg"):
        existing_images.add(name)

missing_slots = [s for s in all_relaxgaming_slots if s not in existing_images]

print(f"Total Relax Gaming slots: {len(all_relaxgaming_slots)}")
print(f"Already have images: {len(existing_images)}")
print(f"Missing images: {len(missing_slots)}")
print(f"\nAttempting recovery with expanded patterns...\n")

recovered = 0
failed = 0

for i, slot_name in enumerate(missing_slots, 1):
    image_path = f"public/images/{slot_name}.jpg"
    
    # Create slug variations
    base_slug = slot_name.lower()
    base_slug = base_slug.replace("'", "").replace("â€™", "")
    base_slug = ''.join(c if c.isalnum() else '-' for c in base_slug)
    base_slug = '-'.join(base_slug.split())
    
    # Try main URL first
    main_url = f"https://www.gamingslots.com/slots/relax-gaming/{base_slug}-slot/"
    
    found_image = False
    
    try:
        resp = requests.get(main_url, timeout=10)
        
        if resp.status_code == 200:
            # Try patterns in order of likelihood
            patterns = [
                # Pattern 1: {slug}-slot-logo.jpg
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*{base_slug}-slot-logo\.jpg', 'jpg'),
                # Pattern 2: {slug}-slot-game.jpg  
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*{base_slug}-slot-game\.jpg', 'jpg'),
                # Pattern 3: {slug}-logo-relax-gaming.png
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*{base_slug}-logo-relax-gaming\.png', 'png'),
                # Pattern 4: {slug}-relax-gaming.jpg
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*{base_slug}-relax-gaming\.jpg', 'jpg'),
                # Pattern 5: relax-gaming-{slug}.jpg
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*relax-gaming-{base_slug}\.jpg', 'jpg'),
                # Pattern 6: Any image with slug in name
                (f'https://www.gamingslots.com/wp-content/uploads/[^"]*{base_slug}[^"]*\.(?:jpg|png)', 'any'),
            ]
            
            for pattern, img_type in patterns:
                if found_image:
                    break
                
                matches = re.findall(pattern, resp.text, re.IGNORECASE)
                
                if matches:
                    img_url = matches[0]
                    
                    try:
                        img_resp = requests.get(img_url, timeout=10)
                        
                        if img_resp.status_code == 200:
                            img = Image.open(BytesIO(img_resp.content))
                            
                            # Skip if image is too small (likely not a slot image)
                            if img.width < 50 or img.height < 50:
                                continue
                            
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            os.makedirs('public/images', exist_ok=True)
                            img.save(image_path, 'JPEG', quality=85)
                            
                            found_image = True
                            recovered += 1
                            
                            if i % 10 == 0:
                                print(f"[{i}/{len(missing_slots)}] {slot_name}... [RECOVERED with {img_type}]")
                    except:
                        pass
        
        if not found_image and i % 10 == 0:
            print(f"[{i}/{len(missing_slots)}] {slot_name}... [FAILED]")
        
        if not found_image:
            failed += 1
        
        time.sleep(0.05)
        
    except Exception as e:
        failed += 1

print(f"\n========================================")
print(f"Recovered: {recovered}")
print(f"Still missing: {failed}")
print(f"Total Relax Gaming with images: {len(existing_images) + recovered}")
