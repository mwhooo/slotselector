#!/usr/bin/env python3
"""Rebuild the complete slot_providers.json from all provider files."""

import json
from pathlib import Path

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_txt_as_dict(filepath, provider_name):
    """Load txt file with slot names (one per line) and convert to dict."""
    slots = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            slot_name = line.strip()
            if slot_name and not slot_name.startswith('#'):
                slots[slot_name] = provider_name
    return slots

def main():
    base_path = Path('.')
    
    # Start with empty dict
    all_slots = {}
    duplicates = {}
    
    # Load in order of priority (later loads take precedence for duplicates)
    
    # Load Pragmatic Play first (from current slot_providers.json)
    if (base_path / 'slot_providers.json').exists():
        print("Loading existing Pragmatic Play entries...")
        current = load_json('slot_providers.json')
        pragmatic_slots = {k: v for k, v in current.items() if v == 'Pragmatic Play'}
        all_slots.update(pragmatic_slots)
        print(f"  Loaded {len(pragmatic_slots)} Pragmatic Play slots")
    
    # Load NetEnt
    if (base_path / 'netent_slots.json').exists():
        print("Loading NetEnt...")
        netent = load_json('netent_slots.json')
        for k, v in netent.items():
            if k in all_slots:
                duplicates[k] = (all_slots[k], v)
            all_slots[k] = v
        print(f"  Added {len(netent)} NetEnt slots")
    
    # Load Hacksaw Gaming
    if (base_path / 'hacksaw_slots.json').exists():
        print("Loading Hacksaw Gaming...")
        hacksaw = load_json('hacksaw_slots.json')
        for k, v in hacksaw.items():
            if k in all_slots and all_slots[k] != v:
                duplicates[k] = (all_slots[k], v)
            all_slots[k] = v
        print(f"  Added {len(hacksaw)} Hacksaw Gaming slots")
    
    # Load Play'n GO
    if (base_path / 'playngo_slots_temp.json').exists():
        print("Loading Play'n GO...")
        playngo = load_json('playngo_slots_temp.json')
        for k, v in playngo.items():
            if k in all_slots and all_slots[k] != v:
                duplicates[k] = (all_slots[k], v)
            all_slots[k] = v
        print(f"  Added {len(playngo)} Play'n GO slots")
    
    # Load Red Tiger
    if (base_path / 'redtiger_slots.json').exists():
        print("Loading Red Tiger...")
        redtiger = load_json('redtiger_slots.json')
        for k, v in redtiger.items():
            if k in all_slots and all_slots[k] != v:
                duplicates[k] = (all_slots[k], v)
            all_slots[k] = v
        print(f"  Added {len(redtiger)} Red Tiger slots")
    
    # Load Relax Gaming
    if (base_path / 'relaxgaming_slots.txt').exists():
        print("Loading Relax Gaming...")
        relaxgaming = load_txt_as_dict('relaxgaming_slots.txt', 'Relax Gaming')
        for k, v in relaxgaming.items():
            if k in all_slots and all_slots[k] != v:
                duplicates[k] = (all_slots[k], v)
            all_slots[k] = v
        print(f"  Added {len(relaxgaming)} Relax Gaming slots")
    
    # Save merged file
    print(f"\nTotal slots: {len(all_slots)}")
    if duplicates:
        print(f"Duplicates found (kept last provider): {len(duplicates)}")
    
    # Sort by key for readability
    sorted_slots = dict(sorted(all_slots.items()))
    
    with open('slot_providers.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_slots, f, indent=2, ensure_ascii=False)
    
    print("Saved to slot_providers.json")
    
    # Count by provider
    providers = {}
    for slot, provider in sorted_slots.items():
        providers[provider] = providers.get(provider, 0) + 1
    
    print("\nProvider breakdown:")
    for provider, count in sorted(providers.items()):
        print(f"  {provider}: {count} slots")

if __name__ == '__main__':
    main()
