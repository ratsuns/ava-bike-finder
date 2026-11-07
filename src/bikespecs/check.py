"""Lists what is wrong with the specs. Changes nothing.

    python3 -m bikespecs.check              (from src/) the problems, and how many specs are in each state
    python3 -m bikespecs.check unverified   also lists the specs in that state (any state from policy.shown)

Problems:
  no_file    a bike on the site has no source file
  no_bike    a source file, or a bike named in policy.py / spec_keep_site.json, isn't on the site
  bad_quote  a source's words don't back its number
  differs    the site shows something other than what the rule (policy.shown) gives: run bikespecs.apply
  status     the rule says discontinued, the site doesn't
"""
import collections, sys

import bikedata

from . import evidence, policy
from .rules import FIELDS, same, supports


def check():
    """-> (problems [(bike id, field, kind, detail)], specs [(bike id, field, state, value)])"""
    files = evidence.load_all()
    cards = bikedata.by_id()
    named = files.keys() | {i for i, _ in policy.KEEP_SITE} | policy.PRICE.keys() | policy.DISCONTINUED | policy.STILL_SOLD
    problems = [(i, '', 'no_bike', 'not on the site') for i in sorted(named - cards.keys())]
    specs = []
    for i, card in cards.items():
        ev = files.get(i)
        if not ev:
            problems.append((i, '', 'no_file', 'no source file yet')); continue
        for f in FIELDS:
            srcs = ev['fields'].get(f, [])
            for s in srcs:
                for v in (s.get('value'), s.get('max_mph')):
                    if not supports(f, v, s.get('quote')):
                        problems.append((i, f, 'bad_quote', f"{s.get('kind')} source's words don't contain {v!r}: {s.get('quote')!r} ({s.get('url')})"))
            v, why = policy.shown(f, card, srcs)
            specs.append((i, f, why, v))
            if not same(f, card.get(f), v):
                problems.append((i, f, 'differs', f'site shows {card.get(f)!r}, the rule gives {v!r} ({why})'))
            if f == 'wt' and bool(card.get('wtnb')) != policy.no_battery(srcs, card.get('wt')):
                problems.append((i, 'wtnb', 'differs', f"site shows \"(no battery)\": {bool(card.get('wtnb'))}, the rule gives {not card.get('wtnb')}"))
        if policy.discontinued(i, ev.get('status')) and card.get('st') != 'disc':
            problems.append((i, 'status', 'status', 'discontinued, but the site does not say so'))
    return problems, specs


if __name__ == '__main__':
    problems, specs = check()
    for p in problems: print(' | '.join(p))
    for i, f, why, v in specs:
        if why in sys.argv[1:]: print(f'{i} {f}: {v!r} ({why})')
    print('specs by state:', dict(collections.Counter(s[2] for s in specs)))
    print('problems:', dict(collections.Counter(p[2] for p in problems)) or 'none')
