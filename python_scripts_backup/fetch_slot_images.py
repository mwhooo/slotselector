import json
import os
from pathlib import Path
from PIL import Image
import shutil
import subprocess
import sys

# Ensure bing-image-downloader is installed
try:
    from bing_image_downloader import downloader
except ImportError:
    print("Installing bing-image-downloader...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "bing-image-downloader"])
    from bing_image_downloader import downloader

# Paths
SLOT_NAMES_FILE = "slot_names.json"
OUTPUT_DIR = "public/images"
TEMP_DIR = "temp_images"

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

# Load slot names
with open(SLOT_NAMES_FILE, 'r', encoding='utf-8') as f:
    slot_data = json.load(f)

# Extract values (game names) from dict
slot_names = list(slot_data.values())

print(f"Found {len(slot_names)} slot games to process")

# Download images for each slot
for index, slot_name in enumerate(slot_names, 1):
    output_file = f"{OUTPUT_DIR}/slot_{index:03d}.jpg"
    
    # Skip if image already exists
    if os.path.exists(output_file):
        print(f"✓ {index:3d}. {slot_name} (already exists)")
        continue
    
    try:
        # Download image
        downloader.download(
            slot_name,
            limit=1,
            output_dir=TEMP_DIR,
            adult_filter_off=True,
            force_replace=False,
            timeout=15,
            verbose=False
        )
        
        # Find the downloaded image
        temp_slot_dir = os.path.join(TEMP_DIR, slot_name)
        if os.path.exists(temp_slot_dir):
            files = os.listdir(temp_slot_dir)
            if files:
                source_image = os.path.join(temp_slot_dir, files[0])
                
                # Convert to JPG
                try:
                    img = Image.open(source_image)
                    # Convert RGBA to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(output_file, 'JPEG', quality=85)
                    print(f"✓ {index:3d}. {slot_name}")
                except Exception as e:
                    print(f"✗ {index:3d}. {slot_name} (conversion error: {str(e)[:30]})")
            else:
                print(f"✗ {index:3d}. {slot_name} (no files downloaded)")
        else:
            print(f"✗ {index:3d}. {slot_name} (download failed)")
        
        # Cleanup temp directory for this slot
        if os.path.exists(temp_slot_dir):
            shutil.rmtree(temp_slot_dir)
    
    except Exception as e:
        print(f"✗ {index:3d}. {slot_name} (error: {str(e)[:30]})")

# Final cleanup
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)

print("\nDownload complete!")
