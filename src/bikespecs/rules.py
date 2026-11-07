"""How a source's words are read, when two sources agree, and what the sources back (decide).
What the site then shows, with Chris's answers, is policy.shown.

What a source's number means (Chris's rules for recording them):
  - price: the maker's regular price (not a sale price)
  - load:  the max load the maker publishes (its payload; when it only gives a total limit, that total, basis "total")
  - weight: with the battery (a maker that lists the frame and the battery separately: the two added up)
  - range: the standard battery with pedal assist (what makers headline); throttle-only figures are not used
"""
import re
from urllib.parse import urlparse

FIELDS = {          # field: (what the site shows, unit)
    'price': ('Price (regular)', 'USD'), 'cls': ('Class', ''), 'spd': ('Top speed', 'mph'), 'tq': ('Torque', 'Nm'),
    'wh': ('Battery', 'Wh'), 'range': ('Range', 'mi'), 'wt': ('Bike weight', 'lb'), 'load': ('Max load', 'lb'),
    'motor': ('Motor (rated watts)', 'W'), 'height': ('Rider height', ''), 'fold': ('Folds', ''),
}
KINDS = ('maker', 'retailer', 'review')
TOLERANCE = {'price': 1, 'spd': 0.6, 'tq': 0, 'wt': 1, 'load': 1}
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


def shown_range(v):
    """the one range number a card shows (Chris): the farthest the bike goes on pedal assist with its stock battery.
    "40–95" -> "95"; "45 (throttle) / 68 (PAS)" -> "68" (throttle-only figures are never used); "up to 85" -> "85" """
    if v in (None, ''): return None
    parts = [x for x in re.split(r'[;,/](?![^()]*\))', str(v)) if x.strip()]
    if len(parts) > 1: parts = [x for x in parts if not re.search(r'(?i)throttle', x)] or parts
    t = re.sub(r'(?i)\d+(?:\.\d+)?\s*\([^)]*throttle[^)]*\)', '', parts[0])   # "45 (throttle)": a throttle-only figure
    ns = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', re.sub(r'\([^)]*\)', '', t))]   # notes in brackets don't count
    return f'{max(ns):g}' if ns else None


def watts(v):
    """the rated watts in a motor description: "750W rear hub (1,310W peak)" -> 750"""
    m = re.search(r'(\d[\d,]*)\s*W(?![a-z])', str(v or ''), re.I)
    return float(m.group(1).replace(',', '')) if m else None


MOTOR_WORDS = {'motor', 'mid', 'drive', 'hub', 'rear', 'front', 'brushless', 'geared', 'peak', 'rated', 'nominal', 'with', 'and', 'the', 'nm', 'system', 'smart',
               'bosch', 'shimano', 'steps', 'yamaha', 'brose', 'mahle', 'bafang', 'giant', 'specialized'}   # brand words: a page often leaves them out


def motor_name(v):
    """a motor's name words: "Bosch Active Line Plus mid-drive (50 Nm)" -> {bosch, active, line, plus}"""
    return {w for w in re.findall(r'[a-z0-9+]{2,}', str(v or '').lower()) if w not in MOTOR_WORDS and not w.isdigit()}


def heights(v):
    """rider heights in inches: 5'0"-6'3" -> [60, 75]; also "5 ft. 1 in", "5 feet, 1 inch", "150cm-190cm", "1,55 et 1,95 m" """
    t = str(v or '').replace('’', "'").replace('′', "'").replace('”', '"').replace('″', '"').replace("'-", "'")
    t = re.sub(r'(\d)\s*(?:ft\.?|feet|foot)\s*,?\s*(?:(\d{1,2})\s*(?:in\.?|inch(?:es)?)\b)?', lambda m: f"{m.group(1)}'{m.group(2) or 0}", t, flags=re.I)
    out = [int(f) * 12 + int(i or 0) for f, i in re.findall(r"(\d)\s*'\s*(\d{1,2})?", t)]
    if not out or re.search(r'\d\s*c?m\b', t, re.I):     # no feet given: the heights are metric (some size tables give no unit)
        out += [round(float(n) / 2.54) for n in re.findall(r'(?<![\d.,])((?:1[3-9]|2[01])\d(?:\.\d)?)(?![\d,]|\.\d)', t)]
        out += [round(float(a + '.' + b) * 100 / 2.54) for a, b in re.findall(r'(?<![\d.,])([12])[.,](\d{2})(?!\d)', t)]
    return out


def class_of(quote):
    """the classes a source's words name: "Class 2", "Class ⟶ 1/2/3", "Class II", "Class 2 | 3" -> {'1','2','3'}"""
    q = re.sub(r'(?i)class\s+(iii|ii|i)\b', lambda m: 'Class ' + str(len(m.group(1))), quote or '')
    return {c for g in re.findall(r'class\W{0,6}([1-3](?:\s*(?:,\s*or|,\s*and|/|,|\||or|and|-)\s*[1-3])*)', q, re.I) for c in re.findall(r'[1-3]', g)}


