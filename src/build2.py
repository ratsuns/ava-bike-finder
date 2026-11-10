"""Builds the whole site into SITE_DIR. Run from src/:  SITE_DIR=.. python3 build2.py

Reads the bike list (bikedata.py -> verify/cards.json), shops.json, site.json (site facts), the two page templates
(site_tpl.html, shops_tpl.html) and what they share (shared/), videos.csv (through videos/publish.py) and the files in verify/. Writes index.html,
browse-vendors/index.html, shops.html (a redirect), data-<hash>.js, videos-<hash>.json, img/, the share images,
icons, site.webmanifest, llms.txt, llms-full.txt and sitemap.xml, and removes site files nothing uses any more.
Needs Python 3 with Pillow and wordfreq 3.1.1 (pip install Pillow wordfreq==3.1.1), and Node with Playwright (for the vendor page's share card).
"""
import datetime, hashlib, html, json, os, re, shutil, subprocess, sys

from PIL import Image

import bikedata
from bikespecs.rules import shown_range
from videos.publish import write as write_videos

SITE = os.environ['SITE_DIR']
for tests in ('bikespecs.test_rules', 'videos.test_rules'):
    if subprocess.run([sys.executable, '-m', tests]).returncode: raise SystemExit(f'{tests} failed, nothing was built')

F = json.load(open('site.json'))
URL, NAME, LIGHT, DARK = F['url'], F['name'], F['theme']['light'], F['theme']['dark']
REBATE = F['rebate']['by_type']
# the Rebate window (shared/info.html) and the share text show cargo and adaptive as one amount
if REBATE['Cargo'] != REBATE['Adaptive']: raise SystemExit('site.json: Cargo and Adaptive rebates differ, but shared/info.html and the share text show them together; split them there first')
def money(n): return f'${n:,}'
def rebate(b): return REBATE[b['type']]['regular']
AMOUNTS = {**{t: money(r['regular']) for t, r in REBATE.items()}, **{t + '_income': money(r['income_qualified']) for t, r in REBATE.items()},
           'gear': money(F['rebate']['gear'])}
REBATE_FACTS = {**AMOUNTS, 'checked': F['rebate']['checked'], 'source': F['rebate']['source']}
FAQ = [(q, a.format(**AMOUNTS)) for q, a in F['faq'].items()]
e = html.escape
TODAY = datetime.date.today()

os.makedirs(SITE + '/img', exist_ok=True)
IMG = set()   # every file the build puts in img/; anything else there is removed at the end
def put_img(name, src):
    shutil.copy(src, f'{SITE}/img/{name}'); IMG.add(name); return f'img/{name}'
# photo file names say what they show plus a short code from the photo itself, so a name only changes when the
# photo changes (browsers only re-download changed photos)
def photo(name):
    src = f'verify/cardphotos/{name}.webp'
    return put_img(f"{name}-{hashlib.md5(open(src, 'rb').read()).hexdigest()[:8]}.webp", src)

# ---- shops: one entry per shop location (some shops are listed under two or three names; those share one entry)
S = json.load(open('shops.json'))
for s in S.values():
    if s.get('logo'): s['logo'] = put_img(f"logo-{s['logo']}.webp", f"verify/shoplogos/{s['logo']}.webp")
LOCS = {}
for k, s in S.items():
    if s.get('lat') is None: raise SystemExit(f'shops.json, {k}: no map location (lat/lng)')
    LOCS.setdefault((s['name'], s.get('address')), dict(k=k, **{f: s[f] for f in ('name', 'address', 'city', 'phone', 'url', 'email', 'contact', 'hours', 'lat', 'lng', 'logo') if s.get(f) is not None}))
SHL = list(LOCS.values())
BY_CITY = sorted(SHL, key=lambda x: (x.get('city') or '', x['name']))
STORES = []   # every shop for Google (structured data), used by both pages
for s in BY_CITY:
    d = {"@type": "BikeStore", "name": s['name'], "address": {"@type": "PostalAddress", "streetAddress": s.get('address'), "addressLocality": s.get('city'), "addressRegion": "CA", "addressCountry": "US"}, "geo": {"@type": "GeoCoordinates", "latitude": s['lat'], "longitude": s['lng']}}
    for a, b in (('phone', 'telephone'), ('url', 'url'), ('email', 'email')):
        if s.get(a): d[b] = s[a]
    if s.get('logo'): d["logo"] = d["image"] = URL + s['logo']
    STORES.append(d)

