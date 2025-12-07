import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

def get_playson_slots():
    """Scrape Playson slots from gamingslots.com"""
    base_url = "https://www.gamingslots.com/slots/playson/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    slots = []
    page = 1
    
    while True:
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"
        
        print(f"Fetching page {page}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 404:
                print(f"Page {page} not found, stopping")
                break
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all slot entries
        slot_links = soup.find_all('a', href=re.compile(r'/slots/playson/[^/]+-slot/'))
        
        if not slot_links:
            print(f"No slots found on page {page}, stopping")
            break
        
        found_new = False
        for link in slot_links:
            href = link.get('href', '')
            
            # Extract slot name from URL
            match = re.search(r'/slots/playson/([^/]+)-slot/', href)
            if match:
                slug = match.group(1)
                # Convert slug to name
                name = slug.replace('-', ' ').title()
                
                if name not in [s['name'] for s in slots]:
                    slots.append({
                        'name': name,
                        'slug': slug,
                        'url': href
                    })
                    found_new = True
        
        print(f"Found {len(slots)} unique slots so far")
        
        if not found_new:
            print("No new slots found, stopping")
            break
        
        page += 1
        time.sleep(1)  # Be nice to the server
    
    return slots

def download_slot_image(slot, output_dir):
    """Download image for a single slot"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    slot_url = slot['url']
    if not slot_url.startswith('http'):
        slot_url = f"https://www.gamingslots.com{slot_url}"
    
    try:
        response = requests.get(slot_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the game frame/image
        game_frame = soup.find('div', class_='game-frame')
        if game_frame:
            img = game_frame.find('img')
            if img and img.get('src'):
                img_url = img['src']
                if not img_url.startswith('http'):
                    img_url = f"https://www.gamingslots.com{img_url}"
                
                # Download image
                img_response = requests.get(img_url, headers=headers, timeout=30)
                img_response.raise_for_status()
                
                # Create filename
                filename = f"{slot['slug'].replace('-', '_')}.jpg"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Downloaded: {filename}")
                return filename
        
        # Alternative: look for main image
        main_img = soup.find('img', class_=re.compile(r'slot|game', re.I))
        if main_img and main_img.get('src'):
            img_url = main_img['src']
            if not img_url.startswith('http'):
                img_url = f"https://www.gamingslots.com{img_url}"
            
            img_response = requests.get(img_url, headers=headers, timeout=30)
            img_response.raise_for_status()
            
            filename = f"{slot['slug'].replace('-', '_')}.jpg"
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
    print("Fetching Playson slots from gamingslots.com...")
    slots = get_playson_slots()
    
    print(f"\nFound {len(slots)} Playson slots:")
    for slot in slots:
        print(f"  - {slot['name']}")
    
    # Download images
    print(f"\nDownloading images...")
    downloaded = []
    
    for i, slot in enumerate(slots):
        print(f"[{i+1}/{len(slots)}] Processing {slot['name']}...")
        filename = download_slot_image(slot, output_dir)
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
