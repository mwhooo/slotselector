import urllib.request
from PIL import Image
from io import BytesIO

# The correct URL for 3 Buzzing Wilds
image_url = "https://www.gamingslots.com/wp-content/uploads/2023/07/3-buzzing-wilds-slot-logo.jpg"
output_file = "public/images/3 Buzzing Wilds.jpg"

print(f"Downloading correct image from: {image_url}")

try:
    with urllib.request.urlopen(image_url, timeout=10) as response:
        image_data = response.read()
    
    img = Image.open(BytesIO(image_data))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img.save(output_file, 'JPEG', quality=85)
    print(f"✓ Saved to {output_file}")
    print(f"Image size: {img.size}")
    
except Exception as e:
    print(f"✗ Error: {e}")
