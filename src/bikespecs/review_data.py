"""the review list's data: every spec the strict rule would change, with its sources (run from src/)"""
import json, sys, collections
sys.path.insert(0, '.')
from bikespecs import evidence
from bikespecs.rules import FIELDS, agree, decide, discontinued

files = evidence.load_all()
rows, disc = [], []
counts = collections.Counter()
for cid, c in evidence.cards():
    k = evidence.key(c); ev = files.get(k)
    if not ev: continue
    if discontinued(ev.get('status')) and c.get('st') != 'disc':
        disc.append(dict(b=k, s=[[s.get('kind'), s.get('url'), (s.get('quote') or '')[:220]] for s in ev['status']['sources']]))
    for f in FIELDS:
        srcs = ev.get('fields', {}).get(f, [])
        d = decide(f, srcs)
        now = c.get(f); shown = now not in (None, '')
        g = None
        if d['state'] == 'conflict': g = 'conflict'
        elif d['show'] and not agree(f, now, d['value']) and shown: g = 'change'
        elif d['show'] and not shown: g = 'add'
        elif not d['show'] and shown: g = 'maker_only' if d['state'] == 'maker_only' else 'unbacked'
        if not g: continue
        counts[g] += 1
        rows.append(dict(b=k, f=f, now=now, val=d['value'], g=g, why=d['why'],
                         s=[[s.get('kind'), s.get('value'), s.get('url'), (s.get('quote') or '')[:220], s.get('basis')] for s in srcs]))
labels = {f: v[0] for f, v in FIELDS.items()}
json.dump(dict(rows=rows, disc=disc, counts=counts, labels=labels, bikes=len(files)), open(sys.argv[1], 'w'), ensure_ascii=False, separators=(',', ':'))
print(dict(counts), 'disc', len(disc), 'rows', len(rows))