# ---- bikes
def bike(c):
    bad = [s for s in c['shops'] if s not in S]
    if bad: raise SystemExit(f"{c['id']}: shops not in shops.json: {bad}")
    if c['type'] not in REBATE: raise SystemExit(f"{c['id']}: type {c['type']!r} has no rebate in site.json")
    for x in c['cv']:
        if not x.get('f'): raise SystemExit(f"{c['id']}: color {x['n']!r} has no color family (f)")
    cv = [dict(n=x['n'], f=x['f'], hex=x.get('hex'), img=photo(x['img']) if x.get('img') else None) for x in c['cv']]
    b = dict(id=c['id'], brand=c['brand'], model=c['model'], type=c['type'], fold=c.get('fold'), cls=c.get('cls'), price=c.get('price'),
             note=c.get('pnote'), motor=c.get('motor'), tq=c.get('tq'), spd=c.get('spd'), wh=c.get('wh'), range=shown_range(c.get('range')),
             load=c.get('load'), height=c.get('height'), wt=c.get('wt'), src=c.get('src'), img=photo(c['img']) if c.get('img') else None,
             shops=c['shops'], cv=cv, st=c.get('st'))
    b['you'] = max(b['price'] - rebate(b), 0) if b['price'] is not None else None   # what you pay after the regular rebate
    if c.get('wtnb'): b['wtnb'] = True
    return b
out = [bike(c) for c in bikedata.load()]
print('bikes', len(out), 'priced', sum(1 for o in out if o['price']))

# ---- the home page
HM, HJ = put_img('hero.mp4', 'verify/hero.mp4'), put_img('hero.jpg', 'verify/hero.jpg')
# the published page keeps the bike list in its own file, so the page itself stays small and link previews
# (Messages, Slack, X) can read it; the list loads right after, before the page script runs.
# window.AVA_SITE holds the site facts (site.json, FAQ amounts filled in) for the page scripts.
FACTS = {**F, 'faq': dict(FAQ)}
DJ = 'window.AVA_B=' + json.dumps(out, separators=(',', ':')) + ';window.AVA_S=' + json.dumps(S, separators=(',', ':')) + ';window.AVA_SITE=' + json.dumps(FACTS, separators=(',', ':')) + ';'
DN = 'data-' + hashlib.md5(DJ.encode()).hexdigest()[:8] + '.js'
open(os.path.join(SITE, DN), 'w').write(DJ)
# video reviews: src/videos.csv is the one list; videos/publish.py checks every video against its bike (the build stops
# on any problem) and writes them to their own small file that the page loads after it's up
VN = write_videos(SITE, [o['id'] for o in out])
# plain-text copy of the list for search engines and browsers that don't run the page script
_grp = {}
for b in out: _grp.setdefault(b['brand'], []).append(b)
_li = []
for br in sorted(_grp, key=str.lower):
    items = []
    for b in sorted(_grp[br], key=lambda x: x['model'].lower()):
        bits = [b.get('type') or '']
        if b.get('cls'): bits.append(f"Class {b['cls']}")
        if b.get('price'): bits.append(f"${b['price']:,} list, about ${b['you']:,} after the ${rebate(b)} rebate")
        items.append(f"<li>{e(br + ' ' + b['model'])} ({e(', '.join(x for x in bits if x))})</li>")
    _li.append(f"<h3>{e(br)}</h3><ul>{''.join(items)}</ul>")
NOS = f'<noscript><div class="wrap"><h2>All {len(out)} e-bikes on the Ava rebate list</h2>{"".join(_li)}</div></noscript>'

# ---- the page templates: __NAME__ marks where the build puts something in
def fill(text, **vals):
    used = set()
    def put(m): used.add(m.group(1)); return vals[m.group(1)]
    text = re.sub(r'__([A-Z][A-Z0-9_]*)__', put, text)
    assert used == set(vals), f'not in the template: {set(vals) - used}'
    return text
