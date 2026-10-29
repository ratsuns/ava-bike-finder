import os
import json,glob,os
B=json.load(open('bikes.json')); R=json.load(open('res_all.json')); IM=json.load(open('imgs_v3.json')); MODES=json.load(open('img_modes_v3.json')); S=json.load(open('shops.json'))
for f in sorted(glob.glob('fill*.json')):
    for r in json.load(open(f)):
        i=r['index']
        if r.get('price') and not R[i].get('price'):
            for k,v in r.items():
                if k!='index' and v is not None: R[i][k]=v
from cargo_specs import CS
for b,r in zip(B,R):
    for k,v in CS.get((b['brand'],b['model']),{}).items():
        if k in ('price','price_note','source') or r.get(k) is None: r[k]=v
fix={'Laurel Cyclery (Oakland)':'https://www.laurelcyclery.com/','NILES BICYCLES (Fremont)':'https://niles-bicycles.cloveronline.com/','Sports Basement (Berkeley)':'https://shop.sportsbasement.com/blogs/stores/berkeley','Alameda Bicycle (Alameda)':'https://www.alamedabicycle.com/','Dublin Cyclery (Dublin)':'https://www.dublincyclery.com/','Robby\'s Bicycles (Stockton)':'https://www.robbysbicycles.com/','Adaptive Cycles (Berkeley)':'https://adaptivecycles.com/','Stay True Cycles (Berkeley)':'https://www.staytrue.bike/','Cycle City (Alameda)':'https://cyclecityusa.com/','King Kog (Oakland)':'https://kingkog.bigcartel.com/','(Oakland)':'https://kingkog.bigcartel.com/'}
for k,u in fix.items():
    if k in S: S[k]['url']=u
for k in ['Castro Valley Cyclery','Castro Valley Cyclery (Castro Valley)']:
    if k in S: S[k]['url']=None  # site's security certificate has expired
out=[]
for b,r,img,mode in zip(B,R,IM,MODES):
    shops=[s.strip() for s in b['shops'].replace('King Kog (Oakland)','(Oakland)').split(',') if s.strip()]
    shops=[s if s in S else ('(Oakland)' if 'Kog' in s else s) for s in shops]
    def n(x):
        try: return float(x) if x is not None else None
        except: return None
    out.append(dict(brand=b['brand'],model=b['model'],type=b['type'],fold=b['fold'],cls=b['cls'],tier=b['price'],
      price=n(r.get('price')),note=r.get('price_note') if (r.get('price') or (r.get('price_note') and 'not researched' not in r.get('price_note','') and 'budget' not in r.get('price_note',''))) else None,motor=r.get('motor'),tq=n(r.get('torque_nm')),spd=n(r.get('top_speed_mph')),
      wh=n(r.get('battery_wh')),range=r.get('range_mi'),load=n(r.get('max_load_lb')),height=r.get('rider_height'),wt=n(r.get('weight_lb')),src=r.get('source'),img=img,fit=mode,shops=shops))
    p=out[-1]['price']
    if p:
        lo,hi={'$':(0,1500),'$$':(1501,3000),'$$$':(3001,1e9)}.get(out[-1]['tier'],(0,1e9))
        out[-1]['warn']= p<lo*0.85 or p>hi*1.15
VS={int(k):v for k,v in json.load(open('verify/specs_verified.json')).items()} if os.path.exists('verify/specs_verified.json') else {}
SP={}
for f in sorted(glob.glob('specs/out*.json')):
    for r in json.load(open(f)): SP[r['index']]=r
import re
GP={}
for f in sorted(glob.glob('specs/gapout*.json')):
    for r in json.load(open(f)): GP[r['index']]=r
def rng(v):
    if v in (None,''): return None
    v=str(v).replace('miles','').replace('mi','').strip()
    v=re.sub(r'\(.*?\)','',v); v=re.split(r'[;,/]',v)[0]
    v=re.sub(r'(?i)(up to|approx\.?|about|~|\+)','',v); v=re.sub(r'\s*-\s*','–',v).strip(' .')
    return v or None
