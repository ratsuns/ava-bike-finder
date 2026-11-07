"""Write what the site shows (policy.py) into verify/cards.json and print every change.

    python3 -m bikespecs.apply      (from src/)
"""
import bikedata

from . import evidence, policy
from .rules import FIELDS, agree, same


def apply():
    files = evidence.load_all()
    cards = bikedata.load()
    changes = []
    for c in cards:
        ev = files.get(c['id'])
        if not ev: continue
        for f in FIELDS:
            srcs = ev['fields'].get(f, [])
            new, why = policy.shown(f, c, srcs)
            if not same(f, c.get(f), new):
                changes.append(f"{c['id']} {f}: {c.get(f)!r} -> {new!r} ({why})")
                c[f] = new
            if f == 'wt':
                if any(s.get('kind') == 'maker' and s.get('basis') == 'without battery' and agree('wt', s.get('value'), c.get('wt')) for s in srcs):
                    c['wtnb'] = True
                else: c.pop('wtnb', None)
        if policy.discontinued(c['id'], ev.get('status')) and c.get('st') != 'disc':
            changes.append(f"{c['id']} status: {c.get('st')!r} -> 'disc'")
            c['st'] = 'disc'
    bikedata.save(cards)
    return changes


if __name__ == '__main__':
    ch = apply()
    print('\n'.join(ch), f'\n{len(ch)} changes written to verify/cards.json')
