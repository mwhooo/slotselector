import cv2
import numpy as np
from pathlib import Path
import os

def extract_and_strip_whitespace(image, min_size=30):
    """
    Extract a single image and remove whitespace around it.
    Returns the cropped image or None if too small.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use Canny edge detection
    edges = cv2.Canny(gray, 100, 200)
    
    # Dilate to connect nearby content
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    edges = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback to threshold
        _, binary = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Get bounding box
    x_min, y_min = image.shape[1], image.shape[0]
    x_max, y_max = 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
    
    # Add minimal padding
    padding = 2
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(image.shape[1], x_max + padding)
    y_max = min(image.shape[0], y_max + padding)
    
    # Check size
    if (x_max - x_min) < min_size or (y_max - y_min) < min_size:
        return None
    
    return image[y_min:y_max, x_min:x_max]

def extract_slots_from_png(png_path, output_dir, start_index=144):
    """
    Extract slot tiles from a composite PNG using color-based detection
    and strip whitespace from each tile.
    """
    img = cv2.imread(png_path)
    if img is None:
        print(f"Error: Could not read {png_path}")
        return 0
    
    height, width = img.shape[:2]
    print(f"Image size: {width}x{height}")
    
    # Convert to HSV for color-based detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Detect tiles by looking for non-background pixels
    # Background is typically very light or white
    lower_bg = np.array([0, 0, 200])  # Light pixels in HSV
    upper_bg = np.array([180, 50, 255])
    
    # Create inverse mask (find non-background)
    bg_mask = cv2.inRange(hsv, lower_bg, upper_bg)
    fg_mask = cv2.bitwise_not(bg_mask)
    
    # Find contours of potential tiles
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Found {len(contours)} potential tiles")
    
    # Filter and extract tiles
    tiles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter by size (skip very small contours)
        if w < 50 or h < 50:
            continue
        
        # Extract tile
        tile = img[y:y+h, x:x+w].copy()
        tiles.append((tile, x, y, w, h))
    
    print(f"Extracted {len(tiles)} tiles after size filtering")
    
    # Sort by position (top to bottom, left to right)
    tiles.sort(key=lambda t: (t[2], t[1]))  # Sort by y, then x
    
    # Remove duplicates by comparing tile content
    unique_tiles = []
    for tile, x, y, w, h in tiles:
        is_duplicate = False
        for existing_tile in unique_tiles:
            # Resize both to same size for comparison
            tile_resized = cv2.resize(tile, (100, 100))
            existing_resized = cv2.resize(existing_tile, (100, 100))
            
            # Check if tiles are very similar
            diff = cv2.absdiff(tile_resized, existing_resized)
            if np.mean(diff) < 10:  # Similar enough
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_tiles.append(tile)
    
    print(f"Unique tiles after deduplication: {len(unique_tiles)}")
    
    # Save tiles with whitespace stripping
    saved_count = 0
    for idx, tile in enumerate(unique_tiles):
        # Strip whitespace
        stripped = extract_and_strip_whitespace(tile)
        if stripped is None:
            print(f"  Skipped tile {idx}: too small after stripping")
            continue
        
        # Save with sequential numbering
        slot_num = start_index + saved_count + 1
        filename = f"slot_{slot_num:03d}.jpg"
        filepath = Path(output_dir) / filename
        
        cv2.imwrite(str(filepath), stripped, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved_count += 1
        print(f"  Saved: {filename}")
    
    return saved_count

def main():
    png_path = Path("slots1.PNG")
    output_dir = Path("public/images")
    
    if not png_path.exists():
        print(f"Error: {png_path} not found")
        return
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup existing images first
    backup_dir = output_dir / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    # Find the highest numbered existing image to continue from
    existing_images = list(output_dir.glob("slot_*.jpg"))
    if existing_images:
        highest = max(int(f.stem.split('_')[1]) for f in existing_images)
        print(f"Found {len(existing_images)} existing images")
        print(f"Will continue numbering from slot_{highest + 1:03d}")
        start_index = highest
    else:
        start_index = 0
        print("No existing images found, starting from slot_001")
    
    print(f"\nExtracting new images from {png_path}...\n")
    
    new_count = extract_slots_from_png(str(png_path), str(output_dir), start_index=start_index)
    
    print(f"\n[DONE] Successfully extracted and saved {new_count} new images")
    print(f"New images saved to {output_dir}/")
    
    # Count total
    total = len(list(output_dir.glob("slot_*.jpg")))
    print(f"Total images now: {total}")

if __name__ == "__main__":
    main()
