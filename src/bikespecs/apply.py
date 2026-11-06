"""Write what the sources back into verify/cards.json (what the build uses), and list every change.

    python3 -m bikespecs.apply      (from src/) -> verify/cards.json updated, verify/spec_changes.json lists the changes
Only bikes with a source file are touched. A spec the sources don't back is cleared, so the site leaves it out.
"""
import json

from . import evidence
from .rules import FIELDS, agree, decide, discontinued

CHANGES = evidence.CARDS.replace('cards.json', 'spec_changes.json')


def apply():
    C = json.load(open(evidence.CARDS))
    files = evidence.load_all()
    changes, flagged = [], []
    for i, L in C.items():
        if not isinstance(L, list): continue
        for c in L:
            ev = files.get(evidence.key(c))
            if not ev: continue
            for f in FIELDS:
                srcs = ev.get('fields', {}).get(f, [])
                d = decide(f, srcs)
                new = d['value'] if d['show'] else None
                if f == 'cls' and new is not None: new = int(float(new))
                if d['state'] == 'conflict': flagged.append(dict(bike=evidence.key(c), field=f, shown=new, why=d['why'], sources=srcs))
                if not agree(f, c.get(f), new) and not (c.get(f) in (None, '') and new is None):
                    changes.append(dict(bike=evidence.key(c), field=f, before=c.get(f), after=new, state=d['state'], why=d['why'],
                                        sources=[{k: s.get(k) for k in ('kind', 'value', 'url', 'quote')} for s in srcs]))
                    c[f] = new
                if f == 'wt':
                    nb = any(s.get('kind') == 'maker' and s.get('basis') == 'without battery' and agree('wt', s.get('value'), new) for s in srcs)
                    if nb: c['wtnb'] = True
                    else: c.pop('wtnb', None)
            if discontinued(ev.get('status')) and c.get('st') != 'disc':
                changes.append(dict(bike=evidence.key(c), field='status', before=c.get('st'), after='disc', state='confirmed',
                                    why='the maker, or two sources, say it is discontinued', sources=ev['status']['sources']))
                c['st'] = 'disc'
    json.dump(C, open(evidence.CARDS, 'w'), indent=0)
    open(evidence.CARDS, 'a').write('\n')
    json.dump(dict(changes=changes, conflicts=flagged), open(CHANGES, 'w'), indent=1, ensure_ascii=False)
    return changes, flagged


if __name__ == '__main__':
    ch, fl = apply()
    print(len(ch), 'changes,', len(fl), 'conflicts listed ->', CHANGES)
