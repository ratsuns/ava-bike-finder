"""How sources are read and when they agree. One place for every rule, used by check.py and apply.py.

Chris's rules:
  - price: the maker's regular price (not a sale price)
  - load:  the max load the maker publishes (its payload; when it only gives a total limit, that total, marked)
  - weight: with the battery (a maker that lists the frame and the battery separately: the two added up)
  - range: the standard battery with pedal assist (what makers headline); throttle-only figures are not used
A spec is shown only when
  - the maker states it and at least one independent source (another site) agrees, or
  - the maker doesn't publish it and two independent sources agree.
When the maker and the other sources disagree, the maker's number is shown and the bike is listed for Chris.
Price is the one exception to "two sources": a maker sets its own price, so the maker's regular price is enough.
"""
import re
from urllib.parse import urlparse

FIELDS = {          # field: (what the site shows, unit)
    'price': ('Price (regular)', 'USD'), 'cls': ('Class', ''), 'spd': ('Top speed', 'mph'), 'tq': ('Torque', 'Nm'),
    'wh': ('Battery', 'Wh'), 'range': ('Range', 'mi'), 'wt': ('Bike weight', 'lb'), 'load': ('Max load', 'lb'),
    'motor': ('Motor (rated watts)', 'W'), 'height': ('Rider height', ''), 'fold': ('Folds', ''),
}
KINDS = ('maker', 'retailer', 'review')
TOLERANCE = {'price': 1, 'spd': 0.6, 'tq': 0, 'wt': 1, 'load': 1}   # absolute; wh is 1.5% (rounding of V x Ah)
KM, KG = 0.621371, 2.20462


