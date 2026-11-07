"""The bike list: verify/cards.json, one entry per bike the site shows. Every part of the build reads and writes
bikes through here, so the file's layout lives in one place.

    cards = bikedata.load()      # list of bike dicts; each has a fixed "id" (e.g. "lectric-xp4-500")
    ...change cards in place...
    bikedata.save()              # writes them back
"""
import json, os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify', 'cards.json')
_raw = None


def load():
    global _raw
    _raw = json.load(open(PATH))
    return [c for rows in _raw.values() if isinstance(rows, list) for c in rows]


def save():
    with open(PATH, 'w') as f:
        json.dump(_raw, f, indent=0)
        f.write('\n')


def by_id():
    return {c['id']: c for c in load()}
