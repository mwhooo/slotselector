#!/usr/bin/env python3
"""Restore database to before the renaming and use a better approach"""
import json
from pathlib import Path

# Reload from the original merge
with open('slot_providers.json', 'r', encoding='utf-8') as f:
    slots = json.load(f)

# The issue is that some slots have duplicate names but different providers
# Example: "Alchemist Wonders" exists for both Pragmatic Play and Hacksaw Gaming
# When we renamed files, we overwrote Pragmatic with Hacksaw

# The solution: Keep the database as-is, but remove Red Tiger and Hacksaw 
# slots that are duplicates of Pragmatic slots

pragmatic_slots = set(k for k, v in slots.items() if v == 'Pragmatic Play')
red_tiger_slots = [k for k, v in slots.items() if v == 'Red Tiger']
hacksaw_slots = [k for k, v in slots.items() if v == 'Hacksaw Gaming']

slots_to_remove = []

print("Checking for duplicates...")
print("\nRed Tiger duplicates with Pragmatic:")
for rt_slot in red_tiger_slots:
    base_name = rt_slot.replace(' Slot', '')
    if base_name in pragmatic_slots:
        slots_to_remove.append(rt_slot)
        print(f"  - {rt_slot} (base: {base_name})")

print("\nHacksaw duplicates with Pragmatic:")
for hs_slot in hacksaw_slots:
    base_name = hs_slot.replace(' Slot', '')
    if base_name in pragmatic_slots:
        slots_to_remove.append(hs_slot)
        print(f"  - {hs_slot} (base: {base_name})")

print(f"\nRemoving {len(slots_to_remove)} duplicate slots...")
for slot in slots_to_remove:
    del slots[slot]

# Save updated database
with open('slot_providers.json', 'w', encoding='utf-8') as f:
    json.dump(dict(sorted(slots.items())), f, indent=2, ensure_ascii=False)

print(f"Updated database with {len(slots)} total slots")
