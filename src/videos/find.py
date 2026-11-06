"""Suggest videos for bikes that have fewer than 3 in videos.csv. Suggestions only: nothing here reaches the site.

    python3 -m videos.find        (run from src/) -> verify/video_suggestions.csv

Looks through verify/yt_candidates.json (videos collected from YouTube's channel lists and searches) with the same
rules the check uses, newest reviews first (last 2 years by views), then older ones; videos judged wrong before are
listed in verify/yt_reject.json and skipped. Copy good ones into videos.csv; the check still runs on publish.
"""
import csv, datetime, json, os, re

from .publish import CSV, SRC, load_csv, models_on_site
from .check import problem
from .rules import bikes_from

CANDIDATES = os.path.join(SRC, 'verify', 'yt_candidates.json')
REJECTED = os.path.join(SRC, 'verify', 'yt_reject.json')
OUT = os.path.join(SRC, 'verify', 'video_suggestions.csv')
NOT_A_REVIEW = re.compile(r'refurb|for sale|assembl|tutorial|quick start|how to |recall|install|accessor|spare part|'
                          r'replacement|stroller|giveaway|sizing|unboxing only|battery for|charger|garage|trailer|podcast', re.I)


def suggest(entries, models, cand, rejected):
    """for each bike with fewer than 3 videos: the best candidates that pass the check, exact model names first, then
    reviews from the last 2 years, then by views"""
    bikes = bikes_from(models)
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)).isoformat()
    reviews = {i: v for i, v in cand.items() if not NOT_A_REVIEW.search(v.get('t', ''))}
    out = []
    for key, bike in bikes.items():
        have = entries.get(key, [])
        if len(have) >= 3: continue
        found = []
        for i, v in reviews.items():
            if i in have or i in rejected.get(key, ()) or problem(v, bike): continue
            kind, _ = bike.match(v['t'])
            found.append((kind != 'model', v.get('d', '') < since, -v.get('vw', 0), i, kind))
        for _, _, _, i, kind in sorted(found)[:3 - len(have)]:
            out.append([bike.brand, bike.model, kind, 'https://www.youtube.com/watch?v=' + i, cand[i]['t'], cand[i]['vw'], cand[i]['d'][:10]])
    return out

if __name__ == '__main__':
    entries = load_csv(CSV)
    models = models_on_site(os.path.join(SRC, '..'))
    rows = suggest(entries, models, json.load(open(CANDIDATES)),
                   json.load(open(REJECTED)) if os.path.exists(REJECTED) else {})
    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Brand', 'Model', 'Names', 'Link', 'Title', 'Views', 'Published'])
        w.writerows(rows)
    print(len(rows), 'suggestions for', len({(r[0], r[1]) for r in rows}), 'bikes ->', OUT)