def mph(quote):
    """top speeds in mph a source states: "20 mph", "28MPH", "up to 20mph" """
    return [float(n) for n in re.findall(r'(\d{2}(?:\.\d)?)\s*(?:-\s*)?mph', quote or '', re.I)]


def close(a, b, field):
    if a is None or b is None: return False
    if field == 'wh': return abs(a - b) <= max(1.0, 0.015 * max(a, b))   # makers round V x Ah
    return abs(a - b) <= TOLERANCE.get(field, 0)


def supports(field, value, quote):
    """the source's exact words contain this value (allowing units: km, kg, V x Ah, frame + battery)"""
    if value in (None, ''): return True
    q = quote or ''
    ns = numbers(q)
    if field == 'fold': return bool(q.strip())
    if field == 'cls':      # no class named: by law Class 1 and 2 top out at 20 mph, Class 3 at 28
        c = str(int(num(value)))
        if c in class_of(q): return True
        sp = mph(q)
        return bool(sp) and ((c in '12' and 20 in sp) or (c == '3' and 28 in sp))
    if field == 'range':
        want = num(shown_range(value))
        return want is not None and any(abs(want - h) <= 0.6 for h in ns + [n * KM for n in ns])
    if field == 'motor':     # its rated watts, or (makers like Bosch publish none) its name
        w = watts(value)
        if w is not None: return any(abs(w - n) < 0.5 for n in ns)
        return bool(motor_name(value)) and motor_name(value) <= motor_name(q)
    if field == 'height':
        want, have = heights(value), heights(q)
        return bool(want) and all(any(abs(w - h) <= 1 for h in have) for w in want)
    v = num(value)
    if v is None: return False
    if field == 'price': ns += [float(n.replace('.', '')) for n in re.findall(r'\$\s?(\d{1,3}(?:\.\d{3})+)(?![\d.])', q)]   # some shops write "US $6.999"
    if any(close(v, n, field) for n in ns): return True
    if field == 'spd' and any(close(v, n * KM, field) for n in ns): return True
    if field in ('wt', 'load') and any(close(v, n * KG, field) for n in ns): return True
    if field == 'wh' and any(close(v, a * b, field) for a in ns for b in ns if a != b and 24 <= a <= 72 and b < 60): return True
    if field == 'wt' and any(close(v, a + b, field) for a in ns for b in ns if a > b): return True
    return False


def agree(field, a, b):
    """two sources give the same value"""
    if a in (None, '') or b in (None, ''): return False
    if field == 'fold': return str(a).strip().lower()[:1] == str(b).strip().lower()[:1]
    if field == 'cls': return int(num(a)) == int(num(b)) if num(a) is not None and num(b) is not None else str(a) == str(b)
    if field == 'range': return shown_range(a) == shown_range(b) != None
    if field == 'motor':
        if watts(a) is not None and watts(b) is not None: return watts(a) == watts(b)
        na, nb = motor_name(a), motor_name(b)
        return bool(na and nb) and (na <= nb or nb <= na)
    if field == 'height': return heights(a)[:1] == heights(b)[:1] and heights(a)[-1:] == heights(b)[-1:]
    return close(num(a), num(b), field)


def same(field, a, b):
    """the site already shows this value (two blanks are the same)"""
    return agree(field, a, b) or (a in (None, '') and b in (None, ''))


def decide(field, sources):
    """what the sources back for one spec: {'state', 'value', 'why'}. A source counts only for what its own words back.
      confirmed              the maker's number, and another site agrees
      conflict               the maker's number; other sites give another
      maker_only             the maker's number; no other site gives one
      confirmed_independent  no maker number; two other sites agree
      not_published          value None: the maker doesn't publish it, and no other site gives it
      unconfirmed            value None: not enough agreeing sources"""
    srcs = [s if supports(field, s.get('value'), s.get('quote')) else dict(s, value=None)
            for s in sources or [] if s.get('kind') in KINDS]
    maker = [s for s in srcs if s['kind'] == 'maker']
    mdom = {domain(s.get('url')) for s in maker}
    others = [s for s in srcs if s['kind'] != 'maker' and domain(s.get('url')) not in mdom]
    stated = [s for s in maker if s.get('value') not in (None, '')]
    if stated:
        v = stated[0]['value']
        backing = {domain(s.get('url')) for s in others if agree(field, v, s.get('value'))}
        if backing: return dict(state='confirmed', value=v, why=f'maker + {len(backing)} more')
        if any(s.get('value') not in (None, '') for s in others):
            return dict(state='conflict', value=v, why='other sources say ' + ', '.join(str(s['value']) for s in others if s.get('value') not in (None, '')))
        return dict(state='maker_only', value=v, why='only the maker states it')
    vals = [s for s in others if s.get('value') not in (None, '')]
    for s in vals:
        doms = {domain(t.get('url')) for t in vals if agree(field, s['value'], t['value'])}
        if len(doms) >= 2: return dict(state='confirmed_independent', value=s['value'], why=f'{len(doms)} independent sources')
    if maker and not vals: return dict(state='not_published', value=None, why='the maker does not publish it')
    return dict(state='unconfirmed', value=None, why='not enough agreeing sources')

