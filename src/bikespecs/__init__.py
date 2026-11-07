"""Bike specs and their sources.

bikes/<id>.json holds one bike's specs, each with 2-3 sources: the link, the kind of source (maker, retailer, review)
and the source's exact words.
  evidence.py  the source files' layout, and reading them
  rules.py     how a source's words are read (units, conversions), when sources agree, what the sources back
  policy.py    what the site shows: what the sources back, with Chris's answers (DECISIONS.md)
  apply.py     writes what the site shows into verify/cards.json
  check.py     lists problems: words that don't back a number, bikes without a file, the site out of step with the rule

Run from src/:  python3 -m bikespecs.check      python3 -m bikespecs.apply      python3 -m bikespecs.test_rules
"""
