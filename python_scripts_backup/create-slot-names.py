import json
from pathlib import Path

def create_slot_names_template():
    """
    Create a template JSON file with slot names that can be manually edited.
    Each slot can then be given a proper name instead of just "Slot X"
    """
    images_dir = Path('public/images')
    slot_images = sorted(images_dir.glob('slot_*.jpg'))
    
    slot_names = {}
    for image_path in slot_images:
        slot_num = int(image_path.stem.split('_')[1])
        slot_names[f"slot_{slot_num:03d}"] = f"Slot {slot_num}"
    
    output_file = Path('slot_names.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(slot_names, f, ensure_ascii=False, indent=2)
    
    print(f"Created {output_file} with {len(slot_names)} slots")
    print(f"You can now manually edit the names in this JSON file")
    print(f"Example format:")
    print(f'  "slot_001": "Lucky 7s"')
    print(f'  "slot_002": "Gold Rush"')

if __name__ == '__main__':
    create_slot_names_template()
