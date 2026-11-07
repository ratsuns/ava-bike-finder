"""Fetch YouTube's current data for every video in videos.csv into verify/video_meta.json, and take the videos YouTube
no longer shows (removed, private, not embeddable, live) out of videos.csv.

    YT_API_KEY=... python3 -m videos.refresh        (run from src/; the GitHub Action does this with the key from its secrets)

Costs 1 unit of the free 10,000 a day per 50 videos.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

from . import files
from .check import unavailable

API = 'https://www.googleapis.com/youtube/v3/videos'


def fetch(ids, key):
    out = {}
    for i in range(0, len(ids), 50):
        q = urllib.parse.urlencode({'part': 'snippet,statistics,contentDetails,status', 'id': ','.join(ids[i:i + 50]), 'key': key})
        req = urllib.request.Request(f'{API}?{q}', headers={'Referer': 'https://ratsuns.github.io/ava-bike-finder/'})
        try:
            reply = json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            raise SystemExit(f'YouTube refused the request ({e.code}): {e.read().decode()[:300]}')
        if 'items' not in reply: raise SystemExit(f'YouTube sent no video list: {str(reply)[:300]}')
        for v in reply['items']:
            s = v['snippet']
            out[v['id']] = {'t': s['title'], 'c': s['channelTitle'], 'd': s['publishedAt'],
                            'vw': int(v.get('statistics', {}).get('viewCount', 0)), 'du': v['contentDetails'].get('duration'),
                            'em': 1 if v['status'].get('embeddable') else 0, 'pv': v['status'].get('privacyStatus'),
                            'lv': s.get('liveBroadcastContent'), 'la': s.get('defaultAudioLanguage') or s.get('defaultLanguage')}
    return out


def main():
    key = os.environ.get('YT_API_KEY')
    if not key: raise SystemExit('YT_API_KEY is not set')
    entries = files.load_csv()
    ids = sorted({i for v in entries.values() for i in v})
    got = fetch(ids, key)
    if len(got) < 0.9 * len(ids):   # YouTube removing a few videos is normal; most of them at once means a problem on its side
        raise SystemExit(f'YouTube returned only {len(got)} of {len(ids)} videos; keeping the old data')
    meta = {i: got.get(i, {'gone': True}) for i in ids}
    files.save_meta(meta)
    print(len(got), 'of', len(ids), 'videos found on YouTube')
    for bike, vids in entries.items():
        for i in [i for i in vids if unavailable(meta[i])]:
            vids.remove(i); print('dropped', bike, i, '-', unavailable(meta[i]))
    files.save_csv(entries)


if __name__ == '__main__':
    sys.exit(main())