# what both pages share (shared/): styles, the nav, the E-bike guide and Rebate info windows (amounts from site.json), scripts
def shared(name, **vals): return fill(open('shared/' + name).read().rstrip('\n'), **vals)
def nav(here): return shared('nav.html', HOME='./' if here else '#top', HERE=' aria-current="page"' if here else '')
INFO = re.sub(r'\{(\w+)\}', lambda m: REBATE_FACTS[m.group(1)], shared('info.html'))
SHARED_JS = shared('shop.js') + '\n' + shared('page.js', THEME=json.dumps(F['theme']))
BOTH = dict(CSS=shared('page.css', LIGHT=LIGHT, DARK=DARK), INFO=INFO, SHARED_JS=SHARED_JS, SCROLLBAR=shared('scrollbar.html'))
PAGE = fill(open('site_tpl.html').read(), **BOTH, NAV=nav(False), DATA_JS=DN, HERO_MP4=HM, HERO_JPG=HJ, VIDS=VN, NOSCRIPT=NOS,
            AVA_SRC=F['rebate']['source'], AUTHOR=F['author']['name'], CITY=F['author']['city'])

# ---- what both pages' <head> share
# the share image gets a content hash in its name, so every change is a new URL that apps and the CDN fetch fresh
def share_image(src, prefix):
    name = prefix + hashlib.md5(open(src, 'rb').read()).hexdigest()[:8] + '.jpg'
    shutil.copy(src, f'{SITE}/{name}'); return name
def head_start(base=''):
    return ('<!doctype html><html lang="en" data-theme="dark" data-overlayscrollbars-initialize><head><meta charset="utf-8">' + base + '<link rel="stylesheet" href="vendor/overlayscrollbars-2.16.0.min.css">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark"><meta name="theme-color" content="{DARK}">')
# phones, tablets and touch screens keep the device's own scrollbar: the page's OverlayScrollbars flag comes off here, before
# the first paint (shared/scrollbar.html reads it)
THEME_JS = ('try{if(!matchMedia("(hover: hover) and (pointer: fine)").matches||matchMedia("(any-pointer: coarse)").matches)document.documentElement.removeAttribute("data-overlayscrollbars-initialize");'
            f'var t=localStorage.getItem("theme");if(t==="light"){{document.documentElement.dataset.theme="light";document.querySelector("meta[name=color-scheme]").content="light";document.querySelector("meta[name=theme-color]").content="{LIGHT}"}}}}catch(e){{}}')
def page_tags(title, desc, url):
    return (f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">'
            '<meta name="robots" content="index,follow,max-image-preview:large"><meta name="msvalidate.01" content="E92F479E5202458908C55622B28B718F">'
            '<link rel="icon" href="favicon.ico" sizes="48x48"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="manifest" href="site.webmanifest"><link rel="alternate" type="text/markdown" title="Full bike and shop list" href="llms-full.txt">')
