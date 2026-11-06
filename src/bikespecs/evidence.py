"""The per-bike source files: bikespecs/bikes/<brand-model>.json

{
 "bike": "Velotric|Fold 1 Plus",
 "checked": "2026-11-06",
 "fields": {
   "range": [
     {"kind": "maker",  "value": "68", "url": "https://www.velotricbike.com/...", "quote": "Pedal Assist Range 68 Miles"},
     {"kind": "review", "value": "68", "url": "https://newatlas.com/...",        "quote": "68 miles (109 km) at the lowest PAS"}
   ],
   ...
 },
 "status": {"sources": [{"kind": "maker", "value": "discontinued", "url": "...", "quote": "... is no longer available"}]},
 "notes": ""
}
A source with "value": null records that it was read and doesn't give that spec. "basis" may say what a figure means
(e.g. load "total" when the maker only gives bike + rider + cargo, weight "without battery").
"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
DIR = os.path.join(HERE, 'bikes')
CARDS = os.path.join(SRC, 'verify', 'cards.json')


def key(card): return f"{card['brand']}|{card['model']}"


def slug(k):
    """the file name for a bike: "Velotric|Fold 1 Plus" -> velotric-fold-1-plus; "+" is "plus" so "C380" and "C380+" differ"""
    return re.sub(r'[^a-z0-9]+', '-', k.lower().replace('+', ' plus ').replace('!', '')).strip('-')


def path(k): return os.path.join(DIR, slug(k) + '.json')


def load(k):
    p = path(k)
    return json.load(open(p)) if os.path.exists(p) else None


def save(data):
    os.makedirs(DIR, exist_ok=True)
    json.dump(data, open(path(data['bike']), 'w'), indent=1, ensure_ascii=False)


def load_all():
    return {d['bike']: d for d in (json.load(open(p)) for p in sorted(glob.glob(os.path.join(DIR, '*.json'))))}


def rename_all():
    """move every file to the name its bike should have (after a change to slug())"""
    for p in glob.glob(os.path.join(DIR, '*.json')):
        want = path(json.load(open(p))['bike'])
        if p != want and not os.path.exists(want): os.rename(p, want)


def cards():
    """[(card id, card)] for every bike card the site shows, from verify/cards.json"""
    C = json.load(open(CARDS))
    return [(f'{i}.{j}', c) for i, L in C.items() if isinstance(L, list) for j, c in enumerate(L)]
