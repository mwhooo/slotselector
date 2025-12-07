import urllib.request
from PIL import Image
from io import BytesIO
import json
import os

# Pragmatic Play slots to download
slots = [
    ("Wolf Gold", "https://www.gamingslots.com/wp-content/uploads/2017/04/wolf-gold-slot.jpg"),
    ("Sugar Rush", "https://www.gamingslots.com/wp-content/uploads/2022/11/sugar-rush-slot-logo-pragmatic-play.png"),
    ("The Dog House Megaways", "https://www.gamingslots.com/wp-content/uploads/2020/07/the-dog-house-megaways-logo.jpg"),
    ("Muertos Multiplier Megaways", "https://www.gamingslots.com/wp-content/uploads/2022/09/muertos-multiplier-megaways-slot-logo.jpg"),
    ("Mustang Gold", "https://www.gamingslots.com/wp-content/uploads/2022/11/mustang-gold-slot-logo-pragmatic-play.png"),
]

output_dir = "public/images"
provider_file = "slot_providers.json"

# Load existing provider data if it exists
providers = {}
if os.path.exists(provider_file):
    with open(provider_file, 'r', encoding='utf-8') as f:
        providers = json.load(f)

print("Downloading Pragmatic Play slot images...")

for slot_name, url in slots:
    output_file = f"{output_dir}/{slot_name}.jpg"
    
    try:
        print(f"Downloading {slot_name}...", end=" ")
        
        # Download the image
        with urllib.request.urlopen(url, timeout=10) as response:
            image_data = response.read()
        
        # Open and convert image
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as JPG
        img.save(output_file, 'JPEG', quality=85)
        
        # Add to provider mapping
        providers[slot_name] = "Pragmatic Play"
        
        print("✓")
    except Exception as e:
        print(f"✗ ({str(e)[:40]})")

# Save provider mapping
with open(provider_file, 'w', encoding='utf-8') as f:
    json.dump(providers, f, indent=2, ensure_ascii=False)

print(f"\n✓ Saved provider mapping to {provider_file}")
print(f"✓ Total slots with providers: {len(providers)}")
