import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]; out=sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 1440; h=int(sys.argv[4]) if len(sys.argv)>4 else 900
scheme=sys.argv[5] if len(sys.argv)>5 else 'light'
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':w,'height':h},color_scheme=scheme)
  msgs=[]; pg.on('console',lambda m: msgs.append(m.type+': '+m.text)); pg.on('pageerror',lambda e: msgs.append('ERR '+str(e)))
  pg.goto(url); pg.wait_for_timeout(1500)
  for a in sys.argv[6:]: exec(a)
  pg.screenshot(path=out); print('\n'.join(msgs[:20])); b.close()
