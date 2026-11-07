"""The accuracy check for videos.csv. The build runs it; any problem stops the build.

Every video on a bike must:
  - be known to YouTube right now: public, allowed to play on other sites, not live
  - be at least a minute long (no Shorts) and in English (rules.py)
  - be listed once per bike
  - have a title about that bike (rules.py)
"""
import bikedata
from .rules import bikes_from, seconds

MIN_SECONDS = 60


def unavailable(v):
    """why YouTube no longer lets this video be shown, or None (refresh.py takes these out of videos.csv)"""
    if v.get('gone'): return 'YouTube no longer has this video'
    if v.get('pv') != 'public' or v.get('em') != 1: return 'not public, or not allowed to play on other sites'
    if v.get('lv') not in (None, 'none'): return 'a live stream'
    return None


def problem(v, bike):
    """(kind, why) for this video (its YouTube data) on this bike: kind is 'model' or 'family' when it can go on the
    bike (see Bike.match), None when it can't, and then why says why"""
    if not v: return None, 'no YouTube data for this video (run refresh.py)'
    gone = unavailable(v)
    if gone: return None, gone
    if seconds(v.get('du')) < MIN_SECONDS: return None, 'shorter than a minute'
    kind, why = bike.match(v.get('t', ''), v.get('la'))
    return kind, why and f'{why}: "{v.get("t", "")}"'


def check(entries, meta, ids):
    """entries {bike id: [video ids]}, meta {video id: YouTube data}, ids: the bikes on the site -> [(bike, video, problem)]"""
    cards = bikedata.by_id()
    bikes = bikes_from([cards[i] for i in ids])
    problems = [(bike, '', 'no row in videos.csv') for bike in sorted(set(bikes) - set(entries))]
    for key, vids in entries.items():
        bike = bikes.get(key)
        if not bike:
            problems.append((key, '', 'not a bike on the site (check the id against verify/cards.json)')); continue
        if len(vids) != len(set(vids)):
            problems.append((key, '', 'the same video is listed twice'))
        problems += [(key, vid, why) for vid in vids for kind, why in [problem(meta.get(vid), bike)] if not kind]
    return problems
