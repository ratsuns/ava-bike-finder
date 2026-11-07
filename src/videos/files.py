"""Every file the video code reads or writes.

  src/videos.csv                     one row per bike: its id (from verify/cards.json), its name for people to read,
                                     and up to PER_BIKE YouTube links
  src/verify/video_meta.json         YouTube's data for every video in videos.csv (refresh.py writes it)
  src/verify/yt_candidates.json      videos collected from YouTube for find.py to look through
  src/verify/yt_reject.json          {bike id: [video ids judged wrong for it before]}
  src/verify/video_suggestions.csv   find.py's suggestions
  <site>/videos-<hash>.json          the videos the page shows
"""
import csv, hashlib, json, os, re

import bikedata

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(SRC, 'videos.csv')
META = os.path.join(SRC, 'verify', 'video_meta.json')
CANDIDATES = os.path.join(SRC, 'verify', 'yt_candidates.json')
REJECTED = os.path.join(SRC, 'verify', 'yt_reject.json')
SUGGESTIONS = os.path.join(SRC, 'verify', 'video_suggestions.csv')
PER_BIKE = 3
COLUMNS = [f'Video {n}' for n in range(1, PER_BIKE + 1)]
LINK = re.compile(r'(?:embed/|v=|youtu\.be/|shorts/)([\w-]{11})(?![\w-])')


def load_csv():
    """{bike id: [video ids]} in the order listed; a cell that is not a YouTube video link stops everything"""
    entries = {}
    for row in csv.DictReader(open(CSV, encoding='utf-8-sig')):
        bike, ids = row['id'].strip(), []
        for col in COLUMNS:
            cell = (row.get(col) or '').strip()
            if not cell: continue
            m = LINK.search(cell)
            if not m: raise SystemExit(f'videos.csv, {bike}, {col}: not a YouTube video link: {cell}')
            ids.append(m.group(1))
        entries[bike] = ids
    return entries


def save_csv(entries):
    """write the lists back in the file's own row order, with each bike's name from the bike list"""
    rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
    names = {i: c['brand'] + ' ' + c['model'] for i, c in bikedata.by_id().items()}
    with open(CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'Bike'] + COLUMNS)
        w.writeheader()
        for r in rows:
            ids = entries[r['id'].strip()]
            w.writerow({'id': r['id'], 'Bike': names.get(r['id'].strip(), r['Bike']),
                        **{col: 'https://www.youtube.com/watch?v=' + ids[n] if n < len(ids) else '' for n, col in enumerate(COLUMNS)}})


def load_meta():
    return json.load(open(META)) if os.path.exists(META) else {}


def save_meta(meta):
    json.dump(meta, open(META, 'w'), indent=0, ensure_ascii=False, sort_keys=True)


def load_candidates():
    return json.load(open(CANDIDATES))


def load_rejected():
    return json.load(open(REJECTED)) if os.path.exists(REJECTED) else {}


def save_suggestions(rows):
    with open(SUGGESTIONS, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'Bike', 'Names', 'Link', 'Title', 'Views', 'Published'])
        w.writerows(rows)


def write_site(site, data):
    """write the page's video file into the site folder; returns its file name (build2.py removes older ones at the end)"""
    text = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    name = 'videos-' + hashlib.md5(text.encode()).hexdigest()[:8] + '.json'
    open(os.path.join(site, name), 'w').write(text)
    return name
