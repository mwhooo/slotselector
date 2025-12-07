import requests
from bs4 import BeautifulSoup
import re

# Scrape Relax Gaming slots from gamingslots.com
url = "https://www.gamingslots.com/slots/relax-gaming/"

print("Fetching Relax Gaming slots from gamingslots.com...")

try:
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all slot links
        slot_links = soup.find_all('a', href=re.compile(r'/slots/relax-gaming/[^/]+-slot/'))
        
        # Extract unique slot names
        slots = set()
        for link in slot_links:
            # Get the href and extract slot name from URL
            href = link.get('href')
            match = re.search(r'/slots/relax-gaming/([^/]+)-slot/', href)
            if match:
                slug = match.group(1)
                # Convert slug back to readable name
                name = slug.replace('-', ' ').title()
                slots.add(name)
        
        print(f"Found {len(slots)} unique Relax Gaming slots\n")
        
        # Print first 15 slots as sample
        sorted_slots = sorted(list(slots))
        print("First 15 slots:")
        for slot in sorted_slots[:15]:
            print(f"  - {slot}")
        
        if len(sorted_slots) > 15:
            print(f"  ... and {len(sorted_slots) - 15} more")
        
        # Save to file
        with open('relaxgaming_slots.txt', 'w') as f:
            for slot in sorted_slots:
                f.write(f"{slot}\n")
        
        print(f"\nSaved {len(slots)} slots to relaxgaming_slots.txt")
        
    else:
        print(f"Error: Status code {response.status_code}")
        print("Relax Gaming might not be available on gamingslots.com")

except Exception as e:
    print(f"Error: {e}")
