import json
import urllib.request
from PIL import Image
from io import BytesIO
import os
import re
from urllib.error import URLError, HTTPError
import time

# Load slot providers
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

output_dir = "public/images"
os.makedirs(output_dir, exist_ok=True)

print(f"Downloading images for Pragmatic Play slots from gamingslots.com...")
print("This will extract real image URLs from each game page.\n")

successful = 0
failed = 0
skipped = 0

for i, slot_name in enumerate(slots.keys(), 1):
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    # Skip if already exists
    if os.path.exists(output_file):
        skipped += 1
        if i % 50 == 0:
            print(f"[{i}/{len(slots)}] Skipped: {slot_name}")
        continue
    
    # Construct slot URL on gamingslots.com
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    slot_url = f"https://www.gamingslots.com/slots/pragmatic-play/{slug}-slot/"
    
    try:
        print(f"[{i}/{len(slots)}] {slot_name}...", end=" ", flush=True)
        
        # Fetch the slot page
        with urllib.request.urlopen(slot_url, timeout=5) as response:
            page_content = response.read().decode('utf-8', errors='ignore')
        
        # Look for image URL in the page (common patterns)
        # Look for data-src or src with wordpress image URLs
        image_patterns = [
            r'https://www\.gamingslots\.com/wp-content/uploads/[^"\s]*-logo[^"\s]*\.(?:jpg|png|webp)',
            r'https://www\.gamingslots\.com/wp-content/uploads/[^"\s]*-slot[^"\s]*\.(?:jpg|png|webp)',
        ]
        
        image_url = None
        for pattern in image_patterns:
            match = re.search(pattern, page_content)
            if match:
                image_url = match.group(0)
                break
        
        if not image_url:
            print("[NO IMG]")
            failed += 1
            continue
        
        # Download the image
        with urllib.request.urlopen(image_url, timeout=5) as response:
            image_data = response.read()
        
        # Open and convert image
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPG
        img.save(output_file, 'JPEG', quality=85)
        successful += 1
        print("[OK]")
        
    except (URLError, HTTPError, FileNotFoundError):
        failed += 1
        print("[SKIP]")
    except Exception as e:
        failed += 1
        print(f"[ERR]")
    
    # Rate limiting
    if i % 10 == 0:
        time.sleep(0.5)

print(f"\n{'='*60}")
print(f"OK: {successful} | FAILED: {failed} | SKIPPED: {skipped}")
print(f"TOTAL: {successful + failed + skipped}/{len(slots)}")
