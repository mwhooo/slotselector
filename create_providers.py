#!/usr/bin/env python3
"""
Create slot_providers.json from downloaded Gamomat slots
"""

import json
import os

# Load gamomat slots
with open('gamomat_slots.json') as f:
    slots = json.load(f)

# Create provider mapping with provider-prefixed filenames
providers = {}
for name in slots:
    slug = name.lower().replace("'", "").replace('"', '')
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split()).strip('-')
    
    # Determine extension (mostly .png for Gamomat)
    jpg_path = f'public/images/gamomat-{slug}.jpg'
    png_path = f'public/images/gamomat-{slug}.png'
    
    if os.path.exists(png_path):
        providers[f'gamomat-{slug}.png'] = 'Gamomat'
    elif os.path.exists(jpg_path):
        providers[f'gamomat-{slug}.jpg'] = 'Gamomat'

# Save
with open('slot_providers.json', 'w') as f:
    json.dump(providers, f, indent=2)

print(f'✓ Created slot_providers.json with {len(providers)} slots')
print(f'\nSample entries:')
for k in list(providers.keys())[:3]:
    print(f'  {k}: {providers[k]}')
