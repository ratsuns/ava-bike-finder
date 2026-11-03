# Source

Everything the live site is built from.

- `site_tpl.html` - the page template (layout, styles, scripts)
- `shops_tpl.html` - the shops page template (shops.html: every shop as a card, next to a map)
- `build2.py` - builds the site: `SITE_DIR=.. python3 build2.py` writes index.html, shops.html, img/ and the icons to the repo root.
  Then, from the repo root, delete images nothing uses any more:
  `python3 -c "import os,re,glob; s=''.join(open(f).read() for f in ['index.html','shops.html']+glob.glob('data-*.js')); refs=set(re.findall(r'img/[\w\-.]+',s)); [os.remove('img/'+f) for f in os.listdir('img') if 'img/'+f not in refs]"`
- `shops.json`, `bikes.json`, `res_all.json`, `fill*.json`, `specs/` - bike and shop data
- `verify/` - checked photos, photo fixes, hero video, share card and icons
