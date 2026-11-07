"""videos.csv -> the page's video file. build2.py calls write(); a video that fails the check stops the build."""
import html

from . import files
from .check import check
from .rules import seconds


def write(site, ids):
    """check every video in videos.csv against its bike (ids: the bikes on the site), then write the page's video file
    into the site folder; returns its file name. Each bike's videos are [id, title, channel, views, date, seconds],
    which the page reads by position."""
    entries, meta = files.load_csv(), files.load_meta()
    problems = check(entries, meta, ids)
    if problems:
        raise SystemExit('Video check failed, nothing was published:\n' + '\n'.join(' | '.join(p) for p in problems))
    return files.write_site(site, {
        bike: [[i, html.unescape(meta[i]['t']), meta[i]['c'], meta[i]['vw'], meta[i]['d'][:10], seconds(meta[i]['du'])] for i in vids]
        for bike, vids in entries.items() if vids})
