"""Fetch YouTube's current data for every video in videos.csv into verify/video_meta.json.

    YT_API_KEY=... python3 -m videos.refresh        (run from src/; the GitHub Action does this with the key from its secrets)

Costs 1 unit of the free 10,000 a day per 50 videos. Views, title and availability are updated; a video YouTube no
longer has is marked "gone" so the check names it.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

from .publish import META, load_csv

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
    ids = sorted({i for v in load_csv().values() for i in v})
    got = fetch(ids, key)
    if len(got) < 0.9 * len(ids):   # YouTube removing a few videos is normal; most of them at once means a problem on its side
        raise SystemExit(f'YouTube returned only {len(got)} of {len(ids)} videos; keeping the old data')
    meta = {i: got.get(i, {'gone': True}) for i in ids}
    json.dump(meta, open(META, 'w'), indent=0, ensure_ascii=False, sort_keys=True)
    print(len(got), 'of', len(ids), 'videos found on YouTube')


if __name__ == '__main__':
    sys.exit(main())
