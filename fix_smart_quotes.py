#!/usr/bin/env python3
"""Fix image filenames with smart quotes"""
import os
from pathlib import Path

img_dir = Path('public/images')

renamed = 0

# Iterate through all files
for file in sorted(img_dir.glob('*')):
    if file.is_file():
        # Replace character 8217 (right single quotation mark) with regular apostrophe
        new_name = file.name.replace('\u2019', "'")
        
        if new_name != file.name:
            new_path = file.parent / new_name
            
            # Only rename if target doesn't exist
            if not new_path.exists():
                file.rename(new_path)
                print(f"Renamed: {file.name} -> {new_name}")
                renamed += 1
            else:
                print(f"Skipped: {new_name} already exists")

print(f"\nTotal files renamed: {renamed}")
