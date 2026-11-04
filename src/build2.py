import os
import json,glob,os
SHOPS_PREVIEW=False  # True makes shops.html a preview: noindex and left out of sitemap.xml
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
fix={'Laurel Cyclery (Oakland)':'https://www.laurelcyclery.com/','Sports Basement (Berkeley)':'https://shop.sportsbasement.com/blogs/stores/berkeley','Alameda Bicycle (Alameda)':'https://www.alamedabicycle.com/','Dublin Cyclery (Dublin)':'https://www.dublincyclery.com/','Adaptive Cycles (Berkeley)':'https://adaptivecycles.com/','Cycle City (Alameda)':'https://cyclecityusa.com/'}
for k,u in fix.items():
    if k in S: S[k]['url']=u
for k in ['Castro Valley Cyclery','Castro Valley Cyclery (Castro Valley)']:
    if k in S: S[k]['url']=None  # site's security certificate has expired
out=[]
for b,r,img,mode in zip(B,R,IM,MODES):
    shops=[s.strip() for s in b['shops'].split(',') if s.strip() and 'Kog' not in s and s.strip()!='(Oakland)']
    def n(x):
        try: return float(x) if x is not None else None
        except: return None
    out.append(dict(brand=b['brand'],model=b['model'],type=b['type'],fold=b['fold'],cls=b['cls'],
      price=n(r.get('price')),note=r.get('price_note') if (r.get('price') or (r.get('price_note') and 'not researched' not in r.get('price_note','') and 'budget' not in r.get('price_note',''))) else None,motor=r.get('motor'),tq=n(r.get('torque_nm')),spd=n(r.get('top_speed_mph')),
      wh=n(r.get('battery_wh')),range=r.get('range_mi'),load=n(r.get('max_load_lb')),height=r.get('rider_height'),wt=n(r.get('weight_lb')),src=r.get('source'),img=img,fit=mode,shops=shops))
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
# one card per current model (verify/cards.json): maker-verified specs, prices, colors and per-color photos.
# A row the maker sells as several models becomes several cards; each card keeps its row's shops and rebate type.
CARDS=json.load(open('verify/cards.json')) if os.path.exists('verify/cards.json') else None
if CARDS:
    CHX={'Black':(29,31,30),'White':(244,244,242),'Gray':(138,143,140),'Silver':(196,200,198),'Blue':(47,99,196),'Green':(63,138,79),'Teal':(31,143,138),'Red':(200,53,46),'Orange':(226,116,42),'Yellow':(233,194,59),'Brown':(123,86,54),'Tan':(201,173,132),'Pink':(228,138,168),'Purple':(122,79,176)}
    def hexfam(h):
        try: r,g,b=int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
        except Exception: return None
        return min(CHX,key=lambda f:sum((a-c)**2 for a,c in zip((r,g,b),CHX[f])))
    def emitf(name):
        src=f'verify/cardphotos/{name}.webp'
        if SITE:
            shutil.copy(src,f'{SITE}/img/c-{name}.webp');return f'img/c-{name}.webp'
        return 'data:image/webp;base64,'+base64.b64encode(open(src,'rb').read()).decode()
    import shutil
    for i,c in CARDS.items():
        if isinstance(c,dict) and 'merge' in c:
            t=out[c['merge']];t['shops']=list(dict.fromkeys(t['shops']+out[int(i)]['shops']))
    new=[]
    for i,o in enumerate(out):
        L=CARDS.get(str(i))
        if isinstance(L,dict): continue
        for c in L:
            n={k:v for k,v in o.items() if k not in ('tier','warn')}
            for k in ('brand','model','cls','spd','tq','wh','range','wt','load','height','motor','price','src','st'): n[k]=c.get(k)
            n['fold']=c.get('fold') or o.get('fold')
            n['range']=rng(n.get('range'))
            if c.get('wtnb'): n['wtnb']=True
            n['note']=c.get('pnote')
            if c.get('cv') is not None:
                cv=[]
                for x in c['cv']:
                    f=fam(x['n']) or (hexfam(x['hex']) if x.get('hex') else None)
                    if not f: continue
                    cv.append(dict(n=x['n'],f=f,hex=x.get('hex'),img=emitf(x['img']) if x.get('img') else None))
                if cv or not o['cv']: n['cv']=cv
            if c.get('img'): n['img']=emitf(c['img'])
            elif n['cv'] is not o['cv'] and any(x['img'] for x in n['cv']): n['img']=next(x['img'] for x in n['cv'] if x['img'])
            new.append(n)
    out=new
