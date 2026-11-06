"""Pick the 3 best YouTube reviews for each bike model from the collected candidate videos.

Input:  verify/yt_candidates.json  {videoId: {t: title, c: channel, d: published, vw: views, du: ISO duration,
                                               em: embeddable 0/1, pv: privacy, lv: live status, la: language}}
Output: verify/videos.json          {"Brand|Model": [{id, t, c, d, vw, du}, ...up to 3]}

Rules (what the user asked for): most-viewed reviews from the last 2 years first, older ones fill open spots; the title must name the brand and the model,
the 3 most viewed win. Only videos YouTube allows on other sites (embeddable), public, not live, and at least
a minute long (no Shorts). A video goes to the most specific model it names (a "FX+ 2S" video is not a "FX+ 2" video).
When no video names a model's full name, the model's family name is tried (a "Level 4" video for "Level 4 REC").
"""
import json, re, glob, datetime, collections, sys, html, os

def norm(s):
    s = s.lower().replace('&', ' and ').replace('+', ' plus ').replace("'", '').replace('’', '')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'(?<=[a-z])(?=[0-9])|(?<=[0-9])(?=[a-z])', ' ', s)   # xp4 -> xp 4, 9d -> 9 d
    return ' '.join(s.split())

# words that describe a version or the frame, not which bike it is
DESCRIPTORS = set(norm('step through thru lowstep low step mens men womens women ebike bike electric bicycle tricycle '
                       'commuter all variants and new gen performance smart system sport hybrid touring').split())
BRAND_NAMES = {  # how titles name each brand (normalized phrases); default is the brand itself
    'Riese and Muller': ['riese muller', 'riese and muller', 'r and m'], 'LarryvsHarry': ['bullitt', 'larry vs harry', 'larry and harry'],
    'Ice Trikes': ['ice'], 'MOD': ['mod'], 'Sixthreezero': ['sixthreezero', 'six three zero'], 'Revi Bikes': ['revi'],
    'Top End': ['top end'], 'Golden Cycles': ['golden cycles'], 'Radio Flyer': ['radio flyer'], 'Urban Arrow': ['urban arrow'],
    'Mobility Access': ['mobility access'], 'Ebike2U': ['ebike 2 u', 'ebike2u'], 'X-Lab': ['x lab', 'xlab'],
}

def has(title, phrase):
    if re.search(r'(?:^| )' + re.escape(phrase) + r'(?: |$)', title): return True
    # names written together or apart ("FamilyNext Pro" / "Family Next Pro", "Scoria2" / "Scoria 2"): compare without spaces,
    # only for longer names so short words can't match inside other words
    sq = phrase.replace(' ', '')
    if len(sq) < 8: return False
    w = title.split()
    for i in range(len(w)):                     # whole words only: "fx plus 2 suspension" is not "fx plus 2 s"
        s = ''
        for j in range(i, len(w)):
            s += w[j]
            if s == sq: return True
            if len(s) >= len(sq): break
    return False

def clean_model(model):
    m = re.sub(r'\([^)]*\)', ' ', model)                      # drop "(and ST)", "(Gen 3)", "(290667)"...
    m = re.sub(r'\b20\d\d\b', ' ', m)                         # model years
    m = re.sub(r'\b\d+\s*mph\b', ' ', m, flags=re.I)          # "20 mph" speed versions
    return m

def core(model, brand_phrases):
    toks = [t for t in norm(clean_model(model)).split() if t not in DESCRIPTORS]
    for bp in brand_phrases:                                  # "Lectric ONE" -> "one"
        b = bp.split()
        if toks[:len(b)] == b: toks = toks[len(b):]
    return toks

FILLER = set('long range electric bike ebike e cargo folding city tricycle trike bmx the w edition rev1'.split())
GENERIC = set('one go pro plus cargo family max mini lite core sport city step trike bike e st x'.split())
TRIM = re.compile(r'^(?:[A-Za-z]{1,3}\d+[A-Za-z]{0,2}|[A-Za-z]+|\d+W)$')   # S10, P5i, EP600, D9, Q9, REC, ADV, 750W

