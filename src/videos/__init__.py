"""Video reviews for each bike.

videos.csv (one row per bike, up to 3 YouTube links) is the only list the site uses.
  rules.py    how a title is matched to a bike
  check.py    the accuracy check every publish runs
  publish.py  videos.csv -> the site's video file
  refresh.py  YouTube's current data for every listed video (needs YT_API_KEY)
  find.py     suggestions for bikes with fewer than 3 videos (never published directly)
"""
