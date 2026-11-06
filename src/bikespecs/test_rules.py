"""Real source wording for every rule in rules.py. Run from src/:  python3 -m bikespecs.test_rules"""
from .rules import decide, supports

SUPPORTS = [   # (field, value, the source's words, backed?)
    ('wh', 608, '36V 16.9Ah', True), ('wh', 540, 'Battery size 540Wh', True), ('wh', 520, 'Battery size 540Wh', False),
    ('range', '68', 'Pedal Assist Range 68 Miles', True), ('range', '15–30', '15 (throttle) / 15-30 miles (PAS)', True),
    ('range', '50', 'up to 80 km', True), ('wt', 75, '64.5 lb w/o battery + 10.5 lb battery', True), ('wt', 56, '25.4 kg', True),
    ('spd', 28, 'up to 45 km/h', True), ('cls', 2, 'Class 1/2/3 e-bike', True), ('cls', 3, 'Class 2', False),
    ('price', 1299, '$1,299.00', True), ('motor', '750W rear hub (1,310W peak)', '750W motor, 1310W peak', True),
    ('height', '5\'0"-6\'3"', 'Rider height 5’0” – 6’3”', True), ('load', 440, '440 lbs max load', True),
    ('load', 400, 'MAX GROSS WEIGHT 440LB/200KG', False), ('cls', 2, 'Class ⟶ 1/2/3', True),
    ('motor', 'Bosch Active Line Plus', 'Motor ⟶ Active Line Plus | Bosch', True), ('motor', 'Bosch Cargo Line', 'Bosch Performance Line', False),
]
M, R, N = 'https://www.velotricbike.com/p', 'https://electricbikereview.com/r', 'https://newatlas.com/n'
DECIDE = [   # (field, sources, state, shown?)
    ('range', [dict(kind='maker', value='68', url=M), dict(kind='review', value='68', url=N)], 'confirmed', True),
    ('tq', [dict(kind='maker', value=75, url=M)], 'maker_only', False),
    ('tq', [dict(kind='maker', value=75, url=M), dict(kind='review', value=65, url=R)], 'conflict', True),
    ('tq', [dict(kind='review', value=65, url=R), dict(kind='retailer', value=65, url=N)], 'confirmed_independent', True),
    ('tq', [dict(kind='maker', value=None, url=M)], 'not_published', False),
    ('tq', [dict(kind='maker', value=75, url=M), dict(kind='review', value=75, url=M + '/other')], 'maker_only', False),  # same site twice
    ('price', [dict(kind='maker', value=1499, url=M)], 'maker_only', True),
]


def run():
    bad = [f'supports{t[:3]} should be {t[3]}' for t in SUPPORTS if supports(*t[:3]) != t[3]]
    for f, s, st, show in DECIDE:
        d = decide(f, s)
        if (d['state'], d['show']) != (st, show): bad.append(f'decide({f}, {s}) -> {d["state"]}/{d["show"]}, expected {st}/{show}')
    return bad


if __name__ == '__main__':
    bad = run()
    print('\n'.join(bad) or f'all {len(SUPPORTS) + len(DECIDE)} spec rules pass')
    raise SystemExit(1 if bad else 0)
