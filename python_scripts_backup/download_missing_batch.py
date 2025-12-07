import json
import urllib.request
from PIL import Image
from io import BytesIO
import os
import re
from urllib.error import HTTPError

# Load provider and check missing
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

output_dir = "public/images"
missing = [s for s in slots.keys() if not os.path.exists(f"{output_dir}/{s}.jpg")]

print(f"Downloading missing slot images...\n")

successful = 0
failed = 0
skipped_not_found = 0

for i, slot_name in enumerate(missing, 1):  # Download ALL missing
    output_file = f"{output_dir}/{slot_name}.jpg"
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    slot_url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        if i % 25 == 0:
            print(f"[{i}/{len(missing)}] {slot_name}...", end=" ", flush=True)
        
        # Fetch page
        with urllib.request.urlopen(slot_url, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        # Look for slot-specific logo URL (highest priority)
        pattern = rf'https://www\.gamingslots\.com/wp-content/uploads/[^"<]*{re.escape(slug)}-slot-logo\.jpg'
        match = re.search(pattern, content)
        
        if not match:
            print("[NOT FOUND]")
            skipped_not_found += 1
            continue
        
        image_url = match.group(0)
        
        # Download image
        with urllib.request.urlopen(image_url, timeout=10) as response:
            image_data = response.read()
        
        # Convert and save
        img = Image.open(BytesIO(image_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_file, 'JPEG', quality=85)
        
        successful += 1
        print("[OK]")
        
    except HTTPError as e:
        if e.code == 404:
            print("[404]")
        else:
            print(f"[ERR {e.code}]")
        failed += 1
    except Exception as e:
        print(f"[ERR]")
        failed += 1

print(f"\n{'='*40}")
print(f"OK: {successful}")
print(f"FAILED: {failed}")
print(f"NOT FOUND: {skipped_not_found}")
