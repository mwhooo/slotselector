"""
Get full NoLimit City game list from official website
The games page uses client-side rendering, but we can try their game URLs
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

# Known NoLimit City games - comprehensive list
# Gathered from various sources
KNOWN_GAMES = [
    "Mental", "San Quentin xWays", "Tombstone", "Tombstone RIP", "Fire in the Hole",
    "Fire in the Hole xBomb", "Fire in the Hole 2", "Deadwood", "Deadwood RIP",
    "Punk Rocker", "Punk Rocker xWays", "Remember Gulag", "Walk of Shame",
    "Karen Maneater", "Misery Mining", "El Paso Gunfight xNudge", "Serial",
    "True Grit Redemption", "Book of Shadows", "Tomb of Nefertiti", "Miner Donkey Trouble",
    "Thor Hammer Time", "Ice Ice Yeti", "Gaelic Gold", "Hot Nudge", "Pixies vs Pirates",
    "Barbarian Fury", "Poker Killer", "Bushido Ways xNudge", "DJ Psycho",
    "East Coast vs West Coast", "Infectious 5 xWays", "Das xBoot", "Das xBoot Zwei",
    "Folsom Prison", "Tombstone Slaughter", "Duck Hunters", "Nightmares vs Giggles",
    "Dead or Alive", "xWays Hoarder xSplit", "Bonus Bunnies", "Casino Win Spin",
    "Kitchen Drama BBQ Frenzy", "Kitchen Drama Sushi Mania", "Fruits", "Tesla Jolt",
    "Casino Win Spin Freespins", "Starstruck", "Creepy Carnival", "Milky Ways",
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
    "Outsmarted", "Redemption's Gate", "Sausage Party", "Bird Box", "Stayin Alive"
]

print("=" * 60)
print("Known NoLimit City games list")
print("=" * 60)
print(f"\nTotal known games: {len(KNOWN_GAMES)}")
print("\nList:")
for i, game in enumerate(sorted(KNOWN_GAMES), 1):
    print(f"  {i:3d}. {game}")

# Now let's check what we already downloaded
OUTPUT_DIR = "public/images"
existing = [f for f in os.listdir(OUTPUT_DIR) if f.startswith('nolimitcity-')]
print(f"\n\nAlready downloaded: {len(existing)} images")

# Map existing files to game names
existing_games = set()
for f in existing:
    name = f.replace('nolimitcity-', '').rsplit('.', 1)[0]
    existing_games.add(name)

print(f"Existing slugs: {len(existing_games)}")

# Find missing
missing = []
for game in KNOWN_GAMES:
    slug = game.lower().replace(' ', '-').replace("'", "")
    if slug not in existing_games and slug.replace('xways', 'xways').replace('xbomb', 'xbomb') not in existing_games:
        missing.append(game)

print(f"\nMissing games: {len(missing)}")
for game in sorted(missing):
    print(f"  - {game}")
