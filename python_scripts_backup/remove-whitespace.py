import cv2
import numpy as np
import os
from pathlib import Path

def remove_whitespace_from_image(image_path, output_path):
    """
    Remove whitespace/light-colored borders from an image by detecting the bounding box
    of the actual content using Canny edge detection and contour analysis.
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to read {image_path}")
        return False
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Use Canny edge detection to find actual content
    edges = cv2.Canny(gray, 100, 200)
    
    # Dilate edges to connect nearby content
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    edges = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours of content
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback: use threshold-based approach
        _, binary = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print(f"⚠ {Path(image_path).name}: No content found, skipping")
        return False
    
    # Get the bounding rectangle that encompasses all content
    x_min, y_min = img.shape[1], img.shape[0]
    x_max, y_max = 0, 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)
    
    # Add minimal padding (2 pixels)
    padding = 2
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(img.shape[1], x_max + padding)
    y_max = min(img.shape[0], y_max + padding)
    
    # Skip if crop would be too small
    if (x_max - x_min) < 20 or (y_max - y_min) < 20:
        print(f"⚠ {Path(image_path).name}: Content too small after crop, skipping")
        return False
    
    # Crop the image
    cropped = img[y_min:y_max, x_min:x_max]
    
    # Save with high quality
    success = cv2.imwrite(output_path, cropped, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if success:
        original_size = os.path.getsize(image_path)
        new_size = os.path.getsize(output_path)
        size_reduction = (1 - (new_size / original_size)) * 100
        if size_reduction > 0.5:  # Only report if meaningful change
            print(f"[OK] {Path(image_path).name}: {original_size} -> {new_size} bytes ({size_reduction:.1f}% smaller)")
        else:
            print(f"[OK] {Path(image_path).name}: Cropped (minimal size change)")
        return True
    else:
        print(f"[FAIL] {Path(image_path).name}: Failed to write")
        return False

def process_all_slot_images():
    """
    Process all slot images in the public/images directory
    """
    images_dir = Path('public/images')
    if not images_dir.exists():
        print(f"Error: {images_dir} directory not found")
        return
    
    # Create backup directory
    backup_dir = images_dir / 'backup'
    backup_dir.mkdir(exist_ok=True)
    
    # Get all slot images
    slot_images = sorted(images_dir.glob('slot_*.jpg'))
    
    if not slot_images:
        print(f"No slot images found in {images_dir}")
        return
    print("Processing images to remove whitespace...\n")
    
    processed = 0
    failed = 0
    
    for image_path in slot_images:
        # Backup original
        backup_path = backup_dir / image_path.name
        if not backup_path.exists():
            import shutil
            shutil.copy2(image_path, backup_path)
        
        # Process image (overwrite original)
        if remove_whitespace_from_image(str(image_path), str(image_path)):
            processed += 1
        else:
            failed += 1
    
    print(f"\n[DONE] Successfully processed {processed} images")
    if failed > 0:
        print(f"[WARN] Failed to process {failed} images")
    print(f"Original images backed up to {backup_dir}")

if __name__ == '__main__':
    process_all_slot_images()
