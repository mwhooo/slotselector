import cloudscraper

url = "https://slotcatalog.com/en/soft/Playson"

# Create a cloudscraper instance
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

print("Trying with cloudscraper...")
try:
    response = scraper.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Success! Content length: {len(response.text)}")
        
        # Check if we got actual content
        if 'Playson' in response.text and 'slots' in response.text.lower():
            print("Got valid page content!")
            # Show first slot found
            from bs4 import BeautifulSoup
            import re
            soup = BeautifulSoup(response.text, 'html.parser')
            slot_links = soup.find_all('a', href=re.compile(r'/en/slots/[^/]+$'))
            print(f"Found {len(slot_links)} slot links")
            
            # Show first few
            for link in slot_links[:5]:
                print(f"  - {link.get('href')}")
        else:
            print("Page content doesn't seem right")
            print(f"First 500 chars: {response.text[:500]}")
    else:
        print(f"Error response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
