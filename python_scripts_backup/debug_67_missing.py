import json
import os
import re

# Load providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Get list of missing
missing = []
for slot_name in providers.keys():
    image_path = f"public/images/{slot_name}.jpg"
    if not os.path.exists(image_path):
        missing.append(slot_name)

# Print summary and sample
print(f"Total missing: {len(missing)}")
print("\nAll 67 missing slots:")
for i, slot in enumerate(missing, 1):
    print(f"{i:2}. {slot}")
