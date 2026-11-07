"""Compares two snapshots made by snapshot.js: which bikes' text changed, and how many pixels each screenshot changed.
    python3 tests/compare.py <before folder> <after folder>
"""
import difflib, glob, json, os, sys

from PIL import Image, ImageChops

a, b = sys.argv[1:3]
bad = 0
for f in sorted(glob.glob(os.path.join(a, '*-text.json'))):
    n = os.path.basename(f)
    A, B = json.load(open(f)), json.load(open(os.path.join(b, n)))
    for part in ('bikes', 'cards'):
        gone = sorted(set(A[part]) - set(B[part])); new = sorted(set(B[part]) - set(A[part]))
        changed = sorted(k for k in set(A[part]) & set(B[part]) if A[part][k] != B[part][k])
        if gone or new or changed: bad += 1
        print(f'{n} {part}: {len(A[part])} before, {len(B[part])} after; gone {gone[:5]}, new {new[:5]}, changed {len(changed)}')
        for k in changed[:3]:
            print('   ', k, ''.join(difflib.unified_diff(A[part][k].splitlines(1), B[part][k].splitlines(1), n=0))[:600])
for f in sorted(glob.glob(os.path.join(a, '*-shops.txt'))):
    if open(f).read() != open(os.path.join(b, os.path.basename(f))).read(): bad += 1; print(os.path.basename(f), 'shops page text changed')
for f in sorted(glob.glob(os.path.join(a, '*.png'))):
    g = os.path.join(b, os.path.basename(f))
    if not os.path.exists(g): bad += 1; print(os.path.basename(f), 'missing after'); continue
    x, y = Image.open(f).convert('RGB'), Image.open(g).convert('RGB')
    if x.size != y.size: bad += 1; print(os.path.basename(f), 'size', x.size, '->', y.size); continue
    d = ImageChops.difference(x, y).convert('L').point(lambda v: 255 if v > 24 else 0)
    pct = 100 * sum(d.histogram()[255:]) / (x.size[0] * x.size[1])
    if pct > 0.1: bad += 1
    print(f'{os.path.basename(f)}: {pct:.2f}% of pixels changed')
print('DIFFERENCES:', bad)
sys.exit(1 if bad else 0)