def numbers(text):
    """every number in a source's words: "1,299" -> 1299, "36V 10.4Ah" -> 36, 10.4"""
    return [float(n.replace(',', '')) for n in re.findall(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?', text or '')]


def domain(url):
    host = urlparse(url or '').netloc.lower()
    return host[4:] if host.startswith('www.') else host


def num(v):
    try: return float(str(v).replace(',', '').replace('$', ''))
    except (TypeError, ValueError): return None


def range_numbers(v):
    """ "15–30" -> [15, 30], "68" -> [68] """
    return [float(x) for x in re.findall(r'\d+(?:\.\d+)?', str(v or ''))]


def watts(v):
    """the rated watts in a motor description: "750W rear hub (1,310W peak)" -> 750"""
    m = re.search(r'(\d[\d,]*)\s*W(?![a-z])', str(v or ''), re.I)
    return float(m.group(1).replace(',', '')) if m else None


MOTOR_WORDS = {'motor', 'mid', 'drive', 'hub', 'rear', 'front', 'brushless', 'geared', 'peak', 'rated', 'nominal', 'with', 'and', 'the'}


def motor_name(v):
    """a motor's name words: "Bosch Active Line Plus mid-drive (50 Nm)" -> {bosch, active, line, plus}"""
    return {w for w in re.findall(r'[a-z]{3,}', str(v or '').lower()) if w not in MOTOR_WORDS}


def heights(v):
    """rider heights in inches: 5'0"-6'3" -> [60, 75]"""
    t = str(v or '').replace('’', "'").replace('′', "'").replace('”', '"').replace('″', '"')
    return [int(f) * 12 + int(i or 0) for f, i in re.findall(r"(\d)\s*'\s*(\d{1,2})?", t)]


def close(a, b, field):
    if a is None or b is None: return False
    if field == 'wh': return abs(a - b) <= max(1.0, 0.015 * max(a, b))
    return abs(a - b) <= TOLERANCE.get(field, 0)


def supports(field, value, quote):
    """the source's exact words contain this value (allowing units: km, kg, V x Ah, frame + battery)"""
    if value in (None, ''): return True
    q = quote or ''
    ns = numbers(q)
    if field == 'fold': return bool(q.strip())
    if field == 'cls':
        m = re.findall(r'class\W{0,6}([1-3](?:\s*(?:/|,|or|and|-)\s*[1-3])*)', q, re.I)     # "Class 2", "Class ⟶ 1/2/3"
        return any(str(int(num(value))) in re.findall(r'[1-3]', g) for g in m)
    if field == 'range':
        want = range_numbers(value)
        have = ns + [n * KM for n in ns]
        return bool(want) and all(any(abs(w - h) <= 0.6 for h in have) for w in want)
    if field == 'motor':     # its rated watts, or (makers like Bosch publish none) its name
        w = watts(value)
        if w is not None: return any(abs(w - n) < 0.5 for n in ns)
        return bool(motor_name(value)) and motor_name(value) <= motor_name(q)
    if field == 'height':
        want, have = heights(value), heights(q)
        return bool(want) and set(want) <= set(have)
    v = num(value)
    if v is None: return False
    if any(close(v, n, field) for n in ns): return True
    if field == 'spd' and any(close(v, n * KM, field) for n in ns): return True
    if field in ('wt', 'load') and any(close(v, n * KG, field) for n in ns): return True
    if field == 'wh' and any(close(v, a * b, field) for a in ns for b in ns if a != b and 24 <= a <= 72 and b < 60): return True
    if field == 'wt' and any(close(v, a + b, field) for a in ns for b in ns if a > b): return True   # frame + battery
    return False


def agree(field, a, b):
    """two sources give the same value"""
    if a in (None, '') or b in (None, ''): return False
    if field == 'fold': return str(a).strip().lower()[:1] == str(b).strip().lower()[:1]
    if field == 'cls': return int(num(a)) == int(num(b)) if num(a) is not None and num(b) is not None else str(a) == str(b)
    if field == 'range': return range_numbers(a) == range_numbers(b) or max(range_numbers(a) or [0]) == max(range_numbers(b) or [0])
    if field == 'motor':
        if watts(a) is not None and watts(b) is not None: return watts(a) == watts(b)
        na, nb = motor_name(a), motor_name(b)
        return bool(na and nb) and (na <= nb or nb <= na)
    if field == 'height': return heights(a)[:1] == heights(b)[:1] and heights(a)[-1:] == heights(b)[-1:]
    return close(num(a), num(b), field)


def decide(field, sources):
    """what the site shows for one spec, from its sources:
    {'state', 'value', 'show', 'why'}  states: confirmed, confirmed_independent, conflict, maker_only, unconfirmed,
    not_published"""
    srcs = [s for s in sources or [] if s.get('kind') in KINDS]
    maker = [s for s in srcs if s['kind'] == 'maker']
    mdom = {domain(s.get('url')) for s in maker}
    others = [s for s in srcs if s['kind'] != 'maker' and domain(s.get('url')) not in mdom]
    stated = [s for s in maker if s.get('value') not in (None, '')]
    if stated:
        v = stated[0]['value']
        backing = {domain(s.get('url')) for s in others if agree(field, v, s.get('value'))}
        if backing: return dict(state='confirmed', value=v, show=True, why=f'maker + {len(backing)} more')
        if field == 'price': return dict(state='maker_only', value=v, show=True, why="the maker's own price")
        if any(s.get('value') not in (None, '') for s in others):
            return dict(state='conflict', value=v, show=True, why='other sources say ' + ', '.join(str(s['value']) for s in others if s.get('value') not in (None, '')))
        return dict(state='maker_only', value=v, show=False, why='only the maker states it; no second source yet')
    vals = [s for s in others if s.get('value') not in (None, '')]
    for s in vals:
        doms = {domain(t.get('url')) for t in vals if agree(field, s['value'], t['value'])}
        if len(doms) >= 2: return dict(state='confirmed_independent', value=s['value'], show=True, why=f'{len(doms)} independent sources')
    if maker and not vals: return dict(state='not_published', value=None, show=False, why='the maker does not publish it')
    return dict(state='unconfirmed', value=None, show=False, why='not enough agreeing sources')


def discontinued(status):
    """a bike is marked discontinued when the maker says so, or two independent sources do"""
    srcs = (status or {}).get('sources', [])
    if any(s.get('kind') == 'maker' and s.get('value') == 'discontinued' for s in srcs): return True
    return len({domain(s.get('url')) for s in srcs if s.get('kind') != 'maker' and s.get('value') == 'discontinued'}) >= 2
