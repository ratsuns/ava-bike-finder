"""videos.csv -> the site's video file (videos-<hash>.json), after the check passes.

    python3 -m videos.publish <site folder> [--drop-unavailable]    (run from src/)
checks, writes the file and points index.html at it. --drop-unavailable first takes videos YouTube no longer shows
(removed, private, not embeddable) out of videos.csv; the weekly GitHub Action uses it. build2.py calls write() directly.
"""
import csv, glob, hashlib, html, json, os, re, sys

from .check import check, unavailable
from .rules import seconds
from .test_rules import run as test_rules

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
CSV = os.path.join(SRC, 'videos.csv')
META = os.path.join(SRC, 'verify', 'video_meta.json')
LINK = re.compile(r'(?:embed/|v=|youtu\.be/|shorts/)([\w-]{11})(?![\w-])')


def load_csv(path=CSV):
    """{"Brand|Model": [video ids]} in the order listed; a cell that is not a YouTube video link stops everything"""
    entries = {}
    for row in csv.DictReader(open(path, encoding='utf-8-sig')):
        key, ids = f"{row['Brand'].strip()}|{row['Model'].strip()}", []
        for col in ('Video 1', 'Video 2', 'Video 3'):
            cell = (row.get(col) or '').strip()
            if not cell: continue
            m = LINK.search(cell)
            if not m: raise SystemExit(f'videos.csv, {key}, {col}: not a YouTube video link: {cell}')
            ids.append(m.group(1))
        entries[key] = ids
    return entries


def save_csv(entries, path=CSV):
    """write the lists back in the file's own row order"""
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['Brand', 'Model', 'Video 1', 'Video 2', 'Video 3'])
        w.writeheader()
        for r in rows:
            ids = entries[f"{r['Brand'].strip()}|{r['Model'].strip()}"]
            w.writerow({'Brand': r['Brand'], 'Model': r['Model'],
                        **{f'Video {n + 1}': 'https://www.youtube.com/watch?v=' + ids[n] if n < len(ids) else '' for n in range(3)}})


def drop_unavailable(entries, meta):
    """take out videos YouTube no longer shows; returns [(bike, video, why)]"""
    dropped = [(k, i, unavailable(meta[i])) for k, ids in entries.items() for i in ids if i in meta and unavailable(meta[i])]
    for k, i, _ in dropped: entries[k].remove(i)
    return dropped


def load_meta(path=META):
    return json.load(open(path)) if os.path.exists(path) else {}


def models_on_site(site):
    t = open(glob.glob(os.path.join(site, 'data-*.js'))[0]).read()
    return sorted({(b['brand'], b['model']) for b in json.loads(t[t.find('['):t.rfind(']') + 1])})


def write(site, models, entries=None, meta=None):
    """test the title rules, check every video, then write videos-<hash>.json into the site folder (removing older
    ones); returns its file name"""
    failed = test_rules()
    if failed: raise SystemExit('The title rules in rules.py are broken, nothing was published:\n' + '\n'.join(failed))
    entries = load_csv() if entries is None else entries
    meta = load_meta() if meta is None else meta
    problems = check(entries, meta, models)
    if problems:
        raise SystemExit('Video check failed, nothing was published:\n' + '\n'.join(' | '.join(p) for p in problems))
    data = {k: [[i, html.unescape(meta[i]['t']), meta[i]['c'], meta[i]['vw'], meta[i]['d'][:10], seconds(meta[i]['du'])]
                for i in ids] for k, ids in entries.items() if ids}
    text = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    assert 'AIza' not in text  # never publish an API key
    name = 'videos-' + hashlib.md5(text.encode()).hexdigest()[:8] + '.json'
    for old in glob.glob(os.path.join(site, 'videos-*.json')):
        if os.path.basename(old) != name: os.remove(old)
    open(os.path.join(site, name), 'w').write(text)
    return name


def point_page_at(site, name):
    """index.html loads the video file by name; point it at the new one"""
    page = os.path.join(site, 'index.html')
    text = open(page).read()
    new = re.sub(r'videos-[0-9a-f]{8}\.json', name, text)
    if new != text: open(page, 'w').write(new)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    site = os.path.abspath(args[0] if args else os.path.join(SRC, '..'))
    entries, meta = load_csv(), load_meta()
    if '--drop-unavailable' in sys.argv:
        for k, i, why in drop_unavailable(entries, meta): print('dropped', k, i, '-', why)
        save_csv(entries)
    name = write(site, models_on_site(site), entries, meta)
    point_page_at(site, name)
    print(name, '|', sum(1 for v in entries.values() if v), 'of', len(entries), 'bikes have videos')
