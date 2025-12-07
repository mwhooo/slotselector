import requests
from bs4 import BeautifulSoup
import re

def count_provider_slots(provider_slug):
    """Count slots for a provider on gamingslots.com"""
    url = f"https://www.gamingslots.com/slots/{provider_slug}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all slot links
    slot_links = soup.find_all('a', href=re.compile(rf'/slots/{provider_slug}/[^/]+-slot/'))
    
    slots = set()
    for link in slot_links:
        href = link.get('href', '')
        match = re.search(rf'/slots/{provider_slug}/([^/]+)/', href)
        if match:
            slots.add(match.group(1))
    
    return sorted(slots)

if __name__ == "__main__":
    for provider in ['netent', 'pragmatic-play']:
        slots = count_provider_slots(provider)
        print(f"\n{provider}: {len(slots)} slots")
        print(f"First 10: {slots[:10]}")
