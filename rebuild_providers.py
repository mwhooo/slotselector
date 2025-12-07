#!/usr/bin/env python3
"""
Rebuild slot_providers.json with provider-prefixed image names
to prevent duplicate overwrites.
"""

import json
import os

output = {}

# Define provider files to load
providers = {
    'pragmatic_slots.json': 'Pragmatic Play',
    'netent_slots.json': 'NetEnt',
    'hacksaw_slots.json': 'Hacksaw Gaming',
    'playngo_slots_temp.json': 'Play\'n GO',
    'redtiger_slots.json': 'Red Tiger',
}

# Load each provider file
for filename, provider_name in providers.items():
    if not os.path.exists(filename):
        print(f"⚠️  {filename} not found, skipping")
        continue
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Data could be a list or dict
        if isinstance(data, dict):
            slots = list(data.keys()) if isinstance(list(data.values())[0], dict) else data
        elif isinstance(data, list):
            slots = data
        else:
            slots = []
        
        # Convert to list of slot names if needed
        if isinstance(slots, dict):
            slots = list(slots.keys())
        
        # Add to output with provider-prefixed image names
        for slot_name in slots:
            # Create provider-prefixed image filename
            provider_prefix = provider_name.lower().replace("'", "").replace(" ", "-")
            image_name = f"{provider_prefix}-{slot_name}.jpg"
            output[image_name] = provider_name
        
        print(f"✓ {provider_name}: {len(slots)} slots")
    
    except Exception as e:
        print(f"✗ Error loading {filename}: {e}")

# Save to slot_providers.json
with open('slot_providers.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Total slots: {len(output)}")
print(f"✓ Saved to slot_providers.json")
