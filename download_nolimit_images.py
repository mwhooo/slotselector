"""
Download NoLimit City images from official sources
"""
import requests
import json
import time
import os
import re

OUTPUT_DIR = "public/images"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
TIMEOUT = 30
PAUSE_EVERY = 5
PAUSE_SECONDS = 2

# Full list of NoLimit City games
GAMES = [
    "Mental", "San Quentin xWays", "Tombstone", "Tombstone RIP", "Fire in the Hole",
    "Fire in the Hole xBomb", "Fire in the Hole 2", "Deadwood", "Deadwood RIP",
    "Punk Rocker", "Punk Rocker xWays", "Remember Gulag", "Walk of Shame",
    "Karen Maneater", "Misery Mining", "El Paso Gunfight xNudge", "Serial",
    "True Grit Redemption", "Book of Shadows", "Tomb of Nefertiti", "Miner Donkey Trouble",
    "Thor Hammer Time", "Ice Ice Yeti", "Gaelic Gold", "Hot Nudge", "Pixies vs Pirates",
    "Barbarian Fury", "Poker Killer", "Bushido Ways xNudge", "DJ Psycho",
    "East Coast vs West Coast", "Infectious 5 xWays", "Das xBoot", "Das xBoot Zwei",
    "Folsom Prison", "Tombstone Slaughter", "Duck Hunters", "Nightmares vs Giggles",
    "xWays Hoarder xSplit", "Bonus Bunnies", "Casino Win Spin",
    "Kitchen Drama BBQ Frenzy", "Kitchen Drama Sushi Mania", "Fruits", "Tesla Jolt",
    "Starstruck", "Creepy Carnival", "Milky Ways",
    "Roadkill", "Golden Genie", "Owls", "Wixx", "Space Arcade", "The Border",
    "Warrior Graveyard", "Buffalo Hunter", "Blood and Shadow", "True Grit Redemption 2",
    "Hooligan Hustle", "Gluttony", "Bangkok Hilton", "The Cage", "The Crypt",
    "Disturbed", "Bizarre", "True Kult", "Whacked", "Bounty Hunters", "Breakout",
    "Gator Hunters", "Dead Men Walking", "Seamen", "Tsar Wars", "Brute Force Alien Onslaught",
    "Flight Mode", "Crazy Ex-Girlfriend", "Evil Goblins xBomb", "Prison Break",
    "Legion X", "Kiss My Chainsaw", "Disorder", "Duck Hunters Happy Hour",
    "Home of the Brave", "Stockholm Syndrome", "Blood and Shadow 2", "Dungeon Quest",
    "Brute Force", "Munchies", "xWays Hoarder 2", "Dead Dead Or Deader", "Little Bighorn",
    "Tombstone No Mercy", "Booze Cruise", "Jingle Balls", "Bull in a China Shop",
    "Outsmarted", "Sausage Party", "Bird Box", "Stayin Alive",
    # Additional games
    "Fire in the Hole 3", "Visitors", "Lottery", "Spirit of the Beast", "Punk Toilet",
    "Slayer Inc", "Techno Tumble"
]

def make_slug(name):
    """Convert game name to URL slug"""
    slug = name.lower()
    slug = slug.replace("'", "")
    slug = slug.replace(" ", "-")
    slug = re.sub(r'-+', '-', slug)
    return slug

def check_existing(slug):
    """Check if image already exists"""
    for ext in ['.png', '.jpg', '.webp']:
        if os.path.exists(os.path.join(OUTPUT_DIR, f"nolimitcity-{slug}{ext}")):
            return True
    return False

print("=" * 60)
print("Downloading NoLimit City images from official sources")
print("=" * 60)

# Try multiple CDN patterns for NoLimit City
# Their images are hosted on various CDNs
CDN_PATTERNS = [
    # Pattern 1: nolimitcity.com CDN
    "https://nolimitcity.com/images/games/{slug}/thumb.png",
    "https://nolimitcity.com/images/games/{slug}/thumb.jpg",
    # Pattern 2: playin.com CDN
    "https://playin.com/images/games/{slug}/thumb.png",
    # Pattern 3: Evolution/NLC CDN
    "https://static.evolutiongaming.com/nlc/games/{slug}/thumb.png",
    # Pattern 4: Alternative patterns
    "https://www.nolimitcity.com/wp-content/uploads/2023/{slug}.png",
]

downloaded = 0
failed = 0
already_exists = 0
slots_list = []

for i, game in enumerate(GAMES, 1):
    slug = make_slug(game)
    
    if check_existing(slug):
        print(f"[{i}/{len(GAMES)}] {game}... ✓ (already exists)")
        already_exists += 1
        slots_list.append(game)
        continue
    
    print(f"[{i}/{len(GAMES)}] {game}...", end=" ")
    
    # Try to find image from gamingslots individual page
    gs_url = f"https://www.gamingslots.com/slots/nolimitcity/{slug}-slot/"
    
    try:
        from bs4 import BeautifulSoup
        
        resp = requests.get(gs_url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            game_frame = soup.find('div', id='fpgame-frame')
            
            if game_frame:
                style = game_frame.get('style', '')
                img_match = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", style)
                
                if img_match:
                    img_url = img_match.group(1)
                    
                    # Determine extension
                    if '.webp' in img_url:
                        ext = '.webp'
                    elif '.png' in img_url:
                        ext = '.png'
                    else:
                        ext = '.jpg'
                    
                    filename = f"nolimitcity-{slug}{ext}"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    img_resp = requests.get(img_url, headers=HEADERS, timeout=TIMEOUT)
                    img_resp.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_resp.content)
                    
                    print(f"✓ {filename}")
                    downloaded += 1
                    slots_list.append(game)
                    
                    if i % PAUSE_EVERY == 0:
                        print(f"      ... pausing {PAUSE_SECONDS}s ...")
                        time.sleep(PAUSE_SECONDS)
                    continue
        
        print("✗ Not found on gamingslots.com")
        failed += 1
        
    except Exception as e:
        print(f"✗ {e}")
        failed += 1
    
    if i % PAUSE_EVERY == 0:
        time.sleep(PAUSE_SECONDS)

print("\n" + "=" * 60)
print(f"Already existed: {already_exists}")
print(f"Downloaded: {downloaded}")
print(f"Failed: {failed}")
print(f"Total available: {already_exists + downloaded}")
print("=" * 60)

# Save slots list
with open('nolimitcity_slots.json', 'w') as f:
    json.dump(slots_list, f, indent=2)
print(f"\n✓ Saved {len(slots_list)} slots to nolimitcity_slots.json")
