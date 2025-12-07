import json
import os
from pathlib import Path
from PIL import Image
import shutil
import subprocess
import sys
import glob

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
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

# Load slot names
with open(SLOT_NAMES_FILE, 'r', encoding='utf-8') as f:
    slot_data = json.load(f)

# Get first game name
first_game_name = list(slot_data.values())[0]
print(f"Downloading image for: {first_game_name}")

try:
    # Download image
    downloader.download(
        first_game_name,
        limit=1,
        output_dir=TEMP_DIR,
        adult_filter_off=True,
        force_replace=True,
        timeout=15,
        verbose=False
    )
    
    # Find the downloaded image in temp directory
    image_files = glob.glob(f"{TEMP_DIR}/**/*.jpg", recursive=True) + glob.glob(f"{TEMP_DIR}/**/*.png", recursive=True)
    
    if image_files:
        source_image = image_files[0]
        output_file = f"{OUTPUT_DIR}/{first_game_name}.jpg"
        
        try:
            img = Image.open(source_image)
            # Convert RGBA to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_file, 'JPEG', quality=85)
            print(f"✓ Downloaded and saved: {output_file}")
        except Exception as e:
            print(f"✗ Error converting image: {str(e)}")
    else:
        print(f"✗ No image files found in temp directory")
    
    # Cleanup temp directory
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

except Exception as e:
    print(f"✗ Error: {str(e)}")
