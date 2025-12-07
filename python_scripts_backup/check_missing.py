import json
import os

# Load provider file
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

# Check which images exist
missing = []
for slot_name in slots.keys():
    image_path = f"public/images/{slot_name}.jpg"
    if not os.path.exists(image_path):
        missing.append(slot_name)

print(f"Total slots: {len(slots)}")
print(f"Missing images: {len(missing)}")
print(f"\nFirst 10 missing slots:")
for i, name in enumerate(missing[:10], 1):
    print(f"  {i}. {name}")
