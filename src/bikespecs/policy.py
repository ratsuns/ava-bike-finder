"""What the site shows for each spec: what the sources back (rules.decide) with Chris's answers (DECISIONS.md).
apply.py writes it into verify/cards.json; check.py and test_rules.py use the same rule.

  - The maker states a number: show the maker's number, whether or not another site agrees.
  - The maker doesn't: show the number two independent sites agree on.
  - Top speed: the highest assisted speed the bike can reach (a source's "max_mph": a bike that ships at 20 mph and
    unlocks to 28 shows 28). Class stays the class it ships in.
  - Price: the maker's regular price (Tern's own US store for Tern bikes that its main site shows only on sale), and it
    never goes up: when the site's price is lower than the sources', the site's price stays (Chris: "use the cheaper
    prices"; Lectric's crossed-out prices, for one, are higher than what people pay).
  - Weight: the card adds "(no battery)" when the maker's figure it shows is without the battery (no_battery).
  - No source backs it: the site's number stays (check.py lists these as "unverified").
  - KEEP_SITE (verify/spec_keep_site.json): a second search found a different number; Chris kept the site's.
  - PRICE: Chris's price for a bike.
A bike is discontinued when the maker says so or two independent sites do, unless Chris's lists below say otherwise.
"""
import json, os

from .rules import agree, decide, domain, num

KEEP_SITE = {(r['id'], r['field']): r['site'] for r in
             json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'verify', 'spec_keep_site.json')))}
PRICE = {'lectric-xpedition-2-0': 1399}          # its crossed-out $1,804 is a Black Friday "was" price; $1,399 is the regular price
DISCONTINUED = {'macfox-x19', 'aventon-sinch-2-5'}
STILL_SOLD = {'bmc-amp-257-al-speed-one', 'radio-flyer-flyer-via', 'retrospec-beaumont-rev-2-city', 'retrospec-judd-rev-folding',
              'senada-osprey-v2', 'senada-gladiator', 'senada-austin-v2', 'senada-moto-cargo',
              # looked up Nov 7, 2026: on sale new from the maker or a shop (verify/discontinued-lookup.csv)
              'scott-sub-cross-eride-30-men-bike-290645', 'scott-silence-eride-20-men-speed-bike-286720',
              'scott-sub-active-eride-20-men-bike-290667', 'serfas-quest', 'giant-roam-e-plus', 'giant-explore-e-plus',
              'hase-kettwiesel-one-shimano-ep6-cargo'}


def shown(field, card, srcs):
    """(the value the site shows for this spec of this bike, why) from the spec's sources in its source file"""
    now = card.get(field)
    if (card['id'], field) in KEEP_SITE: return KEEP_SITE[card['id'], field], 'kept'
    if field == 'price' and card['id'] in PRICE: return PRICE[card['id']], "chris's_price"
    if field == 'spd': srcs = [dict(s, value=s['max_mph']) if s.get('max_mph') else s for s in srcs]
    d = decide(field, srcs)
    v = d['value']
    if field == 'price' and num(now) and num(v) and num(v) > num(now): return now, 'kept_lower_price'
    if v in (None, ''): return (None, d['state']) if now in (None, '') else (now, 'unverified')
    return (int(float(v)) if field == 'cls' else v), d['state']


def no_battery(srcs, wt):
    """the card's weight wt is without the battery: the maker gives that figure with basis 'without battery'"""
    return any(s.get('kind') == 'maker' and s.get('basis') == 'without battery' and agree('wt', s.get('value'), wt) for s in srcs)


def discontinued(bike_id, status):
    """the bike is marked discontinued on the site"""
    if bike_id in STILL_SOLD: return False
    if bike_id in DISCONTINUED: return True
    srcs = (status or {}).get('sources', [])
    if any(s.get('kind') == 'maker' and s.get('value') == 'discontinued' for s in srcs): return True
    return len({domain(s.get('url')) for s in srcs if s.get('kind') != 'maker' and s.get('value') == 'discontinued'}) >= 2
