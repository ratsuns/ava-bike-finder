"""The per-bike source files: bikespecs/bikes/<id>.json, one for each bike on the site (id as in verify/cards.json)

{
 "id": "velotric-fold-1-plus",
 "bike": "Velotric|Fold 1 Plus",
 "checked": "2026-11-06",
 "fields": {
   "range": [
     {"kind": "maker",  "value": "68", "url": "https://www.velotricbike.com/...", "quote": "Pedal Assist Range 68 Miles"},
     {"kind": "review", "value": "68", "url": "https://newatlas.com/...",        "quote": "68 miles (109 km) at the lowest PAS"}
   ],
   "spd": [
     {"kind": "maker", "value": 20, "max_mph": 28, "url": "...", "quote": "20 mph out of the box, unlocks to 28 mph"}
   ],
   ...
 },
 "status": {"sources": [{"kind": "maker", "value": "discontinued", "url": "...", "quote": "... is no longer available"}]},
 "notes": ""
}
A source with "value": null records that it was read and doesn't give that spec. "basis" is the helper's note on what
a figure means (e.g. weight "without battery", load "total" when the maker only gives bike + rider + cargo).
"max_mph" (top speed only): the speed the source's words say the bike can be set to, when that is above "value".
"""
import glob, json, os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bikes')


def load_all():
    """{bike id: its source file}"""
    out = {}
    for p in sorted(glob.glob(os.path.join(DIR, '*.json'))):
        d = json.load(open(p))
        if os.path.basename(p) != d['id'] + '.json': raise ValueError(f'{p}: the file name must be its id, {d["id"]}.json')
        out[d['id']] = d
    return out
