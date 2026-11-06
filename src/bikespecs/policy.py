"""Chris's answers to the spec check (Nov 6, 2026). apply.py follows these; rules.py decides what the sources back.

  1. A spec only the maker states: show the maker's number.
  2. A spec no source states: keep the site's number (it stays listed as unverified in spec_changes.json).
     19 specs a second search found a different number for: keep the site's number (verify/spec_keep_site.json).
  3. Maker and another site disagree: show the maker's number.
  4. Maker + another site agree on a different number than the site: change it.  5. Site blank, sources give it: add it.
  6. Top speed: the highest assisted speed the bike can reach (a bike that ships at 20 mph and unlocks to 28 shows 28).
     Class stays the class it ships in.
  7. Price: the maker's regular price (Tern's own US store for Tern bikes that its main site shows only on sale).
  7a. Price never goes up: when the site's price is lower than the price the sources give, the site's price stays
      (Chris, Nov 6: "use the cheaper prices"; Lectric's crossed-out prices, for one, are higher than what people pay).
  8. ERideHero counts as an independent source (nothing to do: every other site already counts).
"""
import json, os

from . import evidence

SHOW_MAKER_ONLY = True
KEEP_UNBACKED = True
SPEED = 'highest'
PRICE_NEVER_UP = True
KEEP_SITE = {(b, f) for b, f, *_ in json.load(open(os.path.join(evidence.SRC, 'verify', 'spec_keep_site.json')))}
PRICE = {'Lectric|XPedition 2.0': 1399}          # its crossed-out $1,804 is a Black Friday "was" price; $1,399 is the regular price
REMOVE = {'Pedego|Element Platinum Edition',     # discontinued, and not on Chris's rebate list
          'Serfas|Atlas'}                        # no source anywhere; the maker's page is gone
RENAME = {'Lectric|Xpeak': 'XPeak 2.0', 'Lectric|XPedition': 'XPedition 2.0'}   # replaced by the newer model
DISCONTINUED = {'Macfox|X19', 'Aventon|Sinch 2.5'}
STILL_SOLD = {'BMC|AMP 257 AL Speed One', 'Radio Flyer|Flyer Via', 'Retrospec|Beaumont Rev 2 City', 'Retrospec|Judd Rev Folding',
              'Senada|Osprey V2', 'Senada|Gladiator', 'Senada|Austin V2', 'Senada|Moto Cargo'}
