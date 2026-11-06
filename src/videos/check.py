"""The accuracy check for videos.csv. The build and the GitHub Action run it; any problem stops the publish.

Every video on a bike must:
  - be known to YouTube right now: public, allowed to play on other sites, not live
  - be at least a minute long (no Shorts) and in English (or with no language set and an English title)
  - be listed once per bike
  - have a title about that bike (rules.py)
"""
from .rules import bikes_from, seconds

MIN_SECONDS = 60


def unavailable(v):
    """why YouTube no longer lets this video be shown, or None (the weekly refresh drops these videos on its own)"""
    if v.get('gone'): return 'YouTube no longer has this video'
    if v.get('pv') != 'public' or v.get('em') != 1: return 'not public, or not allowed to play on other sites'
    if v.get('lv') not in (None, 'none'): return 'a live stream'
    return None


def problem(v, bike):
    """why this video (its YouTube data) can't go on this bike, or None. find.py uses the same rules."""
    if not v: return 'no YouTube data for this video (run refresh.py)'
    gone = unavailable(v)
    if gone: return gone
    if seconds(v.get('du')) < MIN_SECONDS: return 'shorter than a minute'
    if v.get('la') and not v['la'].lower().startswith('en'): return f"not in English ({v['la']})"
    kind, why = bike.match(v.get('t', ''))
    return None if kind else f'{why}: "{v.get("t", "")}"'


def check(entries, meta, models):
    """entries {"Brand|Model": [video ids]}, meta {id: YouTube data}, models [(brand, model)] -> [(bike, video, problem)]"""
    bikes = bikes_from(models)
    problems = [(key, '', 'no row in videos.csv') for key in sorted(set(bikes) - set(entries))]
    for key, ids in entries.items():
        bike = bikes.get(key)
        if not bike:
            problems.append((key, '', 'not a bike on the list (check the brand and model spelling)')); continue
        if len(ids) != len(set(ids)):
            problems.append((key, '', 'the same video is listed twice'))
        problems += [(key, vid, p) for vid in ids for p in [problem(meta.get(vid), bike)] if p]
    return problems