import shutil
# shop logos (verify/shoplogos/<slug>.webp), matched by the shop's name
LOGO={'Alameda Bicycle':'alameda-bicycle','Blue Heron Bikes':'blue-heron-bikes','Cycle City':'cycle-city','Dublin Cyclery':'dublin-cyclery','Ebikes2U':'ebikes2u','Electric Bike Center':'electric-bike-center','Laurel Cyclery':'laurel-cyclery','Stay True Cycles':'stay-true-cycles','The Bicycle Garage':'the-bicycle-garage','The New Wheel':'the-new-wheel','Tip Top Bike Shop':'tip-top-bike-shop',"Robby's Bicycles":'robby-s-bicycles','Uptown BART Bike Station':'bikehub','Cyclepath':'cyclepath','Rhythm Bikes':'rhythm-bikes','Niles Bicycles':'niles-bicycles','Adaptive Cycles':'adaptive-cycles','Adaptive Cycles (Berkeley)':'adaptive-cycles'}
def logo_for(n):
    if n in LOGO: return LOGO[n]
    if n.startswith("Mike's Bikes"): return 'mike-s-bikes'
    if n.startswith('Trek Bicycle'): return 'trek'
    if n.startswith('Pedego'): return 'pedego'
    if n.startswith('Sports Basement'): return 'sports-basement'
for v in S.values():
    g=logo_for(v['name'])
    if g:
        if SITE: shutil.copy(f'verify/shoplogos/{g}.webp',f'{SITE}/img/logo-{g}.webp'); v['logo']=f'img/logo-{g}.webp'
        else: v['logo']='data:image/webp;base64,'+base64.b64encode(open(f'verify/shoplogos/{g}.webp','rb').read()).decode()
missing=sorted({s for o in out for s in o['shops'] if s not in S})
print('unmapped shops',missing,'priced',sum(1 for o in out if o['price']))
json.dump([{**{k:v for k,v in o.items() if k not in ('img','cv')},'colors':[c['n'] for c in o['cv']]} for o in out],open('merged.json','w'),indent=0)
import shutil
if SITE:
    shutil.copy('verify/hero.mp4',SITE+'/img/hero.mp4');shutil.copy('verify/hero.jpg',SITE+'/img/hero.jpg');HM,HJ='img/hero.mp4','img/hero.jpg'
else:
    HM='data:video/mp4;base64,'+base64.b64encode(open('verify/hero.mp4','rb').read()).decode();HJ='data:image/jpeg;base64,'+base64.b64encode(open('verify/hero.jpg','rb').read()).decode()
html=open('site_tpl.html').read().replace('__HERO_MP4__',HM).replace('__HERO_JPG__',HJ).replace('__BIKES__',json.dumps(out,separators=(',',':'))).replace('__SHOPS__',json.dumps(S,separators=(',',':')))
# the published page keeps the bike list in its own file, so the page itself stays small and link previews
# (Messages, Slack, X) can read it; the list loads right after, before the page script runs
if SITE:
    for f in os.listdir(SITE):
        if f.startswith('data-') and f.endswith('.js'): os.remove(os.path.join(SITE,f))
    DJ='window.AVA_B='+json.dumps(out,separators=(',',':'))+';window.AVA_S='+json.dumps(S,separators=(',',':'))+';'
    DN='data-'+hashlib.md5(DJ.encode()).hexdigest()[:8]+'.js'
    open(os.path.join(SITE,DN),'w').write(DJ)
    PAGE=open('site_tpl.html').read().replace('__HERO_MP4__',HM).replace('__HERO_JPG__',HJ)
    PAGE=PAGE.replace('<script>\nconst B=__BIKES__;\nconst S=__SHOPS__;',f'<script src="{DN}"></script>\n<script>\nconst B=window.AVA_B;\nconst S=window.AVA_S;',1)
    assert '__BIKES__' not in PAGE
    # plain-text copy of the list for search engines and browsers that don't run the page script
    import html as _hx
    _grp={}
    for _b in out: _grp.setdefault(_b['brand'],[]).append(_b)
    _li=[]
    for _br in sorted(_grp,key=str.lower):
        _items=[]
        for _b in sorted(_grp[_br],key=lambda x:x['model'].lower()):
            _r=900 if _b.get('type') in ('Cargo','Adaptive') else 400
            _bits=[_b.get('type') or '']
            if _b.get('cls'): _bits.append(f"Class {_b['cls']}")
            if _b.get('price'): _bits.append(f"${_b['price']:,} list, about ${max(_b['price']-_r,0):,} after the ${_r} rebate")
            _items.append(f"<li>{_hx.escape(_br+' '+_b['model'])} ({_hx.escape(', '.join(x for x in _bits if x))})</li>")
        _li.append(f"<h3>{_hx.escape(_br)}</h3><ul>{''.join(_items)}</ul>")
    NOS=f'<noscript><div class="wrap"><h2>All {len(out)} e-bikes on the Ava rebate list</h2>{"".join(_li)}</div></noscript>'
    PAGE=PAGE.replace('<main class="wrap grid" id="g"></main>','<main class="wrap grid" id="g"></main>'+NOS,1)
    assert NOS in PAGE
