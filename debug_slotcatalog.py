import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

url = "https://slotcatalog.com/en/soft/Playson"

# Create a session
session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# First try - direct request
print("Trying direct request...")
response = session.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Headers received: {dict(response.headers)}")

if response.status_code == 403:
    print("\n403 Forbidden - checking response content...")
    print(f"Response length: {len(response.text)}")
    print(f"First 500 chars: {response.text[:500]}")
    
    # Check if it's Cloudflare or similar
    if 'cloudflare' in response.text.lower():
        print("\n>>> Cloudflare protection detected")
    elif 'captcha' in response.text.lower():
        print("\n>>> Captcha protection detected")
    elif 'ddos' in response.text.lower():
        print("\n>>> DDoS protection detected")
    
# Try with a referer
print("\n\nTrying with referer...")
headers['Referer'] = 'https://slotcatalog.com/en'
response = session.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")

# Try the homepage first
print("\n\nTrying homepage first, then provider page...")
session2 = requests.Session()
homepage_resp = session2.get("https://slotcatalog.com/en", headers=headers, timeout=30)
print(f"Homepage status: {homepage_resp.status_code}")
print(f"Cookies from homepage: {session2.cookies.get_dict()}")

headers['Referer'] = 'https://slotcatalog.com/en'
provider_resp = session2.get(url, headers=headers, timeout=30)
print(f"Provider page status: {provider_resp.status_code}")
