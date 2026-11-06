"""Every spec the site shows must be what its sources back (rules.py). Lists what isn't.

    python3 -m bikespecs.check            (from src/) summary, and the bikes that need work
    python3 -m bikespecs.check --strict   exit 1 on any problem (the build uses this)
"""
import collections, sys

from . import evidence
from .rules import FIELDS, agree, decide, supports


def check():
    """-> list of (bike, field, problem); problem kinds: no_file, bad_quote, differs, should_be_blank"""
    files = evidence.load_all()
    out = []
    for _, card in evidence.cards():
        k = evidence.key(card)
        ev = files.get(k)
        if not ev:
            out.append((k, '', 'no_file', 'no source file yet')); continue
        for f in FIELDS:
            srcs = ev.get('fields', {}).get(f, [])
            for s in srcs:
                if s.get('value') not in (None, '') and not supports(f, s['value'], s.get('quote')):
                    out.append((k, f, 'bad_quote', f"{s.get('kind')} source's words don't contain {s['value']!r}: {s.get('quote')!r} ({s.get('url')})"))
            d = decide(f, srcs)
            shown = card.get(f)
            if d['show'] and not agree(f, shown, d['value']):
                out.append((k, f, 'differs', f"site shows {shown!r}, sources back {d['value']!r} ({d['why']})"))
            if not d['show'] and shown not in (None, ''):
                out.append((k, f, 'should_be_blank', f"site shows {shown!r} but it isn't backed ({d['why']})"))
    return out


def summary():
    files = evidence.load_all()
    states = collections.Counter(decide(f, files[evidence.key(c)].get('fields', {}).get(f, []))['state']
                                 for _, c in evidence.cards() if evidence.key(c) in files for f in FIELDS)
    return states


if __name__ == '__main__':
    problems = check()
    kinds = collections.Counter(p[2] for p in problems)
    print('specs by state:', dict(summary()))
    print('problems:', dict(kinds) or 'none')
    for p in problems:
        if p[2] != 'no_file' or '--all' in sys.argv: print(' | '.join(p))
    if '--strict' in sys.argv and problems: sys.exit(1)
