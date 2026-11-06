"""Accuracy check for the video reviews. The build runs it before writing the videos file and stops if anything fails.

A video shown on a bike must:
  1. be public and allowed to play on other sites (from YouTube's own data in verify/yt_candidates.json)
  2. name that bike in its title: the bike's brand, or its distinctive model name
  3. not name a different bike's model code from the list ("Iconic EVO 2" on the Evo TR 1, "GSD S10" on the GSD P10)
Videos a person approved by hand after a failed check go in verify/yt_approved.json ({"Brand|Model": [ids]}).
"""
import json, os, re, html, importlib.util

_spec = importlib.util.spec_from_file_location('ytm', os.path.join(os.path.dirname(__file__), 'yt_match.py'))
m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(m)
CODE = re.compile(r'\b[A-Za-z]{1,2}\d{1,4}[A-Za-z]{0,2}\b')


def family_names(model, core, bps):
    """the model family, counted only together with the brand:
    the words before the first number or model code ("GSD P10" -> gsd, "Boost EVO 5" -> boost, "Element Core" -> element),
    the model's first word when it carries its own number ("46er Performance" -> 46er), and the shorter names
    yt_match.families() finds by dropping trailing trim words ("Level 4 REC" -> level 4)"""
    out = []
    lead = []
    for w in core:
        if any(ch.isdigit() for ch in w) or len(w) <= 2 or w in ('evo', 'gen'): break
        if w != 'the': lead.append(w)
    if lead and lead != core: out.append(lead)
    first = m.norm(m.clean_model(model).split()[0]) if model.split() else ''
    if first and any(ch.isdigit() for ch in first) and any(ch.isalpha() for ch in first): out.append(first.split())
    out += [f for f in m.families(model, bps) if f != core]
    if len(core) > 1 and core[0] not in m.GENERIC and len(core[0]) >= 4: out.append([core[0]])
    return out


def check(videos, models, cand, approved=None):
    """videos: {"Brand|Model": [{id, ...}]}; models: [(brand, model)]; returns a list of problems (empty = all good)"""
    approved = approved or {}
    by_brand = {}
    for br, mo in models: by_brand.setdefault(br, []).append(mo)
    problems = []
    for key, vids in videos.items():
        br, mo = key.split('|', 1)
        bps = m.BRAND_NAMES.get(br, [m.norm(br)])
        core = m.core(mo, bps)
        own_codes = {c.lower() for c in CODE.findall(m.clean_model(mo))}
        sibling_codes = {c.lower() for other in by_brand.get(br, []) if other != mo
                         for c in CODE.findall(m.clean_model(other))} - own_codes
        for v in vids:
            i = v['id']; c = cand.get(i)
            if i in approved.get(key, []): continue
            if not c:
                problems.append((key, i, 'not a known YouTube video')); continue
            if c.get('em') != 1 or c.get('pv') != 'public':
                problems.append((key, i, 'not public or not allowed to play on other sites')); continue
            title = html.unescape(c['t']); t = m.norm(title); words = set(t.split())
            keys = [w for w in core if w not in m.FILLER and w != 'the'] or core
            names_model = bool(keys) and (all(w in words for w in keys)          # every identifying word, any order
                                          or m.has(t, ' '.join(keys)))           # or written together ("CarbonJoy", "FastRack")
            names_family = any(m.has(t, m.phrase_of(f, bps)) for f in family_names(mo, core, bps))
            names_brand = any(m.has(t, bp) for bp in bps)
            if not names_model and not (names_brand and names_family):
                problems.append((key, i, f'title does not name this bike: "{title}"')); continue
            if not names_brand and not m.distinctive(core):
                problems.append((key, i, f'title names the model but not the brand, and the name is too common: "{title}"')); continue
            other = {x.lower() for x in CODE.findall(title)} & sibling_codes
            if other and not names_model:          # a comparison that names this bike too is fine
                problems.append((key, i, f'title names another model ({", ".join(sorted(other))}): "{title}"'))
    return problems


if __name__ == '__main__':
    import glob, sys
    site = sys.argv[1] if len(sys.argv) > 1 else '..'
    t = open(glob.glob(site + '/data-*.js')[0]).read()
    bikes = json.loads(t[t.find('['):t.rfind(']') + 1])
    models = sorted({(b['brand'], b['model']) for b in bikes})
    cand = json.load(open('verify/yt_candidates.json'))
    appr = json.load(open('verify/yt_approved.json')) if os.path.exists('verify/yt_approved.json') else {}
    p = check(json.load(open('verify/videos.json')), models, cand, appr)
    for x in p: print(' | '.join(x))
    print(len(p), 'problems')
