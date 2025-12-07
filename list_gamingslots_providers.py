import requests
from bs4 import BeautifulSoup
import re

def get_all_providers():
    """Get all providers from gamingslots.com"""
    
    # Try the main slots page which should have provider links
    url = "https://www.gamingslots.com/slots/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all provider links - they follow pattern /slots/PROVIDER-NAME/
    provider_links = soup.find_all('a', href=re.compile(r'^https://www\.gamingslots\.com/slots/[^/]+/$'))
    
    providers = set()
    for link in provider_links:
        href = link.get('href', '')
        match = re.search(r'/slots/([^/]+)/$', href)
        if match:
            slug = match.group(1)
            # Skip individual slot pages (they have -slot suffix)
            if not slug.endswith('-slot'):
                providers.add(slug)
    
    # Also check for provider mentions in the page
    all_links = soup.find_all('a', href=re.compile(r'/slots/[^/]+/'))
    for link in all_links:
        href = link.get('href', '')
        match = re.search(r'/slots/([^/]+)/', href)
        if match:
            slug = match.group(1)
            if not slug.endswith('-slot') and slug not in ['new-slots', 'popular-slots']:
                providers.add(slug)
    
    return sorted(providers)

if __name__ == "__main__":
    providers = get_all_providers()
    print(f"Found {len(providers)} providers on gamingslots.com:\n")
    for i, p in enumerate(providers, 1):
        print(f"{i:3}. {p}")
