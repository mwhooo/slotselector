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

def extract_all_slot_names():
    """Extract names from all slot images"""
    images_dir = Path('public/images')
    if not images_dir.exists():
        print(f"Error: {images_dir} not found")
        return
    
    slot_images = sorted(images_dir.glob('slot_*.jpg'))
    if not slot_images:
        print("No slot images found")
        return
    
    print(f"Processing {len(slot_images)} images for OCR...\n")
    
    slot_names = {}
    successful = 0
    
    for idx, image_path in enumerate(slot_images, 1):
        slot_num = int(image_path.stem.split('_')[1])
        print(f"[{idx}/{len(slot_images)}] {image_path.name}...", end=' ')
        
        extracted_name = extract_slot_name_from_image(image_path)
        
        if extracted_name:
            slot_names[f"slot_{slot_num:03d}"] = extracted_name
            print(f"'{extracted_name}'")
            successful += 1
        else:
            slot_names[f"slot_{slot_num:03d}"] = f"Slot {slot_num}"
            print("[default]")
    
    # Save to JSON
    output_file = Path('slot_names.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(slot_names, f, ensure_ascii=False, indent=2)
    
    print(f"\n[DONE] Successfully extracted {successful}/{len(slot_images)}")
    print(f"Saved to {output_file}")
    print("\nSample extracted names:")
    for slot, name in list(slot_names.items())[:5]:
        print(f"  {slot}: {name}")

if __name__ == '__main__':
    extract_all_slot_names()
