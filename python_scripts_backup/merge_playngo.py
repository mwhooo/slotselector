#!/usr/bin/env python3
"""
Merge Play'n GO slots into the main database
"""
import json

# Load existing slots
with open('slot_providers.json', 'r') as f:
    slots = json.load(f)

# Load Play'n GO slots
with open('playngo_slots_temp.json', 'r') as f:
    playngo_data = json.load(f)

# Count existing providers
provider_counts = {}
for provider in slots.values():
    provider_counts[provider] = provider_counts.get(provider, 0) + 1

print("Current database:")
for provider, count in sorted(provider_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {provider}: {count}")
print(f"  Total: {len(slots)}\n")

# Add Play'n GO slots
added = 0
already_exists = 0

for slot_name in playngo_data.keys():
    if slot_name not in slots:
        slots[slot_name] = "Play'n GO"
        added += 1
    else:
        already_exists += 1
        print(f"  Already exists: {slot_name}")

print(f"\nAdded {added} new Play'n GO slots")
print(f"Skipped {already_exists} duplicates")

# Save updated database
with open('slot_providers.json', 'w') as f:
    json.dump(slots, f, indent=2)

# Print new counts
provider_counts = {}
for provider in slots.values():
    provider_counts[provider] = provider_counts.get(provider, 0) + 1

print("\nUpdated database:")
for provider, count in sorted(provider_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {provider}: {count}")
print(f"  Total: {len(slots)}")
