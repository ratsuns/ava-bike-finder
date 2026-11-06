"""Write what the sources back into verify/cards.json (what the build uses), following Chris's answers (policy.py),
and list every change.

    python3 -m bikespecs.apply      (from src/) -> verify/cards.json updated, verify/spec_changes.json lists the changes
Only bikes with a source file are touched.
"""
import json, re

from . import evidence, policy
from .rules import FIELDS, agree, decide, discontinued, supports

CHANGES = evidence.CARDS.replace('cards.json', 'spec_changes.json')
UNLOCK = re.compile(r'(?i)(?:adjustable|unlock\w*|set|configur\w*|raised?|up)\D{0,15}?(\d{2})\s*mph')


def highest_speed(srcs):
    """top speed is the most the bike can reach: a source that says it ships at 20 and unlocks to 28 counts as 28,
    when its own words (its quote, or page words quoted in its basis) give the 28"""
    out = []
    for s in srcs:
        m = UNLOCK.search(s.get('basis') or '')
        if m and s.get('value') not in (None, ''):
            n = int(m.group(1))
            words = ' '.join([s.get('quote') or ''] + re.findall(r"'([^']+)'", s['basis']))
            if n > float(s['value']) and supports('spd', n, words): s = dict(s, value=n, quote=words)
        out.append(s)
    return out


def shown(f, card, srcs):
    """(the value the site shows, the state it came from)"""
    k, now = evidence.key(card), card.get(f)
    if f == 'spd' and policy.SPEED == 'highest': srcs = highest_speed(srcs)
    d = decide(f, srcs)
    if (k, f) in policy.KEEP_SITE: return now, 'kept: Chris chose the site number'
    if f == 'price' and k in policy.PRICE: return policy.PRICE[k], "Chris's price"
    if d['show']: return d['value'], d['state']
    if d['state'] == 'maker_only' and policy.SHOW_MAKER_ONLY: return d['value'], 'maker_only'
    if policy.KEEP_UNBACKED and now not in (None, ''): return now, 'unverified: no source states it'
    return None, d['state']


def apply():
    C = json.load(open(evidence.CARDS))
    files = evidence.load_all()
    changes, unverified = [], []
    for i, L in C.items():
        if not isinstance(L, list): continue
        for c in list(L):
            k = evidence.key(c)
            if k in policy.REMOVE:
                L.remove(c); changes.append(dict(bike=k, field='removed', before=None, after=None, state="Chris's answer")); continue
            if k in policy.RENAME:
                changes.append(dict(bike=k, field='model', before=c['model'], after=policy.RENAME[k], state="Chris's answer"))
                c['model'] = policy.RENAME[k]; k = evidence.key(c)
            ev = files.get(k)
            if not ev: continue
            for f in FIELDS:
                srcs = ev.get('fields', {}).get(f, [])
                new, state = shown(f, c, srcs)
                if f == 'cls' and new not in (None, ''): new = int(float(new))
                if state.startswith('unverified'): unverified.append(dict(bike=k, field=f, value=new))
                if not agree(f, c.get(f), new) and not (c.get(f) in (None, '') and new in (None, '')):
                    changes.append(dict(bike=k, field=f, before=c.get(f), after=new, state=state,
                                        sources=[{x: s.get(x) for x in ('kind', 'value', 'url', 'quote')} for s in srcs]))
                    c[f] = new
                if f == 'wt':
                    nb = any(s.get('kind') == 'maker' and s.get('basis') == 'without battery' and agree('wt', s.get('value'), c.get('wt')) for s in srcs)
                    if nb: c['wtnb'] = True
                    else: c.pop('wtnb', None)
            disc = (k in policy.DISCONTINUED or discontinued(ev.get('status'))) and k not in policy.STILL_SOLD
            if disc and c.get('st') != 'disc':
                changes.append(dict(bike=k, field='status', before=c.get('st'), after='disc', state="Chris's answer or the maker / two sources"))
                c['st'] = 'disc'
    json.dump(C, open(evidence.CARDS, 'w'), indent=0)
    open(evidence.CARDS, 'a').write('\n')
    json.dump(dict(changes=changes, unverified=unverified), open(CHANGES, 'w'), indent=1, ensure_ascii=False)
    return changes, unverified


if __name__ == '__main__':
    ch, un = apply()
    print(len(ch), 'changes,', len(un), 'specs shown unverified ->', CHANGES)
