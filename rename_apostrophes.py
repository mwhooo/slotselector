#!/usr/bin/env python3
"""Rename image files to use regular apostrophes instead of smart quotes"""
import os
from pathlib import Path

img_dir = Path('public/images')

# Mapping of smart quote filenames to regular apostrophe filenames
files_to_rename = [
    ("Fishin' Reels.jpg", "Fishin' Reels.jpg"),
    ("Joker's Jewels.jpg", "Joker's Jewels.jpg"),
    ("Kraken's Sky Bounty.jpg", "Kraken's Sky Bounty.jpg"),
    ("Loki's Riches.jpg", "Loki's Riches.jpg"),
    ("Master Chen's Fortune.jpg", "Master Chen's Fortune.jpg"),
    ("Mr Tain's Fishing Adventures.jpg", "Mr Tain's Fishing Adventures.jpg"),
    ("Panda's Fortune.jpg", "Panda's Fortune.jpg"),
    ("Panda's Fortune 2.jpg", "Panda's Fortune 2.jpg"),
    ("Santa's Great Gifts.jpg", "Santa's Great Gifts.jpg"),
    ("Santa's Wonderland.jpg", "Santa's Wonderland.jpg"),
    ("Sugar Rush Valentine's Day.jpg", "Sugar Rush Valentine's Day.jpg"),
    ("Tundra's Fortune.jpg", "Tundra's Fortune.jpg"),
]

# List all files in images directory
for file in img_dir.iterdir():
    if file.is_file():
        # Check if filename contains a smart quote character
        if "'" in file.name or "'" in file.name:
            # Replace smart quote with regular apostrophe
            new_name = file.name.replace("'", "'").replace("'", "'")
            new_path = file.parent / new_name
            
            if new_path != file and not new_path.exists():
                file.rename(new_path)
                print(f"Renamed: {file.name} -> {new_name}")
            elif new_path.exists() and new_path != file:
                print(f"Skipped: {new_name} already exists")

print("\nDone! All filenames with smart quotes have been converted to regular apostrophes.")
