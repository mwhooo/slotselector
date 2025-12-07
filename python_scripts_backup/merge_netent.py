import json

# Load current providers
with open('slot_providers.json', 'r') as f:
    current = json.load(f)

# Load NetEnt
with open('netent_slots.json', 'r') as f:
    netent = json.load(f)

# Merge
combined = {**current, **netent}

print(f"Current slots: {len(current)}")
print(f"NetEnt slots: {len(netent)}")
print(f"Total after merge: {len(combined)}")

# Save merged
with open('slot_providers.json', 'w') as f:
    json.dump(combined, f, indent=2)

print("\nUpdated slot_providers.json")
