import json
from collections import Counter

with open('slot_providers.json', 'r') as f:
    data = json.load(f)

counts = Counter(data.values())
print("Providers and slot counts:")
for provider, count in counts.most_common():
    print(f"  {provider}: {count}")
