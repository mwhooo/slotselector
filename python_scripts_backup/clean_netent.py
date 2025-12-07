import json
import re

# Load the scraped data
with open('netent_slots.json', 'r') as f:
    slots = json.load(f)

# Clean up - remove trailing " Slot" and fix entries
cleaned = {}
for slot_name in slots.keys():
    # Remove " Slot" suffix if present
    name = slot_name.replace(' Slot', '').strip()
    
    # Skip entries that don't look like real slot names
    if name.startswith('#') or name.startswith('Http') or len(name) < 3:
        continue
    
    cleaned[name] = 'NetEnt'

print(f"Cleaned {len(cleaned)} NetEnt slots (removed {len(slots) - len(cleaned)} invalid entries)")
print("\nSample slots:")
for name in sorted(cleaned.keys())[10:20]:
    print(f"  {name}")

# Save cleaned version
with open('netent_slots.json', 'w') as f:
    json.dump(cleaned, f, indent=2)

print(f"\nSaved {len(cleaned)} cleaned NetEnt slots")
