import json
from collections import Counter

with open('slot_providers.json', 'r') as f:
    providers = json.load(f)

counts = Counter(providers.values())
print(f"\n{'Provider':<25} {'Count':>6}")
print("-" * 35)
for provider, count in sorted(counts.items()):
    print(f"{provider:<25} {count:>6}")
print("-" * 35)
print(f"{'TOTAL':<25} {len(providers):>6}")
