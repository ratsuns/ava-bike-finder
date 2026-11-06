"""Bike specs, each backed by its sources.

bikes/<bike>.json holds one bike's specs, each with 2-3 sources: the link, the kind of source (maker, retailer,
review) and the source's exact words. Nothing is shown on the site unless the sources back it.
  rules.py     how a source's words are read (units, conversions), when sources agree, and Chris's rules
  evidence.py  reading and writing the per-bike files
  check.py     every spec the site shows must match what its sources back; lists what doesn't
  apply.py     writes the backed values into verify/cards.json, which the build uses

Run from src/:  python3 -m bikespecs.check      python3 -m bikespecs.apply
"""