else: PAGE=html
open('Ava_Rebate_Bike_Finder.html','w').write(html)
# SEO + social cards: head tags, icons, manifest, sitemap
URL='https://ratsuns.github.io/ava-bike-finder/'
# the share image gets a content hash in its name, so every change is a new URL that apps and the CDN fetch fresh
OGN='og-'+hashlib.md5(open('verify/seo/og.jpg','rb').read()).hexdigest()[:8]+'.jpg'
TITLE='Ava E-Bike Rebate Finder: Every Eligible E-Bike, Price and Shop'
DESC=f"All {len(out)} e-bikes on Ava Community Energy's rebate list for Alameda and San Joaquin County. See your price after the $400 or $900 rebate and find a shop."
# structured data for Google: the site, who made it, and every participating shop
_seen={};
for _s in S.values():
    _k=(_s.get('name'),_s.get('address'))
    if _s.get('name') and _k not in _seen: _seen[_k]=_s
_stores=[]
for _s in sorted(_seen.values(),key=lambda x:(x.get('city') or '',x['name'])):
    _d={"@type":"BikeStore","name":_s['name']}
    if _s.get('address'): _d["address"]={"@type":"PostalAddress","streetAddress":_s['address'],"addressLocality":_s.get('city'),"addressRegion":"CA","addressCountry":"US"}
    for a,b in (('phone','telephone'),('url','url'),('email','email')):
        if _s.get(a): _d[b]=_s[a]
    _stores.append(_d)
FAQ=[('How much is the Ava e-bike rebate?', "$900 off cargo and adaptive e-bikes and $400 off standard e-bikes. If you're enrolled in CARE or FERA (PG&E) or EAP (Alameda Municipal Power), it's $1,500 off cargo and adaptive and $1,000 off standard, plus up to $250 for a helmet, lock and lights."), ('Who can get the Ava e-bike rebate?', "Anyone 18 or older who lives in Alameda County, or who is an Ava residential customer in San Joaquin County (Tracy, Stockton, Lathrop and nearby unincorporated areas). It's one rebate per person and up to two per household."), ('How do I get the Ava e-bike rebate?', "Apply on Ava's Bike Electric page. Ava picks people in a random drawing each month, and you're entered in three drawings in a row. If you're picked, Ava emails you a rebate code. Use it in person at a participating shop within 60 days."), ('Can I use the Ava e-bike rebate online?', "No. The rebate only works in person at a participating shop. It can't be used online, on used bikes or on bikes bought before you applied."), ('Does the Ava e-bike rebate cover sales tax?', "No. The rebate comes off the bike's price only. Sales tax and shipping are paid on top.")]
_me={"@type":"Person","@id":URL+"#chris","name":"Chris Beltran","address":{"@type":"PostalAddress","addressLocality":"Oakland","addressRegion":"CA"}}
LD={"@context":"https://schema.org","@graph":[
 {"@type":"WebSite","@id":URL+"#site","name":"Ava Bike Finder","url":URL,"description":DESC,"inLanguage":"en-US","publisher":{"@id":URL+"#chris"},"copyrightHolder":{"@id":URL+"#chris"},"copyrightYear":2026},
 {"@type":"WebPage","@id":URL,"url":URL,"name":TITLE,"description":DESC,"isPartOf":{"@id":URL+"#site"},"author":{"@id":URL+"#chris"},"dateModified":__import__('datetime').date.today().isoformat(),"about":{"@type":"Thing","name":"Ava Community Energy e-bike rebate"},"primaryImageOfPage":URL+OGN},
 _me,
 {"@type":"FAQPage","@id":URL+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]},
 {"@type":"Dataset","name":"E-bikes eligible for the Ava Community Energy rebate","description":f"All {len(out)} e-bikes on Ava's eligible list with maker price, price after the rebate, class, type, motor, battery, range, weight and the shops that sell each one.","url":URL,"dateModified":__import__('datetime').date.today().isoformat(),"creator":{"@id":URL+"#chris"},"isAccessibleForFree":True,"license":"https://ratsuns.github.io/ava-bike-finder/#copyright","distribution":[{"@type":"DataDownload","encodingFormat":"text/markdown","contentUrl":URL+"llms-full.txt"}]},
 {"@type":"ItemList","name":"Shops that accept the Ava e-bike rebate","numberOfItems":len(_stores),"itemListElement":[{"@type":"ListItem","position":i+1,"item":x} for i,x in enumerate(_stores)]}]}
