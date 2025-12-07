import json

# Read existing slot providers
with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

# Read Relax Gaming slots
with open('relaxgaming_slots.txt', 'r') as f:
    relaxgaming_slots = [line.strip() for line in f if line.strip()]

# Clean and add to providers
current_count = len(providers)
added = 0

for slot in relaxgaming_slots:
    # Skip if already exists
    if slot not in providers:
        providers[slot] = "Relax Gaming"
        added += 1

# Save updated providers
with open('slot_providers.json', 'w') as f:
    json.dump(providers, f, indent=2)

print(f"Merged Relax Gaming slots:")
print(f"  Previous count: {current_count}")
print(f"  Added: {added}")
print(f"  Total now: {len(providers)}")
print(f"\nSlots by provider:")

# Count by provider
provider_counts = {}
for slot, provider in providers.items():
    if provider not in provider_counts:
        provider_counts[provider] = 0
    provider_counts[provider] += 1

for provider in sorted(provider_counts.keys()):
    print(f"  {provider}: {provider_counts[provider]}")
