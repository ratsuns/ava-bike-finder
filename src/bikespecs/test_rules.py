"""Real source wording for how sources are read (rules.supports), and what the site shows (policy.shown,
policy.discontinued) for each of Chris's answers. Run from src/:  python3 -m bikespecs.test_rules"""
from . import policy
from .rules import shown_range, supports

SUPPORTS = [   # (field, value, the source's words, backed?)
    ('wh', 608, '36V 16.9Ah', True), ('wh', 540, 'Battery size 540Wh', True), ('wh', 520, 'Battery size 540Wh', False),
    ('range', '68', 'Pedal Assist Range 68 Miles', True), ('range', '15–30', '15 (throttle) / 15-30 miles (PAS)', True),
    ('range', '50', 'up to 80 km', True), ('range', '45 (throttle) / 68 (PAS)', 'Pedal Assist Range 68 Miles', True), ('wt', 75, '64.5 lb w/o battery + 10.5 lb battery', True), ('wt', 56, '25.4 kg', True),
    ('spd', 28, 'up to 45 km/h', True), ('cls', 2, 'Class 1/2/3 e-bike', True), ('cls', 3, 'Class 2', False),
    ('price', 1299, '$1,299.00', True), ('motor', '750W rear hub (1,310W peak)', '750W motor, 1310W peak', True),
    ('height', '5\'0"-6\'3"', 'Rider height 5’0” – 6’3”', True), ('load', 440, '440 lbs max load', True),
    ('load', 400, 'MAX GROSS WEIGHT 440LB/200KG', False), ('cls', 2, 'Class ⟶ 1/2/3', True),
    ('motor', 'Bosch Active Line Plus', 'Motor ⟶ Active Line Plus | Bosch', True), ('motor', 'Bosch Cargo Line', 'Bosch Performance Line', False),
    ('height', '5\'1"-6\'4"', 'Rider Height | 5 ft. 1 in - 6 ft. 4 in', True), ('height', '5\'1"-6\'4"', 'riders from 5 feet, 1 inch to 6 feet, 4 inches', True),
    ('height', '4\'11"-6\'3"', 'Rider Height: 150cm-190cm', True), ('height', '5\'1"-6\'5"', 'entre 1,55 et 1,95 cm', True),
    ('cls', 2, 'Class II: Throttle Pedal Assist', True), ('cls', 3, 'Class 2 | 3, Max Assist Speed: 20mph (Throttle) | 28 (PA)MPH', True),
    ('cls', 1, 'Ebike Max Speed | 20 mph', True), ('cls', 3, 'Ebike Max Speed | 20 mph', False), ('cls', 1, 'MAXIMUM ASSISTED SPEED | 25 km/h', False),
    ('price', 6999, 'US $6.999', True), ('motor', 'Bosch Gen4 Performance Speed', 'The Gen4 Performance Speed motor', True),
    ('motor', '750W rear hub (1,300W peak)', 'MOTOR PEAK OUTPUT: ⟶ 1300W watts', False), ('fold', 'No', '', False),
    ('motor', 'Shimano EP600', 'Motor ⟶ Shimano EP600', True), ('motor', 'Shimano EP8', 'Shimano EP600', False),
    ('cls', 3, 'as a Class 1, 2, or 3 eBike', True), ('cls', 2, 'a maximum speed of 20 mph when it arrives, but it can be adjusted to the Class 3 maximum of 28 mph', True),
    ('height', '4\'8"-6\'4"', 'Recommended Rider Height 142.0 - 150.0 152.0 - 163.0 183.0 - 193.0', True), ('height', '5\'3"-6\'7"', 'One Size 1.59m - 2.00m', True),
]
M, R, N = 'https://www.velotricbike.com/p', 'https://electricbikereview.com/r', 'https://newatlas.com/n'


def src(kind, value, url, quote=None, **more):
    return dict(kind=kind, value=value, url=url, quote=str(value) if quote is None else quote, **more)