def families(model, brand_phrases):
    """Shorter names to fall back on when no video names the full model: drop trailing trim words
    (REC, ADV, P10, S5i, EP600, 750W...) but never a plain model number (FX+ 2, Level 4, Como 4.0)."""
    words = [w for w in clean_model(model).replace('/', ' ').split()]
    out = []
    while len(words) > 1 and TRIM.match(words[-1]) and not re.fullmatch(r'\d+(\.\d+)?', words[-1]):
        words = words[:-1]
        k = core(' '.join(words), brand_phrases)
        if k and (len(k) >= 2 or (len(k[0]) >= 3 and k[0] not in GENERIC)): out.append(k)
    return out

def seconds(iso):
    m = re.fullmatch(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    if not m: return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s

def main(site):
    t = open(glob.glob(site + '/data-*.js')[0]).read()
    bikes = json.loads(t[t.find('['):t.rfind(']') + 1])
    models = collections.OrderedDict()
    for b in bikes: models.setdefault((b['brand'], b['model']), None)
    cand = json.load(open('verify/yt_candidates.json'))
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)).strftime('%Y-%m-%dT%H:%M:%SZ')
    ok = {i: v for i, v in cand.items() if v.get('em') == 1 and v.get('pv') == 'public' and v.get('lv') in (None, 'none')
          and seconds(v.get('du')) >= 60}
    for v in ok.values(): v['t'] = html.unescape(v['t'])
    # not reviews: sale listings, setup guides, parts and repairs; plus videos a reviewer judged wrong (verify/yt_reject.json)
    JUNK = re.compile(r'refurb|gebruikte|te koop|for sale|demo bikes|assembl|tutorial|quick start|how to (enable|install|assemble)|recall|battery w|tire blowout|install|accessor|spare part|how to |replacement|fitting|stroller|wagon|giveaway|sizing', re.I)
    NOFAM = set(json.load(open('verify/yt_nofamily.json'))) if os.path.exists('verify/yt_nofamily.json') else set()
    rej = json.load(open('verify/yt_reject.json')) if os.path.exists('verify/yt_reject.json') else {}   # {"Brand|Model": [ids]}
    FOREIGN = re.compile(r'\b(de|het|een|voor|van|fiets|und|der|die|das|mit|für|ist|zum|rower|na|miasta|otro|mundo|elcykel|erfahrung|vergleich|prueba|bicicleta|vélo|elektrische)\b|[^\x00-\u024f\u2000-\u2bff\U0001F000-\U0001FAFF\s]', re.I)
    ok = {i: v for i, v in ok.items() if not JUNK.search(v['t'])
          and (not v.get('la') or v['la'].lower().startswith('en')) and not FOREIGN.search(v['t'])}
    titles = {i: norm(v['t']) for i, v in ok.items()}
    by_brand = collections.defaultdict(list)
    for (br, mo) in models: by_brand[br].append(mo)
    out = {}; pool = {}
    for br, mos in by_brand.items():
        bps = BRAND_NAMES.get(br, [norm(br)])
        vids = [i for i, tt in titles.items() if any(has(tt, bp) for bp in bps)]
        cores = {mo: core(mo, bps) for mo in mos}
        full = set(' '.join(c) for c in cores.values())
        fams = {mo: families(mo, bps) for mo in mos}
        # a one-word name that is also an everyday word ("One", "Cargo", "Family") only counts right after the brand
        def phrase(k):
            p = ' '.join(k)
            return (bps[0] + ' ' + p) if len(k) == 1 and (k[0] in GENERIC or len(k[0]) <= 3 and not any(ch.isdigit() for ch in k[0]) and k[0] not in ('gsd','hsd','nbd','rfa')) else p
        def pick(names):
            """names: {model: [phrase tokens]}; a video goes to the model(s) whose matched phrase is longest"""
            got = collections.defaultdict(list)
            for i in vids:
                tt = titles[i]
                hits = [(len(k), mo) for mo, ks in names.items() for k in ks if k and has(tt, phrase(k))]
                if hits:
                    best = max(h[0] for h in hits)
                    for n, mo in set(hits):
                        if n == best: got[mo].append(i)
            return got
        # exact model name only: a family fallback put sister models' reviews on the wrong bike (Vektron P5i on Vektron Q9)
        # 2nd step: reviewers drop or reorder words the list uses ("XP4 750 Long-Range" is reviewed as "XP4 750",
        # "Arroyo C5 Elite" as "Arroyo C5 HMB Elite"): every identifying word must be in the title, in any order.
        # Each match from this step is checked by a reviewer before it is shown (verify/yt_reject.json).
        def keys(mo):
            k = [t for t in cores[mo] if t not in FILLER]
            return k if k and (len(k) >= 2 or any(ch.isdigit() for ch in k[0]) or len(k[0]) >= 4) else []
        def pick_any(names):
            got = collections.defaultdict(list)
            for i in vids:
                ws = set(titles[i].split())
                hits = [(len(k), mo) for mo, k in names.items() if k and all(t in ws for t in k)]
                if hits:
                    best = max(h[0] for h in hits)
                    for n, mo in set(hits):
                        if n == best: got[mo].append(i)
            return got
        l1, l2 = pick({mo: [c] for mo, c in cores.items()}), pick_any({mo: keys(mo) for mo in mos})
        # 3rd step (Chris: "same model family is OK"): a general review of the family ("Tern GSD") may fill open spots,
        # but never one that names a different model code ("GSD S10" on the GSD P10) or that matched another bike
        taken = collections.defaultdict(set)
        for lv in (l1, l2):
            for mo, ids in lv.items():
                for i in ids: taken[i].add(mo)
        CODE = re.compile(r'\b[A-Za-z]{1,2}\d{1,4}[A-Za-z]{0,2}\b')
        l3 = collections.defaultdict(list)
        for mo in mos:
            if br + '|' + mo in NOFAM: continue   # family name too common a word for this bike ("Adventure", "Flyer")
            own = {c.lower() for c in CODE.findall(clean_model(mo))}
            for f in fams[mo]:
                if ' '.join(f) in full: continue
                for i in vids:
                    if taken[i] - {mo}: continue
                    if not has(titles[i], phrase(f)): continue
                    if {c.lower() for c in CODE.findall(ok[i]['t'])} - own: continue
                    if i not in l3[mo]: l3[mo].append(i)
        levels = [l1, l2, l3]
        for mo in mos:
            ids = []
            for lv in levels:
                # the last 2 years first (most viewed), then older reviews fill any open spots: older bikes only have older reviews
                for i in sorted(lv.get(mo, []), key=lambda i: (ok[i]['d'] < since, -ok[i]['vw'])):
                    if i not in ids and i not in rej.get(br + '|' + mo, ()): ids.append(i)
                if len(ids) >= 3: break
            pool[br + '|' + mo] = [[i, ok[i]['t'], ok[i]['vw']] for i in ids]
            ids = ids[:3]
            out[br + '|' + mo] = [{'id': i, 't': ok[i]['t'], 'c': ok[i]['c'], 'd': ok[i]['d'][:10], 'vw': ok[i]['vw'],
                                   'du': seconds(ok[i]['du'])} for i in ids]
    json.dump(out, open('verify/videos.json', 'w'), indent=1, ensure_ascii=False)
    json.dump(pool, open('verify/yt_pool.json', 'w'), indent=1, ensure_ascii=False)
    n = collections.Counter(len(v) for v in out.values())
    print('models', len(out), '| with 3:', n[3], '2:', n[2], '1:', n[1], 'none:', n[0])
    return out

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '..')
