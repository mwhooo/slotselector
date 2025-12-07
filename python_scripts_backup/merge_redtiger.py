import json

# Load Red Tiger
with open('redtiger_slots.json', 'r') as f:
    redtiger = json.load(f)

# Clean up - remove trailing " Slot" and skip bad entries
cleaned = {}
for slot_name in redtiger.keys():
    # Remove " Slot" suffix
    name = slot_name.replace(' Slot', '').strip()
    
    # Skip bad entries
    if name.startswith('#') or name.startswith('Http') or len(name) < 3:
        continue
    
    cleaned[name] = 'Red Tiger'

print(f"Cleaned {len(cleaned)} Red Tiger slots (removed {len(redtiger) - len(cleaned)} invalid)")

# Merge with current
with open('slot_providers.json', 'r') as f:
    current = json.load(f)

merged = {**current, **cleaned}

print(f"\nCurrent slots: {len(current)}")
print(f"Adding: {len(cleaned)} Red Tiger slots")
print(f"Total after merge: {len(merged)}")

# Save merged
with open('slot_providers.json', 'w') as f:
    json.dump(merged, f, indent=2)

print("\nUpdated slot_providers.json")
