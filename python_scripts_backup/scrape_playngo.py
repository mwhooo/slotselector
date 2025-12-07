#!/usr/bin/env python3
"""
Scrape Play'n GO slots using Selenium for JavaScript rendering
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

PROVIDER_NAME = "Play'n GO"

def get_all_playngo_slots():
    """Get all Play'n GO slots using Selenium"""
    slots = {}
    
    print("Starting Selenium browser...")
    
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome not available: {e}")
        print("Trying with Firefox...")
        options_ff = webdriver.FirefoxOptions()
        options_ff.add_argument('--headless')
        driver = webdriver.Firefox(options=options_ff)
    
    try:
        url = "https://www.gamingslots.com/slots/playn-go/"
        print(f"Loading {url}...")
        driver.get(url)
        
        # Wait for content to load
        print("Waiting for content to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
        )
        
        # Scroll to load lazy content
        print("Scrolling to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < 5:  # Limit scrolls to avoid infinite loops
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
        
        # Get page content
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all article elements containing slot games
        print("Parsing slot names...")
        found_games = set()
        
        articles = soup.find_all('article')
        print(f"Found {len(articles)} article elements")
        
        for article in articles:
            # Try to get title from various possible locations
            title_elem = article.find(['h3', 'h2', 'h1'])
            if title_elem:
                game_name = title_elem.get_text().strip()
                # Clean up the name
                game_name = game_name.replace(' slot', '').replace(' Slot', '').strip()
                if game_name and len(game_name) > 2 and game_name not in found_games:
                    found_games.add(game_name)
                    slots[game_name] = PROVIDER_NAME
        
        # Alternative: look for links with specific patterns
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/slots/playn-go/' in href and '-' in href:
                # Extract from URL
                slug = href.split('/slots/playn-go/')[-1].replace('/', '').replace('-slot', '').strip()
                if slug:
                    game_name = ' '.join(word.capitalize() for word in slug.split('-'))
                    if game_name and len(game_name) > 2 and game_name not in found_games:
                        found_games.add(game_name)
                        slots[game_name] = PROVIDER_NAME
        
        print(f"Found {len(found_games)} unique games")
        
    finally:
        driver.quit()
    
    return slots, found_games

if __name__ == "__main__":
    print(f"Starting Play'n GO scrape...\n")
    playngo_slots, game_names = get_all_playngo_slots()
    
    print(f"\n\nFound {len(playngo_slots)} Play'n GO slots:")
    for slot in sorted(playngo_slots.keys())[:15]:
        print(f"  - {slot}")
    if len(playngo_slots) > 15:
        print(f"  ... and {len(playngo_slots) - 15} more")
    
    if len(playngo_slots) > 0:
        # Save to temp file
        with open('playngo_slots_temp.json', 'w') as f:
            json.dump(playngo_slots, f, indent=2)
        print(f"\nSaved to playngo_slots_temp.json")
    else:
        print("No games found. Check the website structure.")
