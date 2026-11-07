"""The bike list: verify/cards.json, one entry per bike the site shows, in the site's order. Every part of the build
reads and writes bikes through here, so the file's layout lives in one place.

    cards = bikedata.load()      # list of bike dicts; each has a fixed "id" (e.g. "lectric-xp4-500")
    ...change, add or remove cards in that list...
    bikedata.save(cards)         # writes that list back

A bike: id, brand, model, type (Standard / Cargo / Adaptive: sets the rebate), shops (keys of shops.json), the specs
(cls spd tq wh range wt load height fold motor, wtnb when the weight is without battery), price, pnote (price note),
src (where the specs come from), st (None, 'disc' or 'na'), img (main photo) and cv (colors: n name, f color family,
hex, img). Photos are verify/cardphotos/<img>.webp.
"""
import json, os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify', 'cards.json')


def load():
    cards = json.load(open(PATH))
    ids = [c['id'] for c in cards]
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice: raise SystemExit(f'verify/cards.json: these ids are on more than one bike: {twice}')
    return cards


def save(cards):
    with open(PATH, 'w') as f:
        json.dump(cards, f, indent=0)
        f.write('\n')


def by_id():
    return {c['id']: c for c in load()}