import html as _h
e=_h.escape
SEO=(f'<title>{e(TITLE)}</title><meta name="description" content="{e(DESC)}"><link rel="canonical" href="{URL}">'
 '<meta name="robots" content="index,follow,max-image-preview:large">'
 '<link rel="icon" href="favicon.ico" sizes="48x48"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="manifest" href="site.webmanifest"><link rel="alternate" type="text/markdown" title="Full bike and shop list" href="llms-full.txt">'
 f'<meta property="og:type" content="website"><meta property="og:site_name" content="Ava Bike Finder"><meta property="og:url" content="{URL}"><meta property="og:title" content="{e("Find your e-bike with the Ava rebate")}"><meta property="og:description" content="{e(DESC)}">'
 f'<meta property="og:image" content="{URL}{OGN}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="Ava Bike Finder: Find your e-bike with the Ava rebate. $900 off cargo and adaptive, $400 off standard."><meta property="og:locale" content="en_US">'
 f'<meta property="og:video" content="{URL}img/hero.mp4"><meta property="og:video:secure_url" content="{URL}img/hero.mp4"><meta property="og:video:type" content="video/mp4"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">'
 f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e("Find your e-bike with the Ava rebate")}"><meta name="twitter:description" content="{e(DESC)}"><meta name="twitter:image" content="{URL}{OGN}"><meta name="twitter:image:alt" content="Ava Bike Finder: Find your e-bike with the Ava rebate.">'
 '<script type="application/ld+json">'+json.dumps(LD,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>')
if SITE:
    shutil.copy('verify/seo/og.jpg',SITE+'/'+OGN)
    for f in ['favicon.svg','favicon.ico','apple-touch-icon.png','fav-192.png','fav-512.png']: shutil.copy('verify/seo/'+f,SITE+'/'+f)
    json.dump({"name":"Ava Bike Finder","short_name":"Ava Bikes","start_url":"./","scope":"./","display":"standalone","background_color":"#000000","theme_color":"#0f1211",
     "icons":[{"src":"fav-192.png","sizes":"192x192","type":"image/png"},{"src":"fav-512.png","sizes":"512x512","type":"image/png"},{"src":"fav-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(SITE+'/site.webmanifest','w'))
    import datetime
    # plain markdown files for AI assistants (llmstxt.org)
    _today=datetime.date.today().strftime('%B %-d, %Y')
    def _rb(b): return 900 if b.get('type') in ('Cargo','Adaptive') else 400
    _hdr=f"""# Ava Bike Finder

> Every e-bike on Ava Community Energy's e-bike rebate list ({len(out)} bikes), with each bike's price, the price after the rebate, specs and the shops that sell it. Made by Chris Beltran in Oakland, CA. Not affiliated with Ava Community Energy. Updated {_today}.

## The rebate (source: https://avaenergy.org/bike-electric/, checked October 29, 2026)

"""+"\n".join(f"- **{q}** {a}" for q,a in FAQ)+"""

## Files

- [Full bike and shop list](llms-full.txt): every bike with price, price after rebate, class, specs and shops, plus every shop's address, phone, hours and website.
- [Website](https://ratsuns.github.io/ava-bike-finder/): search and filter the list.
"""
    open(SITE+'/llms.txt','w').write(_hdr)
    _rows=["| Bike | Type | Class | Price | After rebate | Motor | Battery | Range | Weight | Status | Shops |","|---|---|---|---|---|---|---|---|---|---|---|"]
    _stx={'disc':'Discontinued by maker','na':'No Ava shop sells it now'}
    for _b in sorted(out,key=lambda x:(x['brand'].lower(),x['model'].lower())):
        _p=_b.get('price')
        _c=lambda v:str(v).replace('|','/') if v not in (None,'') else ''
        _rows.append('| '+' | '.join([_c(_b['brand']+' '+_b['model']),_c(_b.get('type')),_c(_b.get('cls')),f"${_p:,}" if _p else 'not listed',f"${max(_p-_rb(_b),0):,}" if _p else '',_c(_b.get('motor')),f"{_b['wh']} Wh" if _b.get('wh') else '',f"{_b['range']} mi" if _b.get('range') else '',(f"{_b['wt']} lb"+(' (no battery)' if _b.get('wtnb') else '')) if _b.get('wt') else '',_stx.get(_b.get('st'),'Available'),_c(', '.join(S[k]['name'] for k in (_b.get('shops') or []) if k in S))])+' |')
    _shops=[]
    for _s in sorted(_seen.values(),key=lambda x:(x.get('city') or '',x['name'])):
        _shops.append(f"### {_s['name']} ({_s.get('city','')})\n"+"\n".join(f"- {k}: {v}" for k,v in (('Address',(_s.get('address') or '')+(', '+_s['city'] if _s.get('city') else '')+', CA'),('Phone',_s.get('phone')),('Hours',_s.get('hours')),('Email',_s.get('email')),('Website',_s.get('url'))) if v))
    open(SITE+'/llms-full.txt','w').write(_hdr.replace('## Files','## Notes\n\n- "After rebate" uses the regular $400 (standard) or $900 (cargo and adaptive) rebate. Sales tax is extra.\n- Prices are the maker\'s US list price, or the selling shop\'s price when the maker has none.\n\n## Files',1)+f"\n## All {len(out)} e-bikes\n\n"+"\n".join(_rows)+"\n\n## Participating shops\n\n"+"\n\n".join(_shops)+"\n")
    open(SITE+'/sitemap.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>'+('' if SHOPS_PREVIEW else f'<url><loc>{URL}browse-vendors/</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>')+'</urlset>')
    PAGE=PAGE.replace('<title>Ava Rebate Bike Finder</title>','',1)
if SITE: open(SITE+'/index.html','w').write('<!doctype html><html lang="en" data-theme="dark" data-overlayscrollbars-initialize><head><meta charset="utf-8"><link rel="stylesheet" href="vendor/overlayscrollbars-2.16.0.min.css"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#0f1211">'+SEO+'<script>if(location.hash==="#dir")location.replace("browse-vendors/");try{if(!matchMedia("(hover: hover) and (pointer: fine)").matches||matchMedia("(any-pointer: coarse)").matches)document.documentElement.removeAttribute("data-overlayscrollbars-initialize");var t=localStorage.getItem("theme");if(t==="light"){document.documentElement.dataset.theme="light";document.querySelector("meta[name=color-scheme]").content="light";document.querySelector("meta[name=theme-color]").content="#f6f7f5"}}catch(e){}</script><script type="speculationrules">{"prefetch":[{"where":{"href_matches":"*browse-vendors/*"},"eagerness":"moderate"}]}</script></head><body data-overlayscrollbars-initialize style="margin:0">'+PAGE+'</body></html>')
# shops.html: every shop location as the home page's shop card, next to a map with a pin per shop
def _css_keep(css,classes,types):
    # copies the home page rules whose selectors only use the given classes and element types (rule order kept, @media/@supports filtered inside)
    def ok(sel):
        if any(v not in ('root','themebtn') for v in re.findall(r'view-transition-[\w-]+\(([^)]*)\)',sel)): return False
        s=re.sub(r'\[[^\]]*\]','',sel)
        while re.search(r'\([^()]*\)',s): s=re.sub(r'\([^()]*\)','',s)
        s=re.sub(r'::?[\w-]+','',s)
        cl=re.findall(r'\.([\w-]+)',s); ids=re.findall(r'#([\w-]+)',s); ty=re.findall(r'[a-zA-Z][\w-]*',re.sub(r'[.#][\w-]+','',s))
        return not ids and all(c in classes or c.startswith('os-') for c in cl) and all(t in types for t in ty)
    def walk(t):
        o=[];i=0
        while i<len(t):
            j=t.find('{',i)
            if j<0: break
            pre=t[i:j].strip();d=1;k=j+1
            while d:
                d+={'{':1,'}':-1}.get(t[k],0);k+=1
            body=t[j+1:k-1];i=k
            if pre.startswith('@media') or pre.startswith('@supports') or pre.startswith('@starting-style'):
                inner=walk(body)
                if inner: o.append(pre+'{'+inner+'}')
            elif pre.startswith('@'): continue
            else:
                sels=[x.strip() for x in pre.split(',') if ok(x.strip())]
                if sels: o.append(','.join(sels)+'{'+body.strip()+'}')
        return '\n'.join(o)
    return walk(re.sub(r'/\*.*?\*/','',css,flags=re.S))
if SITE:
    _tpl=open('site_tpl.html').read()
    _css=_tpl[_tpl.index('<style>')+7:_tpl.index('</style>')]
    BASE_CSS=_css_keep(_css,{'wrap','shop','slogo','ini','shead','maplink','hrs','tel','mail','web','city','m','brand','themebtn','tm-core','tm-cut','tm-rays','topnav','navr','navlinks','menubtn','mi-open','mi-close','navmenu','nmh','nmb','nmx','nml','nmc','locked','drawer','dhead','dbody','dclose','g2','g3','gamt','gc','gdl','gk','gl','gnote','gsrc','gsteps','gsub','lg','rb','has-more','has-above'},{'html','body','a','svg','img','b','span','ul','li','button','nav','dialog','div','p','h2','h3','dl','dt','dd','ol'})
    # the card helpers and the card markup come straight from the home page script, so the cards are identical
    def _js(name,until=None):
        m=re.search(r'^const '+name+r'=.*$',_tpl,re.M); assert m,name
        if not until: return m.group(0)
        e=_tpl.index(until,m.end()); return _tpl[m.start():_tpl.index('\n',e)]
    HELPERS='\n'.join([_js('esc'),_js('mapUrl'),_js('telUrl'),_js('PIN'),_js('GLOBE'),_js('CLOCK'),_js('MAIL'),_js('mailUrl',' return `mailto:'),_js('slogo'),_js('shopLines'),_js('EXT')])
    # the shop card (the same markup the home page's old "Where to buy" list used)
    CARD='`<div class="shop" data-shop="${esc(s.k)}">${slogo(s)}<span class="city">${esc(s.city||\'\')}</span><b>${esc(s.name)}</b>${shopLines(s)||\'<span class="m">Address not listed</span>\'}${s.url?`<a class="web" href="${esc(s.url)}" target="_blank" rel="noopener">${GLOBE}<span>Shop website</span>${EXT}</a>`:\'\'}</div>`'
    # one card and pin per shop location (some shops are listed under two or three names in the data; those share one pin)
    _loc={}
    for k,s in S.items():
        if s.get('lat') is None: continue
        _loc.setdefault((s['name'],s.get('address')),dict(k=k,**{f:s[f] for f in ('name','address','city','phone','url','email','contact','hours','lat','lng','logo') if s.get(f) is not None}))
    SHL=list(_loc.values())
    SURL=URL+'browse-vendors/'
    STITLE='Participating Shops for the Ava E-Bike Rebate | Ava Bike Finder'
    SDESC=f'All {len(SHL)} shops that take the Ava Community Energy e-bike rebate in Alameda and San Joaquin County, on a map with each address, phone number and opening hours.'
    # the vendor page's own share card (the page itself on the share card's grid; made by verify/seo/og-vendors-shot.js); hashed name like og.jpg
    OGV='og-vendors-'+hashlib.md5(open('verify/seo/og-vendors.jpg','rb').read()).hexdigest()[:8]+'.jpg'
    shutil.copy('verify/seo/og-vendors.jpg',SITE+'/'+OGV)
    _OGV_ALT=f'Ava Bike Finder vendor directory: the list of shops that take the Ava e-bike rebate next to a map with a pin for each shop.'
    _today=datetime.date.today().isoformat()
    # structured data: this page, where it sits in the site, and every shop on it (with its map location)
    _vs=[]
    for _s in sorted(SHL,key=lambda x:(x.get('city') or '',x['name'])):
        _d={"@type":"BikeStore","name":_s['name'],"address":{"@type":"PostalAddress","streetAddress":_s.get('address'),"addressLocality":_s.get('city'),"addressRegion":"CA","addressCountry":"US"},"geo":{"@type":"GeoCoordinates","latitude":_s['lat'],"longitude":_s['lng']}}
        for a,b in (('phone','telephone'),('url','url'),('email','email')):
            if _s.get(a): _d[b]=_s[a]
        if _s.get('logo'): _d["logo"]=URL+_s['logo']
        _vs.append(_d)
    SLD={"@context":"https://schema.org","@graph":[
     {"@type":"CollectionPage","@id":SURL,"url":SURL,"name":STITLE,"description":SDESC,"inLanguage":"en-US","isPartOf":{"@id":URL+"#site"},"breadcrumb":{"@id":SURL+"#crumbs"},"primaryImageOfPage":URL+OGV,"dateModified":_today,"mainEntity":{"@id":SURL+"#shops"}},
     {"@type":"BreadcrumbList","@id":SURL+"#crumbs","itemListElement":[{"@type":"ListItem","position":1,"name":"Ava Bike Finder","item":URL},{"@type":"ListItem","position":2,"name":"Browse vendors","item":SURL}]},
     {"@type":"WebSite","@id":URL+"#site","name":"Ava Bike Finder","url":URL},
     {"@type":"ItemList","@id":SURL+"#shops","name":"Shops that accept the Ava e-bike rebate","numberOfItems":len(_vs),"itemListElement":[{"@type":"ListItem","position":i+1,"item":x} for i,x in enumerate(_vs)]}]}
    # share-card tags, used by the page and by the old shops.html address
    SOG=(f'<meta property="og:type" content="website"><meta property="og:site_name" content="Ava Bike Finder"><meta property="og:url" content="{SURL}"><meta property="og:title" content="{e("Every shop that takes the Ava e-bike rebate")}"><meta property="og:description" content="{e(SDESC)}">'
     f'<meta property="og:image" content="{URL}{OGV}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="{e(_OGV_ALT)}"><meta property="og:locale" content="en_US">'
     f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e("Every shop that takes the Ava e-bike rebate")}"><meta name="twitter:description" content="{e(SDESC)}"><meta name="twitter:image" content="{URL}{OGV}"><meta name="twitter:image:alt" content="{e(_OGV_ALT)}">')
    STY_URL={'light':'https://tiles.openfreemap.org/styles/bright','dark':'https://tiles.openfreemap.org/styles/bright'}  # OSM Bright in both themes
    SHEAD=('<!doctype html><html lang="en" data-theme="dark" data-overlayscrollbars-initialize><head><meta charset="utf-8"><link rel="stylesheet" href="vendor/overlayscrollbars-2.16.0.min.css"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#0f1211">'
     f'<title>{e(STITLE)}</title><meta name="description" content="{e(SDESC)}"><link rel="canonical" href="{SURL}">'
     +('<meta name="robots" content="noindex">' if SHOPS_PREVIEW else '<meta name="robots" content="index,follow,max-image-preview:large">')+
     '<link rel="icon" href="favicon.ico" sizes="48x48"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="manifest" href="site.webmanifest"><link rel="alternate" type="text/markdown" title="Full bike and shop list" href="llms-full.txt">'
     +SOG+
     # the map style for the current theme starts downloading right away, alongside MapLibre (deferred, so it never holds up the page)
     '<script type="speculationrules">{"prefetch":[{"where":{"selector_matches":"a.brand, a[href=\\"./\\"]"},"eagerness":"moderate"}]}</script>'
     '<link rel="preconnect" href="https://tiles.openfreemap.org" crossorigin>'
     # the map's tile index is also fetched up front, in parallel, instead of only after the style arrives
     '<link rel="preload" as="fetch" crossorigin href="https://tiles.openfreemap.org/planet">'
     # the style's icons and label fonts also start downloading right away, instead of after the map program has read the style
     # (sharp icons on high-density screens, like the map itself)
     '<script>(()=>{const r=Math.min(devicePixelRatio||1,2)>1?"@2x":"",b="https://tiles.openfreemap.org/";["sprites/ofm_f384/ofm"+r+".json","sprites/ofm_f384/ofm"+r+".png","fonts/Noto%20Sans%20Regular/0-255.pbf","fonts/Noto%20Sans%20Italic/0-255.pbf"].forEach(u=>{const l=document.createElement("link");l.rel="preload";l.as="fetch";l.crossOrigin="anonymous";l.href=b+u;document.head.append(l)})})()</script>'
     f'<script>try{{if(!matchMedia("(hover: hover) and (pointer: fine)").matches||matchMedia("(any-pointer: coarse)").matches)document.documentElement.removeAttribute("data-overlayscrollbars-initialize");var t=localStorage.getItem("theme");if(t==="light"){{document.documentElement.dataset.theme="light";document.querySelector("meta[name=color-scheme]").content="light";document.querySelector("meta[name=theme-color]").content="#f6f7f5"}}}}catch(e){{}}(function(){{var l=document.createElement("link");l.rel="preload";l.as="fetch";l.crossOrigin="anonymous";l.href=document.documentElement.dataset.theme==="light"?"{STY_URL["light"]}":"{STY_URL["dark"]}";document.head.appendChild(l)}})()</script>'
     # the map's stylesheet downloads in parallel but never holds up the cards: it's applied when it arrives, and the map starts once it's in
     '<link rel="preload" as="style" href="vendor/maplibre-gl-5.24.0.min.css" onload="this.onload=null;this.rel=\'stylesheet\';window.MLCSS=1;document.dispatchEvent(new Event(\'mlcss\'))" onerror="window.MLCSS=1;document.dispatchEvent(new Event(\'mlcss\'))"><script defer src="vendor/maplibre-gl-5.24.0.min.js"></script>')
    # the same top nav and phone menu as the home page; its window buttons become links back to the home page
    _nav=_tpl[_tpl.index('<nav class="topnav"'):_tpl.index('</div><header class="hero"')]
    _nav=_nav.replace('href="#top"','href="./"',1).replace('href="browse-vendors/"','href="browse-vendors/" aria-current="page"')
    assert _nav.count('data-open="guide"')==2 and _nav.count('data-open="rebate"')==2 and _nav.count('aria-current')==2
    # the E-bike guide and Rebate info windows come along, so those buttons open them right here
    _dl=''.join(_tpl[_tpl.index(f'<dialog id="{d}"'):_tpl.index('</dialog>',_tpl.index(f'<dialog id="{d}"'))+9]+'\n' for d in ('guide','rebate'))
    SP=open('shops_tpl.html').read()
    for a,b in (('__HEAD__',SHEAD),('__BASE_CSS__',BASE_CSS),('__HELPERS__',HELPERS),('__CARD__',CARD),('__NAV__',_nav),('__DIALOGS__',_dl),('__COUNT__',str(len(SHL))),('__WORLD__',open('worlddots.json').read().strip()),('__SHOPS__',json.dumps(SHL,separators=(',',':'),ensure_ascii=False).replace('</','<\\/'))):
        assert SP.count(a)==1,a; SP=SP.replace(a,b)
    # the page lives at browse-vendors/ (clean address); every relative link in it resolves from the site root
    SP=SP.replace('<meta charset="utf-8">','<meta charset="utf-8"><base href="../">',1)
    # the structured data goes at the end of the page, so it never delays the first paint (search engines read it anywhere)
    assert SP.rstrip().endswith('</body></html>')
    SP=SP.rstrip()[:-len('</body></html>')]+'<script type="application/ld+json">'+json.dumps(SLD,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script></body></html>'
    os.makedirs(SITE+'/browse-vendors',exist_ok=True);open(SITE+'/browse-vendors/index.html','w').write(SP)
    # the old shops.html address forwards to browse-vendors/ (keeping any #part of the link)
    open(SITE+'/shops.html','w').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(STITLE)}</title><meta name="description" content="{e(SDESC)}"><link rel="canonical" href="{SURL}"><meta name="robots" content="noindex">{SOG}<meta http-equiv="refresh" content="0;url=browse-vendors/"><script>location.replace("browse-vendors/"+location.search+location.hash)</script></head><body><a href="browse-vendors/">Participating shops</a></body></html>')
    print('shops.html',len(SHL),'locations',len(SP),'bytes')
open('Ava_Rebate_Bike_Finder_local.html','w').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+html+'</body></html>')
print(os.path.getsize('Ava_Rebate_Bike_Finder.html'))
