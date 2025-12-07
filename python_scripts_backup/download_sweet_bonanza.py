import urllib.request
from PIL import Image
from io import BytesIO
import os

# Image URL from gamingslots.com
image_url = "https://www.gamingslots.com/wp-content/uploads/2022/11/sweet-bonanza-slot-logo-pragmatic-play.png"
output_file = "public/images/Sweet Bonanza.jpg"

print(f"Downloading from: {image_url}")

try:
    # Download the image
    with urllib.request.urlopen(image_url, timeout=10) as response:
        image_data = response.read()
    
    # Open and convert image
    img = Image.open(BytesIO(image_data))
    
    # Convert RGBA to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save as JPG
    img.save(output_file, 'JPEG', quality=85)
    print(f"✓ Downloaded and saved: {output_file}")
    print(f"Image size: {img.size}")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
