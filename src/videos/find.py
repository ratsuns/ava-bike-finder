"""Suggest videos for bikes that have fewer than files.PER_BIKE in videos.csv. Suggestions only: nothing here reaches the site.

    python3 -m videos.find        (run from src/) -> verify/video_suggestions.csv

Looks through verify/yt_candidates.json (videos collected from YouTube's channel lists and searches) with the same
rules the check uses, newest reviews first (last 2 years by views), then older ones; videos judged wrong before are
listed in verify/yt_reject.json and skipped. Copy good ones into videos.csv; the check still runs on every build.
"""
import datetime, re

import bikedata
from . import files
from .check import problem
from .rules import bikes_from

NOT_A_REVIEW = re.compile(r'refurb|for sale|assembl|tutorial|quick start|how to |recall|install|accessor|spare part|'
                          r'replacement|stroller|giveaway|sizing|unboxing only|battery for|charger|garage|trailer|podcast', re.I)


def suggest(entries, cards, cand, rejected):
    """for each bike with room for more videos: the best candidates that pass the check, exact model names first, then
    reviews from the last 2 years, then by views"""
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)).isoformat()
    reviews = {i: v for i, v in cand.items() if not NOT_A_REVIEW.search(v.get('t', ''))}
    out = []
    for key, bike in bikes_from(cards).items():
        have = entries.get(key, [])
        if len(have) >= files.PER_BIKE: continue
        found = []
        for i, v in reviews.items():
            if i in have or i in rejected.get(key, ()): continue
            kind, _ = problem(v, bike)
            if kind: found.append((kind != 'model', v.get('d', '') < since, -v.get('vw', 0), i, kind))
        for _, _, _, i, kind in sorted(found)[:files.PER_BIKE - len(have)]:
            out.append([key, f'{bike.brand} {bike.model}', kind, 'https://www.youtube.com/watch?v=' + i, cand[i]['t'], cand[i]['vw'], cand[i]['d'][:10]])
    return out


if __name__ == '__main__':
    rows = suggest(files.load_csv(), bikedata.load(), files.load_candidates(), files.load_rejected())
    files.save_suggestions(rows)
    print(len(rows), 'suggestions for', len({r[0] for r in rows}), 'bikes ->', files.SUGGESTIONS)
