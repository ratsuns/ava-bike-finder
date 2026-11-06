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
DECIDE = [   # (field, sources, state, shown?)
    ('range', [dict(kind='maker', value='68', url=M, quote='68'), dict(kind='review', value='68', url=N, quote='68')], 'confirmed', True),
    ('tq', [dict(kind='maker', value=75, url=M, quote='75')], 'maker_only', False),
    ('tq', [dict(kind='maker', value=75, url=M, quote='75'), dict(kind='review', value=65, url=R, quote='65')], 'conflict', True),
    ('tq', [dict(kind='review', value=65, url=R, quote='65'), dict(kind='retailer', value=65, url=N, quote='65')], 'confirmed_independent', True),
    ('tq', [dict(kind='maker', value=None, url=M)], 'not_published', False),
    ('tq', [dict(kind='maker', value=75, url=M, quote='75'), dict(kind='review', value=75, url=M + '/other', quote='75')], 'maker_only', False),  # same site twice
    ('price', [dict(kind='maker', value=1499, url=M, quote='1499')], 'maker_only', True),
    ('wt', [dict(kind='maker', value=60, url=M, quote='60 lb'), dict(kind='review', value=60, url=N, quote='weighs a lot')], 'maker_only', False),  # words don't back it
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