for i,o in enumerate(out):
    r=SP.get(i,{})
    for k in ('spd','tq','load','wh','wt'):
        v=r.get(k)
        try: v=float(v) if v not in (None,'') else None
        except: v=None
        if v is not None: o[k]=int(v) if v==int(v) else v
    if r.get('motor'): o['motor']=r['motor']
    if r.get('range'): o['range']=r['range']
    o['range']=rng(o.get('range'))
    if o.get('spd') is not None and o['spd']<17: o['spd']=None
    g=GP.get(i,{})
    for k in ('spd','tq','load'):
        if o.get(k) is None and g.get(k) not in (None,''):
            try: v=float(g[k]); o[k]=int(v) if v==int(v) else v
            except: pass
    if not o.get('range') and g.get('range'): o['range']=rng(g['range'])
    if o.get('spd') is not None and o['spd']<17: o['spd']=None
    o['colors']=r.get('colors') or []
    o['cs']=r.get('colors_simple') or []
    # manufacturer-verified specs (verify/specs_verified.json, one entry per bike with its source page) win over everything above.
    # A field the maker doesn't publish is set to None there, so the card leaves it out instead of showing an unverified number.
    v=VS.get(i)
    if v:
        for k in ('cls','spd','tq','load','wh','wt'):
            if k in v: o[k]=v[k]
        for k in ('range','height','fold','motor'):
            if k in v: o[k]=v[k]
        if 'range' in v: o['range']=rng(o.get('range'))
# per-color photos (verified colors + verified photos), written as separate image files for the static site
from famap import fam
import base64,io,hashlib
from PIL import Image
CP=json.load(open('colorphotos.json'));CP.update(json.load(open('color_overrides.json')))
DISP=json.load(open('verify/display_from_color.json'))
VER={int(k):v for k,v in json.load(open('verify/verified.json')).items()}
KEEP=json.load(open('verify/keep.json'))
NEW=json.load(open('verify/newphotos.json')) if os.path.exists('verify/newphotos.json') else {}
SITE=os.environ.get('SITE_DIR')
if SITE: os.makedirs(SITE+'/img',exist_ok=True)
def emit(u,name,size=(480,360),q=62):
    im=Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGB')
    if im.size!=size: im=im.resize(size,Image.LANCZOS)
    b=io.BytesIO();im.save(b,'WEBP',quality=q,method=6);data=b.getvalue()
    if SITE:
        open(f'{SITE}/img/{name}.webp','wb').write(data);return f'img/{name}.webp'
    return 'data:image/webp;base64,'+base64.b64encode(data).decode()
for i,o in enumerate(out):
    v=VER.get(i,{})
    # main photo
    # photos re-checked in the October audit (wrong model, lifestyle shots, crops) take priority
    fx=f'verify/mainfix/{i}.png'
    if os.path.exists(fx): o['img']=emit('data:image/png;base64,'+base64.b64encode(open(fx,'rb').read()).decode(),f'{i}')
    elif f'm{i}' in NEW: o['img']=emit(NEW[f'm{i}'],f'{i}')
    else: o['img']=emit(o['img'],f'{i}')
    cv=[]
    for j,c in enumerate(v.get('colors') or []):
        f=c.get('family') or fam(c['name'])
        if not f: continue
        k=f'{i}|{j}';u=None
        cf=f'verify/colorfix/{i}-{j}.png'
        if os.path.exists(cf): u='data:image/png;base64,'+base64.b64encode(open(cf,'rb').read()).decode()
        elif f'c{k}' in NEW: u=NEW[f'c{k}']
        elif k in KEEP and KEEP[k] in CP: u=CP[KEEP[k]]['img']
        cv.append(dict(n=c['name'],f=f,hex=c.get('hex'),img=emit(u,f'{i}-{j}') if u else None))
    o['cv']=cv
    # display photo: where the main photo is a lifestyle/padded shot, show a clean photo of one of its colors instead (no color is selected)
    j=DISP.get(str(i))
    if j is not None and j<len(cv) and cv[j]['img']: o['img']=cv[j]['img']
    o.pop('colors',None);o.pop('cs',None)
missing=sorted({s for o in out for s in o['shops'] if s not in S})
print('unmapped shops',missing,'priced',sum(1 for o in out if o['price']))
json.dump([{**{k:v for k,v in o.items() if k not in ('img','cv')},'colors':[c['n'] for c in o['cv']]} for o in out],open('merged.json','w'),indent=0)
import shutil
if SITE:
    shutil.copy('verify/hero.mp4',SITE+'/img/hero.mp4');shutil.copy('verify/hero.jpg',SITE+'/img/hero.jpg');HM,HJ='img/hero.mp4','img/hero.jpg'