def share_tags(url, title, desc, image, alt, short_alt, video=''):
    return (f'<meta property="og:type" content="website"><meta property="og:site_name" content="{e(NAME)}"><meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">'
            f'<meta property="og:image" content="{URL}{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="{e(alt)}"><meta property="og:locale" content="en_US">'
            + video +
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{URL}{image}"><meta name="twitter:image:alt" content="{e(short_alt)}">')
def ld_script(ld): return '<script type="application/ld+json">' + json.dumps(ld, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/') + '</script>'
WEBSITE = {"@type": "WebSite", "@id": URL + "#site", "name": NAME, "url": URL}
SHOPS_LD_NAME = 'Shops that accept the Ava e-bike rebate'

# ---- home page <head>
OGN = share_image('verify/seo/og.jpg', 'og-')
TITLE = 'E-bike Rebate Finder: Every Ava-Eligible E-Bike, Price and Shop'
DESC = f"All {len(out)} e-bikes on Ava Community Energy's rebate list for {F['area']}. See your price after the {AMOUNTS['Standard']} or {AMOUNTS['Cargo']} rebate and find a shop."
ME = {"@type": "Person", "@id": URL + "#chris", "name": F['author']['name'], "address": {"@type": "PostalAddress", "addressLocality": F['author']['city'], "addressRegion": "CA"}}
LD = {"@context": "https://schema.org", "@graph": [
    {**WEBSITE, "description": DESC, "inLanguage": "en-US", "publisher": {"@id": URL + "#chris"}, "copyrightHolder": {"@id": URL + "#chris"}, "copyrightYear": 2026},
    {"@type": "WebPage", "@id": URL, "url": URL, "name": TITLE, "description": DESC, "isPartOf": {"@id": URL + "#site"}, "author": {"@id": URL + "#chris"}, "dateModified": TODAY.isoformat(), "about": {"@type": "Thing", "name": "Ava Community Energy e-bike rebate"}, "primaryImageOfPage": URL + OGN},
    ME,
    {"@type": "FAQPage", "@id": URL + "#faq", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    {"@type": "Dataset", "name": "E-bikes eligible for the Ava Community Energy rebate", "description": f"All {len(out)} e-bikes on Ava's eligible list with maker price, price after the rebate, class, type, motor, battery, range, weight and the shops that sell each one.", "url": URL, "dateModified": TODAY.isoformat(), "creator": {"@id": URL + "#chris"}, "isAccessibleForFree": True, "license": URL + "#copyright", "distribution": [{"@type": "DataDownload", "encodingFormat": "text/markdown", "contentUrl": URL + "llms-full.txt"}]},
    {"@type": "ItemList", "name": SHOPS_LD_NAME, "numberOfItems": len(STORES), "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": x} for i, x in enumerate(STORES)]}]}
_hero_video = (f'<meta property="og:video" content="{URL}{HM}"><meta property="og:video:secure_url" content="{URL}{HM}"><meta property="og:video:type" content="video/mp4"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">')
_tagline = 'Find your e-bike with the Ava rebate'
SEO = (page_tags(TITLE, DESC, URL)
       + share_tags(URL, _tagline, DESC, OGN, f"{NAME}: {_tagline}. {AMOUNTS['Cargo']} off cargo and adaptive, {AMOUNTS['Standard']} off standard.", f'{NAME}: {_tagline}.', _hero_video)
       + ld_script(LD))
open(SITE + '/index.html', 'w').write(head_start() + SEO + '<script>if(location.hash==="#dir")location.replace("browse-vendors/");' + THEME_JS + '</script><script type="speculationrules">{"prefetch":[{"where":{"href_matches":"*browse-vendors/*"},"eagerness":"moderate"}]}</script><script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments);};</script><script defer src="/_vercel/insights/script.js"></script></head><body data-overlayscrollbars-initialize style="margin:0">' + PAGE + '</body></html>')

# ---- icons, manifest, llms files (llmstxt.org: plain markdown for AI assistants)
for f in ['favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'fav-192.png', 'fav-512.png']: shutil.copy('verify/seo/' + f, SITE + '/' + f)
json.dump({"name": NAME, "short_name": F['short_name'], "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#000000", "theme_color": DARK,
           "icons": [{"src": "fav-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "fav-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "fav-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, open(SITE + '/site.webmanifest', 'w'))
_hdr = f"""# {NAME}

> Every e-bike on Ava Community Energy's e-bike rebate list ({len(out)} bikes), with each bike's price, the price after the rebate, specs and the shops that sell it. Made by {F['author']['name']} in {F['author']['city']}, CA. Not affiliated with Ava Community Energy. Updated {TODAY.strftime('%B %-d, %Y')}.

## The rebate (source: {F['rebate']['source']}, checked {F['rebate']['checked']})

""" + "\n".join(f"- **{q}** {a}" for q, a in FAQ) + f"""

## Files

- [Full bike and shop list](llms-full.txt): every bike with price, price after rebate, class, specs and shops, plus every shop's address, phone, hours and website.
- [Website]({URL}): search and filter the list.
"""
open(SITE + '/llms.txt', 'w').write(_hdr)
_rows = ["| Bike | Type | Class | Price | After rebate | Motor | Battery | Range | Weight | Status | Shops |", "|---|---|---|---|---|---|---|---|---|---|---|"]
def _c(v): return str(v).replace('|', '/') if v not in (None, '') else ''
for b in sorted(out, key=lambda x: (x['brand'].lower(), x['model'].lower())):
    p = b.get('price')
    _rows.append('| ' + ' | '.join([_c(b['brand'] + ' ' + b['model']), _c(b.get('type')), _c(b.get('cls')), f"${p:,}" if p else 'not listed', f"${b['you']:,}" if p else '', _c(b.get('motor')), f"{b['wh']} Wh" if b.get('wh') else '', f"{b['range']} mi" if b.get('range') else '', (f"{b['wt']} lb" + (' (no battery)' if b.get('wtnb') else '')) if b.get('wt') else '', F['status'][b['st']]['llms'] if b.get('st') else 'Available', _c(', '.join(S[k]['name'] for k in b['shops']))]) + ' |')
_shops = [f"### {s['name']} ({s.get('city', '')})\n" + "\n".join(f"- {k}: {v}" for k, v in (('Address', (s.get('address') or '') + (', ' + s['city'] if s.get('city') else '') + ', CA'), ('Phone', s.get('phone')), ('Hours', s.get('hours')), ('Email', s.get('email')), ('Website', s.get('url'))) if v) for s in BY_CITY]
_notes = f"## Notes\n\n- \"After rebate\" uses the regular {AMOUNTS['Standard']} (standard) or {AMOUNTS['Cargo']} (cargo and adaptive) rebate. Sales tax is extra.\n- Prices are the maker's US list price, or the selling shop's price when the maker has none.\n\n## Files"
open(SITE + '/llms-full.txt', 'w').write(_hdr.replace('## Files', _notes, 1) + f"\n## All {len(out)} e-bikes\n\n" + "\n".join(_rows) + "\n\n## Participating shops\n\n" + "\n\n".join(_shops) + "\n")

# ---- browse-vendors/: every shop location as the home page's shop card, next to a map with a pin per shop
SURL = URL + 'browse-vendors/'
STITLE = f'Participating Shops for the Ava E-Bike Rebate | {NAME}'
SDESC = f"All {len(SHL)} shops that take the Ava Community Energy e-bike rebate in {F['area']}, on a map with each address, phone number and opening hours."
# the vendor page's own share card is a picture of the page itself (made by verify/seo/og-vendors-shot.js, see below)
OGV = share_image('verify/seo/og-vendors.jpg', 'og-vendors-')
_OGV_ALT = f'{NAME} vendor directory: the list of shops that take the Ava e-bike rebate next to a map with a pin for each shop.'
SLD = {"@context": "https://schema.org", "@graph": [
    {"@type": "CollectionPage", "@id": SURL, "url": SURL, "name": STITLE, "description": SDESC, "inLanguage": "en-US", "isPartOf": {"@id": URL + "#site"}, "breadcrumb": {"@id": SURL + "#crumbs"}, "primaryImageOfPage": URL + OGV, "dateModified": TODAY.isoformat(), "mainEntity": {"@id": SURL + "#shops"}},
    {"@type": "BreadcrumbList", "@id": SURL + "#crumbs", "itemListElement": [{"@type": "ListItem", "position": 1, "name": NAME, "item": URL}, {"@type": "ListItem", "position": 2, "name": "Browse vendors", "item": SURL}]},
    WEBSITE,
    {"@type": "ItemList", "@id": SURL + "#shops", "name": SHOPS_LD_NAME, "numberOfItems": len(STORES), "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": x} for i, x in enumerate(STORES)]}]}
SOG = share_tags(SURL, 'Every shop that takes the Ava e-bike rebate', SDESC, OGV, _OGV_ALT, _OGV_ALT)
MAP_STYLE = 'https://tiles.openfreemap.org/styles/bright'   # OSM Bright, in both themes
# the page lives at browse-vendors/ (clean address); every relative link in it resolves from the site root
SHEAD = (head_start('<base href="../">') + page_tags(STITLE, SDESC, SURL) + SOG +
     '<script type="speculationrules">{"prefetch":[{"where":{"selector_matches":"a.brand, a[href=\\"./\\"]"},"eagerness":"moderate"}]}</script>'
     '<link rel="preconnect" href="https://tiles.openfreemap.org" crossorigin>'
     # the map's tile index, style, icons and label fonts start downloading right away, in parallel, instead of one
     # after another once the map program has read the style (sharp icons on high-density screens, like the map itself)
     '<link rel="preload" as="fetch" crossorigin href="https://tiles.openfreemap.org/planet">'
     '<script>(()=>{const r=Math.min(devicePixelRatio||1,2)>1?"@2x":"",b="https://tiles.openfreemap.org/";["sprites/ofm_f384/ofm"+r+".json","sprites/ofm_f384/ofm"+r+".png","fonts/Noto%20Sans%20Regular/0-255.pbf","fonts/Noto%20Sans%20Italic/0-255.pbf"].forEach(u=>{const l=document.createElement("link");l.rel="preload";l.as="fetch";l.crossOrigin="anonymous";l.href=b+u;document.head.append(l)})})()</script>'
     f'<script>{THEME_JS}(function(){{var l=document.createElement("link");l.rel="preload";l.as="fetch";l.crossOrigin="anonymous";l.href="{MAP_STYLE}";document.head.appendChild(l)}})()</script>'
     # the map's stylesheet downloads in parallel but never holds up the cards: it's applied when it arrives, and the map starts once it's in
     '<link rel="preload" as="style" href="vendor/maplibre-gl-5.24.0.min.css" onload="this.onload=null;this.rel=\'stylesheet\';window.MLCSS=1;document.dispatchEvent(new Event(\'mlcss\'))" onerror="window.MLCSS=1;document.dispatchEvent(new Event(\'mlcss\'))"><script defer src="vendor/maplibre-gl-5.24.0.min.js"></script>'
     '<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments);};</script><script defer src="/_vercel/insights/script.js"></script>')
# the shop list is put into the page at build time, so it shows at once and search engines see every shop without running the
# page. It is made by the pages' own card code (shared/shop.js, run here in Node), which also puts the shops in their order
_r = subprocess.run(['node', '-e', open('shared/shop.js').read() + '\nconst SH=' + json.dumps(SHL) + ';SH.sort(shopOrder);process.stdout.write(JSON.stringify({sh:SH,list:shopList(SH)}))'],
                    capture_output=True, text=True, check=True)
_sp = json.loads(_r.stdout)
assert _sp['list'].count('class="shop"') == len(SHL), 'prerendered shop list'
SP = fill(open('shops_tpl.html').read(), **BOTH, HEAD=SHEAD, NAV=nav(True), COUNT=str(len(SHL)), WORLD=open('worlddots.json').read().strip(), MAP_STYLE=MAP_STYLE,
          SHOPS=json.dumps(_sp['sh'], separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/'), SHOP_LIST=_sp['list'])
# the structured data goes at the end of the page, so it never delays the first paint (search engines read it anywhere)
assert SP.rstrip().endswith('</body></html>')
SP = SP.rstrip()[:-len('</body></html>')] + ld_script(SLD) + '</body></html>'
os.makedirs(SITE + '/browse-vendors', exist_ok=True); open(SITE + '/browse-vendors/index.html', 'w').write(SP)
# the old shops.html address forwards to browse-vendors/ (keeping any #part of the link)
open(SITE+'/shops.html','w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(STITLE)}</title><meta name="description" content="{e(SDESC)}"><link rel="canonical" href="{SURL}"><meta name="robots" content="noindex">{SOG}<meta http-equiv="refresh" content="0;url=browse-vendors/"><script>location.replace("browse-vendors/"+location.search+location.hash)</script></head><body><a href="browse-vendors/">Participating shops</a></body></html>')
print('browse-vendors', len(SHL), 'locations', len(SP), 'bytes')

# ---- "last updated" dates (sitemap, the pages' structured data, llms.txt) are the day a page's content last changed, not
# the build day. A page's fingerprint is its words, its structured data and its data file (dates left out), so code and
# style changes don't count as content changes. Fingerprints and dates are kept in verify/seo/lastmod.json (committed with the site)
_iso, _long = TODAY.isoformat(), TODAY.strftime('%B %-d, %Y')
def undated(s): return s.replace(_iso, '@D').replace(_long, '@D')
def _fp(s):
    s = undated(s)
    ld = ''.join(re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S))
    data = ''.join(re.findall(r'data-[0-9a-f]{8}\.js', s))
    txt = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', '', s, flags=re.S); txt = re.sub(r'<[^>]+>', ' ', txt); txt = re.sub(r'\s+', ' ', txt)
    return hashlib.sha256((txt + ld + data).encode()).hexdigest()

# the vendor page's share card is a picture of the page itself, so it is re-made whenever the page changes
# (shop list, count, wording, layout). og-vendors-map.jpg is the real map behind the pins, captured in a browser;
# the build warns when the page's map view no longer matches it (for example a different first shop)
_OGJ = 'verify/seo/og-vendors.json'; _og = json.load(open(_OGJ)) if os.path.exists(_OGJ) else {}
_pg = undated(SP.replace(OGV, 'OGV'))
_ogfp = hashlib.sha256((_pg + ''.join(hashlib.md5(open('verify/seo/' + x, 'rb').read()).hexdigest() for x in ('og-vendors-shot.js', 'og-vendors-map.jpg', 'Geist-Variable.woff2'))).encode()).hexdigest()
if _og.get('fp') != _ogfp:
    _r = subprocess.run(['node', 'verify/seo/og-vendors-shot.js', os.path.abspath(SITE), 'shot'], capture_output=True, text=True)
    if _r.returncode: raise SystemExit('the vendor share card has to be re-shot (the shops page changed), and that failed.\n'
                                       'It needs Node with Playwright and Chromium (npm i playwright; npx playwright install chromium).\n' + _r.stderr[-2000:])
    _view = json.loads(_r.stdout.strip().splitlines()[-1])
    Image.open('verify/seo/og-vendors.png').convert('RGB').resize((1200, 630), Image.LANCZOS).save('verify/seo/og-vendors.jpg', quality=90, optimize=True, progressive=True)
    os.remove('verify/seo/og-vendors.png')
    _m = _og.get('map')
    if _m and (abs(_view['c']['lng'] - _m['lng']) > 1e-6 or abs(_view['c']['lat'] - _m['lat']) > 1e-6 or _view['z'] != _m['zoom'] or _view['w'] != _m['w']):
        print('WARNING: the vendor share card map photo (verify/seo/og-vendors-map.jpg) no longer matches the page map view', _view, '- re-capture it')
    _og = {'fp': _ogfp, 'map': _m or {'lng': _view['c']['lng'], 'lat': _view['c']['lat'], 'zoom': _view['z'], 'w': _view['w'], 'h': _view['h']}}
    json.dump(_og, open(_OGJ, 'w'), indent=1)
    _new = share_image('verify/seo/og-vendors.jpg', 'og-vendors-')
    if _new != OGV:
        for _x in ('browse-vendors/index.html', 'shops.html'):
            _p = SITE + '/' + _x; _s = open(_p).read(); open(_p, 'w').write(_s.replace(OGV, _new))   # read before 'w' empties the file
        OGV = _new
    print('vendor share card re-made:', OGV)

_LMF = 'verify/seo/lastmod.json'; _LM = json.load(open(_LMF)) if os.path.exists(_LMF) else {}
_dates = {}
for _f, _u in (('index.html', URL), ('browse-vendors/index.html', SURL), ('llms.txt', URL + 'llms.txt'), ('llms-full.txt', URL + 'llms-full.txt')):
    _p = SITE + '/' + _f; _s = open(_p).read(); _h = _fp(_s); _o = _LM.get(_u)
    if not _o or _o['fp'] != _h: _o = _LM[_u] = {'fp': _h, 'date': _iso}
    _d = datetime.date.fromisoformat(_o['date']); _dates[_u] = _o['date']
    open(_p, 'w').write(_s.replace(_iso, _o['date']).replace(_long, _d.strftime('%B %-d, %Y')))
json.dump(_LM, open(_LMF, 'w'), indent=1, sort_keys=True)
open(SITE + '/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc><lastmod>{_dates[u]}</lastmod></url>' for u in (URL, SURL)) + '</urlset>')
open(SITE + '/robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {URL}sitemap.xml\n')
print('last updated', _dates)

# ---- remove what nothing uses any more: old bike-list and video files, old photos and logos, old share images
# (done last, so a build that stops early leaves the old page and the file it points at in place)
for f in os.listdir(SITE + '/img'):
    if f not in IMG: os.remove(f'{SITE}/img/{f}')
for f in os.listdir(SITE):
    if re.fullmatch(r'og-(vendors-)?[0-9a-f]{8}\.jpg', f) and f not in (OGN, OGV): os.remove(f'{SITE}/{f}')
    if f.startswith('data-') and f.endswith('.js') and f != DN: os.remove(f'{SITE}/{f}')
    if f.startswith('videos-') and f.endswith('.json') and f != VN: os.remove(f'{SITE}/{f}')