# the tests' own entries in Chris's lists, so they don't depend on what the real lists hold
policy.KEEP_SITE, policy.PRICE = {('kept', 'tq'): 70}, {'priced': 1234}
policy.STILL_SOLD, policy.DISCONTINUED = {'still-sold'}, {'chris-disc'}
SHOWN = [   # (what it checks, bike id, field, the site's value now, sources, what the site shows)
    ('the price never goes up', 'b', 'price', 1299, [src('maker', 1499, M), src('review', 1499, N)], 1299),
    ('a lower price replaces the site\'s', 'b', 'price', 1499, [src('maker', 1299, M)], 1299),
    ("the maker's number wins when another site disagrees", 'b', 'tq', 65, [src('maker', 75, M), src('review', 65, R)], 75),
    ("a number only the maker states is shown", 'b', 'tq', None, [src('maker', 75, M)], 75),
    ('two other sites that agree are enough without the maker', 'b', 'tq', None, [src('review', 65, R), src('retailer', 65, N)], 65),
    ('the same site twice is one source', 'b', 'tq', None, [src('review', 65, R), src('retailer', 65, R + '/other')], None),
    ("a source whose words don't back its number doesn't count", 'b', 'tq', None,
     [src('review', 65, R, 'plenty of torque'), src('retailer', 65, N)], None),
    ("the site's number stays when no source backs one", 'b', 'tq', 80, [src('maker', None, M, '')], 80),
    ('top speed is the highest the bike can reach', 'b', 'spd', 20,
     [src('maker', 20, M, 'Class 2 at 20 mph out of the box, unlocks to 28 mph', max_mph=28)], 28),
    ("a kept site number stays whatever the sources say", 'kept', 'tq', None, [src('maker', 75, M)], 70),
    ("Chris's price wins over the maker's", 'priced', 'price', None, [src('maker', 99999, M)], 1234),
]
DISC = lambda *kv: {'sources': [dict(kind=k, value='discontinued', url=u) for k, u in kv]}
DISCONTINUED = [   # (bike id, status sources, discontinued?)
    ('b', DISC(('maker', M)), True), ('b', DISC(('review', R)), False), ('b', DISC(('review', R), ('retailer', N)), True),
    ('b', DISC(('review', R), ('retailer', R + '/other')), False), ('still-sold', DISC(('maker', M)), False), ('chris-disc', None, True),
]
SHOWN_RANGE = [   # (range as recorded, the one number the card shows: the farthest on pedal assist)
    ('40–95', '95'), ('45 (throttle) / 68 (PAS)', '68'), ('40 (throttle) – 70 (PAS)', '70'), ('up to 85', '85'),
    ('30–75 (pedal assist, by mode); 25–45 throttle', '75'), ('Up to 75 (PAS), 50 (throttle)', '75'),
    ('up to 40 (FAQ: up to 99)', '40'), ('22.5', '22.5'), ('', None),
]
NO_BATTERY = [   # (weight sources, the card's weight, card says "(no battery)"?)
    ([src('maker', 64.5, M, basis='without battery')], 64.5, True), ([src('retailer', 64.5, N, basis='without battery')], 64.5, False),
]


def run():
    bad = [f'supports{t[:3]} should be {t[3]}' for t in SUPPORTS if supports(*t[:3]) != t[3]]
    for what, i, f, now, srcs, want in SHOWN:
        got = policy.shown(f, {'id': i, f: now}, srcs)[0]
        if got != want: bad.append(f'{what}: shows {got!r}, expected {want!r}')
    for i, status, want in DISCONTINUED:
        if policy.discontinued(i, status) != want: bad.append(f'discontinued({i}, {status}) should be {want}')
    bad += [f'shown_range({v!r}) should be {w!r}, got {shown_range(v)!r}' for v, w in SHOWN_RANGE if shown_range(v) != w]
    for srcs, wt, want in NO_BATTERY:
        if policy.no_battery(srcs, wt) != want: bad.append(f'no_battery({srcs[0]["kind"]}, {wt}) should be {want}')
    return bad


if __name__ == '__main__':
    bad = run()
    print('\n'.join(bad) or f'all {len(SUPPORTS) + len(SHOWN) + len(DISCONTINUED) + len(NO_BATTERY) + len(SHOWN_RANGE)} spec rules pass')
    raise SystemExit(1 if bad else 0)
