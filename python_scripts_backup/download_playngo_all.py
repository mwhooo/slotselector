import json
import requests
import re
import time
from pathlib import Path
from PIL import Image
from io import BytesIO

with open('playngo_slots_temp.json') as f:
    slots = json.load(f)

print(f"Downloading {len(slots)} Play'n'GO slots\n")
ok, fail, notfound = 0, 0, 0

for i, (name, _) in enumerate(slots.items(), 1):
    slug = name.lower().replace("'","").replace("â€™","")
    slug = ''.join(c if c.isalnum() else '-' for c in slug)
    slug = '-'.join(slug.split())
    
    url = f'https://www.gamingslots.com/slots/playn-go/{slug}-slot/'
    
    path = Path(f'public/images/{name}.jpg')
    if path.exists():
        if i % 50 == 0:
            print(f'[{i}/{len(slots)}] {name}... [EXISTS]')
        continue
    
    if i % 50 == 0:
        print(f'[{i}/{len(slots)}] {name}...', end=' ')
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 404:
            if i % 50 == 0: 
                print('[404]')
            notfound += 1
        elif r.status_code == 200:
            m = re.findall(f'https://www.gamingslots.com/wp-content/uploads/[^"]+{slug}-slot-logo.jpg', r.text)
            if m:
                ir = requests.get(m[0], timeout=10)
                if ir.status_code == 200:
                    try:
                        img = Image.open(BytesIO(ir.content))
                        if img.mode != 'RGB': 
                            img = img.convert('RGB')
                        path.parent.mkdir(exist_ok=True)
                        img.save(path, 'JPEG', quality=85)
                        if i % 50 == 0: 
                            print('[OK]')
                        ok += 1
                    except:
                        if i % 50 == 0: 
                            print('[SAVE ERR]')
                        fail += 1
                else:
                    if i % 50 == 0: 
                        print('[DL FAIL]')
                    fail += 1
            else:
                if i % 50 == 0: 
                    print('[NO URL]')
                notfound += 1
        time.sleep(0.2)
    except: 
        if i % 50 == 0: 
            print('[ERR]')
        fail += 1

print(f'\n========================================')
print(f'OK: {ok}')
print(f'FAILED: {fail}')
print(f'NOT FOUND: {notfound}')
