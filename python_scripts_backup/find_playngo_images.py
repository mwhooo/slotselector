#!/usr/bin/env python3
"""
Find actual image URLs for Play'n GO slots
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

def find_image_urls():
    """Scrape actual image URLs from the site"""
    
    print("Starting Selenium browser...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://www.gamingslots.com/slots/playn-go/"
        print(f"Loading {url}...")
        driver.get(url)
        
        # Wait for images to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )
        
        # Scroll to load lazy content
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(0.5)
        
        # Get all images
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        images = soup.find_all('img')
        print(f"\nFound {len(images)} images")
        
        # Look for image URLs in the page
        image_urls = {}
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src and alt and 'placeholder' not in src.lower():
                # Try to extract slot name from alt text
                if len(src) > 20:
                    image_urls[alt] = src
        
        print(f"Found {len(image_urls)} relevant images")
        
        # Print some examples
        for i, (alt, src) in enumerate(list(image_urls.items())[:5]):
            print(f"  [{i+1}] {alt}: {src[:80]}...")
        
        # Check for common URL patterns in the HTML
        print("\nSearching for image URL patterns...")
        import re
        
        # Find all URLs with wp-content
        urls = re.findall(r'https://[^\s"\'<>]+\.(?:jpg|png|jpeg)', driver.page_source)
        print(f"Found {len(urls)} image URLs")
        
        # Show unique domains
        domains = set()
        for u in urls:
            domain = '/'.join(u.split('/')[:4])
            domains.add(domain)
        
        print("Image domains:")
        for d in sorted(domains):
            print(f"  {d}")
        
        # Save all URLs for inspection
        with open('playngo_image_urls.txt', 'w') as f:
            for u in sorted(set(urls)):
                f.write(u + '\n')
        
        print("\nSaved all URLs to playngo_image_urls.txt")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    find_image_urls()
