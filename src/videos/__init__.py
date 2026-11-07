"""Video reviews for each bike.

videos.csv (one row per bike, by the bike's id in verify/cards.json) is the only list the site uses.
  files.py    every file this code reads or writes
  rules.py    how a title is matched to a bike
  check.py    the accuracy check every build runs
  publish.py  videos.csv -> the site's video file (build2.py calls it)
  refresh.py  YouTube's current data for every listed video (needs YT_API_KEY); drops videos YouTube no longer shows
  find.py     suggestions for bikes with room for more videos (never published directly)
"""
