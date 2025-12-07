import json
import os

# Load current providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Check which slots have images
with_images = {}
without_images = {}

for slot_name in providers.keys():
    image_path = f"public/images/{slot_name}.jpg"
    if os.path.exists(image_path):
        with_images[slot_name] = providers[slot_name]
    else:
        without_images[slot_name] = providers[slot_name]

print(f"Slots with images: {len(with_images)}")
print(f"Slots without images: {len(without_images)}")

# Save filtered version with only slots that have images
with open('slot_providers.json', 'w') as f:
    json.dump(with_images, f, indent=2)

print(f"\nUpdated slot_providers.json to include only {len(with_images)} slots with images")

# Show breakdown by provider
from collections import Counter
providers_count = Counter([p for p in with_images.values()])
print("\nSlots by provider:")
for provider, count in providers_count.most_common():
    print(f"  {provider}: {count}")
