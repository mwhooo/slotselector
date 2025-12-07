import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
import time
from urllib.parse import urljoin

def get_playson_slots_from_slotcatalog():
    """Scrape Playson slots from slotcatalog.com"""
    base_url = "https://slotcatalog.com/en/soft/Playson"
    
    # Create cloudscraper instance to bypass Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    slots = []
    page = 1
    max_pages = 20  # Safety limit
    
    while page <= max_pages:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}/{page}"
        
        print(f"Fetching page {page}: {url}")
        
        # Retry logic
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = scraper.get(url, timeout=60)
                if response.status_code == 404:
                    print(f"Page {page} not found, stopping")
                    break
                response.raise_for_status()
                break  # Success
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    print(f"Failed to fetch page {page} after {max_retries} attempts")
                    response = None
        
        if response is None or response.status_code == 404:
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find slot links - they have pattern like /en/slots/SLOT-NAME
        # Exclude links with #SlotRank suffix
        slot_links = soup.find_all('a', href=re.compile(r'/en/slots/[^/#]+$'))
        
        if not slot_links:
            print(f"No slots found on page {page}, stopping")
            break
        
        found_new = False
        for link in slot_links:
            href = link.get('href', '')
            # Extract slot name from URL
            match = re.search(r'/en/slots/([^/]+)$', href)
            if match:
                slug = match.group(1)
                # Convert slug to name
                name = slug.replace('-', ' ').replace('_', ' ')
                
                # Get the image if present
                img = link.find('img')
                img_src = img.get('src', '') if img else ''
                
                # Also try data-src for lazy loaded images
                if not img_src and img:
                    img_src = img.get('data-src', '')
                
                if name not in [s['name'] for s in slots]:
                    slots.append({
                        'name': name,
                        'slug': slug,
                        'url': f"https://slotcatalog.com{href}",
                        'image': img_src
                    })
                    found_new = True
                    print(f"  Found: {name}")
        
        print(f"Found {len(slots)} unique slots so far")
        
        # Check if there's a next page
        next_link = soup.find('a', text='next') or soup.find('a', href=re.compile(rf'/en/soft/Playson/{page+1}'))
        if not next_link and not found_new:
            print("No more pages, stopping")
            break
        
        page += 1
        time.sleep(1)  # Be nice to the server
    
    return slots, scraper

def download_slot_image(slot, output_dir, scraper):
    """Download image for a single slot from slotcatalog"""
    try:
        # First try the direct image from the list
        if slot.get('image') and 'slotcatalog.com' in slot['image']:
            img_url = slot['image']
            if not img_url.startswith('http'):
                img_url = f"https://slotcatalog.com{img_url}"
            
            img_response = scraper.get(img_url, timeout=30)
            if img_response.status_code == 200 and len(img_response.content) > 1000:
                ext = 'webp' if 'webp' in img_url else 'jpg'
                filename = f"{slot['slug'].replace('-', '_').lower()}.{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Downloaded from list: {filename}")
                return filename
        
        # Otherwise, fetch the slot page
        response = scraper.get(slot['url'], timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for slot images - they're often in figure or game-preview containers
        img_selectors = [
            'img[src*="userfiles/image/Game"]',
            '.game-preview img',
            '.slot-image img',
            'img[alt*="slot"]',
        ]
        
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img:
                img_url = img.get('src', '') or img.get('data-src', '')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin('https://slotcatalog.com', img_url)
                    
                    img_response = scraper.get(img_url, timeout=30)
                    if img_response.status_code == 200 and len(img_response.content) > 1000:
                        ext = 'webp' if 'webp' in img_url else 'jpg'
                        filename = f"{slot['slug'].replace('-', '_').lower()}.{ext}"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        print(f"Downloaded from page: {filename}")
                        return filename
        
        # Look for any game image
        imgs = soup.find_all('img', src=re.compile(r'Game|slot', re.I))
        for img in imgs:
            img_url = img.get('src', '') or img.get('data-src', '')
            if img_url and 'slotcatalog' in img_url:
                if not img_url.startswith('http'):
                    img_url = urljoin('https://slotcatalog.com', img_url)
                
                img_response = scraper.get(img_url, timeout=30)
                if img_response.status_code == 200 and len(img_response.content) > 1000:
                    ext = 'webp' if 'webp' in img_url else 'jpg'
                    filename = f"{slot['slug'].replace('-', '_').lower()}.{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"Downloaded: {filename}")
                    return filename
        
        print(f"No image found for: {slot['name']}")
        return None
        
    except Exception as e:
        print(f"Error downloading {slot['name']}: {e}")
        return None


def main():
    output_dir = "public/images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of Playson slots
    print("Fetching Playson slots from slotcatalog.com...")
    slots, scraper = get_playson_slots_from_slotcatalog()
    
    print(f"\nFound {len(slots)} Playson slots")
    
    # Save slots list for reference
    with open('playson_slotcatalog.json', 'w', encoding='utf-8') as f:
        json.dump(slots, f, indent=2, ensure_ascii=False)
    print(f"Saved slot list to playson_slotcatalog.json")
    
    # Download images
    print(f"\nDownloading images...")
    downloaded = []
    
    for i, slot in enumerate(slots):
        print(f"[{i+1}/{len(slots)}] Processing {slot['name']}...")
        filename = download_slot_image(slot, output_dir, scraper)
        if filename:
            downloaded.append({
                'name': slot['name'],
                'filename': filename
            })
        time.sleep(0.5)  # Be nice to the server
    
    print(f"\nDownloaded {len(downloaded)} images")
    
    # Update slot_providers.json
    providers_file = "slot_providers.json"
    if os.path.exists(providers_file):
        with open(providers_file, 'r') as f:
            providers = json.load(f)
    else:
        providers = {}
    
    # Add Playson entries
    for item in downloaded:
        providers[item['filename']] = "Playson"
    
    with open(providers_file, 'w') as f:
        json.dump(providers, f, indent=2)
    
    print(f"Updated {providers_file} with {len(downloaded)} Playson entries")
    
    return downloaded

if __name__ == "__main__":
    main()
