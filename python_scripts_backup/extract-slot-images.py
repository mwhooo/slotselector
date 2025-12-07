#!/usr/bin/env python3
"""
Extract individual slot game images from a composite grid image.
Uses morphological operations to handle whitespace-separated tiles.
"""

import cv2
import numpy as np
import os
from pathlib import Path

# Create output directory
output_dir = Path('public/images')
output_dir.mkdir(parents=True, exist_ok=True)

# Get the next image number (find the highest existing slot number)
existing_files = list(output_dir.glob('slot_*.jpg'))
if existing_files:
    existing_nums = []
    for f in existing_files:
        try:
            num = int(f.stem.split('_')[1])
            existing_nums.append(num)
        except:
            pass
    start_num = max(existing_nums) + 1 if existing_nums else 1
else:
    start_num = 1

print(f"Starting image number: {start_num}")

# Find the image file (look for slots1.PNG first)
image_file = None
if Path('slots1.PNG').exists():
    image_file = Path('slots1.PNG')
elif Path('slots1.png').exists():
    image_file = Path('slots1.png')

if not image_file:
    print("slots1.PNG not found in project folder.")
    exit(1)

print(f"Found image: {image_file}")

# Read image
img = cv2.imread(str(image_file))
if img is None:
    print(f"Failed to read image: {image_file}")
    exit(1)

height, width = img.shape[:2]
print(f"Image size: {width}x{height}")

# Convert to HSV for better color detection
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Separate channels
h, s, v = cv2.split(hsv)

# Look for non-white/non-gray areas (high saturation or low value = colored content)
sat_mask = (s > 30).astype(np.uint8) * 255
dark_mask = (v < 245).astype(np.uint8) * 255

# Combine masks - areas that are colored or dark (game content)
content_mask = cv2.bitwise_or(sat_mask, dark_mask)

# Dilate to connect nearby pixels
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
content_mask = cv2.dilate(content_mask, kernel, iterations=2)

# Find contours on this mask
contours, _ = cv2.findContours(content_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter contours - each game tile should be a reasonable sized box
rects = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    area = w * h
    
    # Game tiles - lower threshold to catch smaller tiles
    if w > 75 and h > 75 and area > 5625:
        rects.append((x, y, w, h, area))

print(f"Found {len(rects)} potential slot tiles (before filtering)")

# Sort by area (largest first) and remove duplicates/overlaps
rects = sorted(rects, key=lambda r: r[4], reverse=True)

# Remove overlapping rectangles (keep larger ones)
final_rects = []
for rect in rects:
    x1, y1, w1, h1, area1 = rect
    overlaps = False
    for x2, y2, w2, h2, _ in final_rects:
        # Check if rectangles overlap significantly
        overlap_x = min(x1 + w1, x2 + w2) - max(x1, x2)
        overlap_y = min(y1 + h1, y2 + h2) - max(y1, y2)
        if overlap_x > 0 and overlap_y > 0:
            overlap_area = overlap_x * overlap_y
            if overlap_area > (area1 * 0.1):  # More than 10% overlap
                overlaps = True
                break
    if not overlaps:
        final_rects.append((x1, y1, w1, h1, area1))

# Sort by position (top-left to bottom-right)
final_rects = sorted(final_rects, key=lambda r: (r[1], r[0]))

print(f"After deduplication: {len(final_rects)} tiles")

# Extract and save individual slot images
for idx, (x, y, w, h, _) in enumerate(final_rects, start_num):
    # Minimal padding to preserve the tile
    padding = 2
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)
    
    slot_image = img[y1:y2, x1:x2]
    
    # Save slot image
    output_path = output_dir / f'slot_{idx:03d}.jpg'
    cv2.imwrite(str(output_path), slot_image)
    print(f"Saved: {output_path} ({w}x{h})")

print(f"\nExtracted {len(final_rects)} new slot images. Total slots now: {start_num + len(final_rects) - 1}")
