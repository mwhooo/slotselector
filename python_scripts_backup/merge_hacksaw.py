import json

# Load Hacksaw
with open('hacksaw_slots.json', 'r') as f:
    hacksaw = json.load(f)

# Clean up - remove trailing " Slot" and skip bad entries
cleaned = {}
for slot_name in hacksaw.keys():
    # Remove " Slot" suffix
    name = slot_name.replace(' Slot', '').strip()
    
    # Skip bad entries
    if name.startswith('#') or name.startswith('Http') or len(name) < 3:
        continue
    
    cleaned[name] = 'Hacksaw Gaming'

print(f"Cleaned {len(cleaned)} Hacksaw slots (removed {len(hacksaw) - len(cleaned)} invalid)")
print("\nAll Hacksaw slots:")
for name in sorted(cleaned.keys()):
    print(f"  {name}")

# Merge with current
with open('slot_providers.json', 'r') as f:
    current = json.load(f)

merged = {**current, **cleaned}

print(f"\nCurrent slots: {len(current)}")
print(f"Adding: {len(cleaned)} Hacksaw slots")
print(f"Total after merge: {len(merged)}")

# Save merged
with open('slot_providers.json', 'w') as f:
    json.dump(merged, f, indent=2)

print("\nUpdated slot_providers.json")
