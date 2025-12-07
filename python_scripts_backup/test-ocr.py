import easyocr
import json
from pathlib import Path
import re

# Initialize OCR reader
print("Loading OCR model (this may take a moment on first run)...")
reader = easyocr.Reader(['en'], gpu=False)
print("OCR model loaded.\n")

def extract_slot_name_from_image(image_path):
    """Extract slot name from image using EasyOCR"""
    try:
        results = reader.readtext(str(image_path))
        
        if not results:
            return None
        
        # Combine all detected text
        text_parts = [detection[1] for detection in results]
        text = ' '.join(text_parts)
        
        if not text or len(text.strip()) == 0:
            return None
        
        # Clean up text
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s\-&:!]', '', text)
        text = text.strip()
        
        if len(text) < 3:
            return None
        
        return text
        
    except Exception as e:
        return None

# Test with first 5 images
images_dir = Path('public/images')
slot_images = sorted(images_dir.glob('slot_*.jpg'))[:5]

print(f"Testing OCR on {len(slot_images)} sample images...\n")

for idx, image_path in enumerate(slot_images, 1):
    slot_num = int(image_path.stem.split('_')[1])
    print(f"[{idx}] {image_path.name}...", end=' ')
    
    extracted_name = extract_slot_name_from_image(image_path)
    
    if extracted_name:
        print(f"'{extracted_name}'")
    else:
        print("[NO TEXT DETECTED]")

print("\nDone with test run.")
