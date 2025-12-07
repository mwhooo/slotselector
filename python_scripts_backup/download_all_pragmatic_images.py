import json
import urllib.request
from PIL import Image
from io import BytesIO
import os
from urllib.error import URLError, HTTPError
import time
import sys

# Handle encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load slot providers
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

output_dir = "public/images"
os.makedirs(output_dir, exist_ok=True)

print(f"Attempting to download images for {len(slots)} Pragmatic Play slots...")
print("This may take several minutes...\n")

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
    
    # Construct image URL from gamingslots.com pattern
    # Convert slot name to URL-friendly format
    slug = slot_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    image_url = f"https://www.gamingslots.com/wp-content/uploads/2024/01/{slug}-logo.png"
    
    try:
        print(f"[{i}/{len(slots)}] Downloading {slot_name}...", end=" ", flush=True)
        
        # Try to download
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
        # Image not found at expected URL, skip
        failed += 1
        print("[SKIP]")
    except Exception as e:
        # Other errors (timeout, conversion, etc)
        failed += 1
        print(f"[ERR: {str(e)[:20]}]")
    
    # Rate limiting - be nice to the server
    if i % 10 == 0:
        time.sleep(0.5)

print(f"\n{'='*60}")
print(f"Download Complete!")
print(f"{'='*60}")
print(f"OK: {successful}")
print(f"FAILED: {failed}")
print(f"SKIPPED: {skipped}")
print(f"TOTAL: {successful + failed + skipped}/{len(slots)}")