else:
    HM='data:video/mp4;base64,'+base64.b64encode(open('verify/hero.mp4','rb').read()).decode();HJ='data:image/jpeg;base64,'+base64.b64encode(open('verify/hero.jpg','rb').read()).decode()
html=open('site_tpl.html').read().replace('__HERO_MP4__',HM).replace('__HERO_JPG__',HJ).replace('__BIKES__',json.dumps(out,separators=(',',':'))).replace('__SHOPS__',json.dumps(S,separators=(',',':')))
open('Ava_Rebate_Bike_Finder.html','w').write(html)
# SEO + social cards: head tags, icons, manifest, sitemap
URL='https://ratsuns.github.io/ava-bike-finder/'
# the share image gets a content hash in its name, so every change is a new URL that apps and the CDN fetch fresh
OGN='og-'+hashlib.md5(open('verify/seo/og.jpg','rb').read()).hexdigest()[:8]+'.jpg'
TITLE='Ava E-Bike Rebate Finder: Every Eligible E-Bike, Price and Shop'
DESC=f"Browse all {len(out)} e-bikes on Ava Community Energy's rebate list. See your price after the $400 or $900 rebate, compare specs and find shops near you."
import html as _h
e=_h.escape
SEO=(f'<title>{e(TITLE)}</title><meta name="description" content="{e(DESC)}"><link rel="canonical" href="{URL}">'
 '<meta name="robots" content="index,follow,max-image-preview:large">'
 '<link rel="icon" href="favicon.ico" sizes="48x48"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="manifest" href="site.webmanifest">'
 f'<meta property="og:type" content="website"><meta property="og:site_name" content="Ava Bike Finder"><meta property="og:url" content="{URL}"><meta property="og:title" content="{e("Find your e-bike with the Ava rebate")}"><meta property="og:description" content="{e(DESC)}">'
 f'<meta property="og:image" content="{URL}{OGN}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="Ava Bike Finder: Find your e-bike with the Ava rebate. $900 off cargo and adaptive, $400 off standard."><meta property="og:locale" content="en_US">'
 f'<meta property="og:video" content="{URL}img/hero.mp4"><meta property="og:video:secure_url" content="{URL}img/hero.mp4"><meta property="og:video:type" content="video/mp4"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">'
 f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e("Find your e-bike with the Ava rebate")}"><meta name="twitter:description" content="{e(DESC)}"><meta name="twitter:image" content="{URL}{OGN}"><meta name="twitter:image:alt" content="Ava Bike Finder: Find your e-bike with the Ava rebate.">'
 '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"WebSite","name":"Ava Bike Finder","url":URL,"description":DESC,"inLanguage":"en-US"})+'</script>')
if SITE:
    shutil.copy('verify/seo/og.jpg',SITE+'/'+OGN)
    for f in ['favicon.svg','favicon.ico','apple-touch-icon.png','fav-192.png','fav-512.png']: shutil.copy('verify/seo/'+f,SITE+'/'+f)
    json.dump({"name":"Ava Bike Finder","short_name":"Ava Bikes","start_url":"./","scope":"./","display":"standalone","background_color":"#000000","theme_color":"#0f1211",
     "icons":[{"src":"fav-192.png","sizes":"192x192","type":"image/png"},{"src":"fav-512.png","sizes":"512x512","type":"image/png"},{"src":"fav-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(SITE+'/site.webmanifest','w'))
    import datetime
    open(SITE+'/sitemap.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url></urlset>')
    html=html.replace('<title>Ava Rebate Bike Finder</title>','',1)
if SITE: open(SITE+'/index.html','w').write('<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#0f1211">'+SEO+'<script>try{var t=localStorage.getItem("theme");if(t==="light"){document.documentElement.dataset.theme="light";document.querySelector("meta[name=color-scheme]").content="light";document.querySelector("meta[name=theme-color]").content="#f6f7f5"}}catch(e){}</script></head><body style="margin:0">'+html+'</body></html>')
open('Ava_Rebate_Bike_Finder_local.html','w').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+html+'</body></html>')
print(os.path.getsize('Ava_Rebate_Bike_Finder.html'))
