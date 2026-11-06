"""Real titles for every matching rule. Run from src/:  python3 -m videos.test_rules   (the build runs it too)

Each case: (brand, model, title, expected) with expected 'model', 'family' or None (not about this bike).
When a rule changes, every case here must still pass; add the title that showed the problem.
"""
from .rules import bikes_from

MODELS = {
    'Cannondale': ['Adventure Neo', 'Adventure Neo Allroad', 'Adventure Neo Allroad EQ', 'Adventure Neo Allroad Speed', 'Tesoro Carbon 1', 'Tesoro Carbon 2',
                   'Tesoro X 1', 'Tesoro X 2'],
    'Electra': ['Cruiser Go!', 'Ponto Go!', 'Ponto Go! S', 'Townie Go!', 'Townie Go! S', 'Townie Go! S EQ'],
    'Emojo': ['Bull', 'Bull Trail', 'Bull Trail Urban Cruiser', 'Bull Urban Cruiser', 'Bison Pro', 'Bison Pro Urban Cruiser'],
    'Eunorau': ['E-FAT-MN', 'E-FAT-STEP'],
    'Fuji': ['E-Traverse 1.1+ (and ST)', 'Sanibel'],
    'Himiway': ['D5 (Zebra)', 'D5 2.0', 'D5 2.0 20"', 'D5 2.0 ST', 'D5 Pro', 'D5 Pro ST', 'D5 ST (Zebra ST)'],
    'Lectric': ['XP4 750 Long-Range', 'XP4 500', 'XP Trike2 750 (Long-Range)'],
    'MOD': ['CarGo 3', 'Easy SideCar', 'Groove Step-Thru 3'],
    'Omnium': ['Cargo V3', 'Min-Max V3'],
    'Pedego': ['Avenue', 'Avenue Core', 'Avenue Pro', 'Cargo', 'Element 2', 'Element Core', 'Interceptor', 'Interceptor Platinum Edition', 'Ridge Rider'],
    'Mokwheel': ['Basalt', 'Scoria'], 'Riese and Muller': ['Load4 60 vario', 'Load4 75 vario'], 'Xtracycle': ['The Hopper', 'Swoop'], 'Izip': ['Simi'], 'Bulls': ['Iconic Evo 1', 'Iconic Evo TR'], 'Bunch': ['The Original 4+'],
    'Salsa': ['Confluence Apex 1', 'Confluence GRX 600 2x', 'Tributary'],
    'Radio Flyer': ['Flyer Via', 'Flyer Via Pro', 'Flyer Loop'],
    'Retrospec': ['Roo Rev XL Cargo Electric Bike', 'Abbot Rev 2 (and Step Through)', 'Boca Rev 2 Electric Tricycle', 'Chatham Rev 3 (and Step Through)',
                  'Chatham Rev+ 2 (and Step Through)', 'Joe Rev 2 BMX Electric Bike', 'Joe Rev BMX Electric Bike (Rev 1)',
                  'Koa Rev 3 (and Step Through)', 'Koa Rev+ 2 (and Step Through)'],
    'Sixthreezero': ['EVRYjourney NEW 500W (Men\'s Sport Hybrid)', 'EVRYjourney Electric Tricycle Rickshaw 750W'],
    'Specialized': ['Globe Haul LT', 'Globe Haul ST', 'Turbo Como 4.0 IGH', 'Turbo Como 5.0 IGH', 'Turbo Vado 2 (4.0)',
                    'Turbo Vado 2 (5.0 IGH)', 'Turbo Vado 3 Evo', 'Turbo Vado 3 X'],
    'Sunseeker': ['E-Delta B1 SX Electric Delta', 'E-Eco Tad B1 SX Electric Tadpole'],
    'Tern': ['Orox R14 (27.5")', 'HSD P5i (Gen 3)', 'GSD P10', 'GSD S10', 'Quick Haul D8', 'Quick Haul Long', 'Quick Haul P9 Sport', 'Vektron P10'],
    'Trek': ['Allant+', 'Charter+ 4S', 'Charter+ 5S Lowstep', 'FX+ 1', 'FX+ 1S', 'FX+ 2', 'FX+ 2S'],
    'Urtopia': ['Carbon Fusion GT', 'Carbon 1'],
    'Yuba': ['Boda Boda', 'Spicy Curry+', 'Spicy Curry V3'],
    'Zooz': ['Ultra Flex G2 Low Bar'],
}

CASES = [
    # names the model
    ('Lectric', 'XP4 750 Long-Range', 'Lectric XP4 750 Review - Still the Best?', 'model'),
    ('Himiway', 'D5 ST (Zebra ST)', 'Himiway Zebra Step-Thru - Good For Seniors and More? - Review and Test Ride', 'model'),
    ('Himiway', 'D5 2.0', 'Himiway D5 2.0 Review', 'model'),
    ('Specialized', 'Turbo Vado 3 Evo', 'Introducing the Vado 3 Evo', 'model'),
    ('Specialized', 'Globe Haul ST', 'Specialized Globe Haul ST review', 'model'),
    ('Trek', 'FX+ 2S', 'Trek FX+ 2S review', 'model'),
    ('Trek', 'FX+ 1', 'Trek&#39;s First Throttle-Equipped E-Bike |Trek FX+1 Review', 'model'),
    ('Sunseeker', 'E-Delta B1 SX Electric Delta', 'Sun Seeker Eco Delta Electric Trike Review - 1.8k', 'model'),
    ('Sunseeker', 'E-Eco Tad B1 SX Electric Tadpole', 'Sun Seeker Eco Tad Electric Trike Review - 1.9k', 'model'),
    ('Omnium', 'Min-Max V3', 'Game-Changer: Omnium Mini Max Cargo Bike Review (2026)', 'model'),
    ('Pedego', 'Avenue Core', 'Pedego Avenue Core vs Avenue Pro', 'model'),
    ('Electra', 'Townie Go! S', 'Smart Tech in a Beach Cruiser? Electra Townie Go! S Review', 'model'),
    ('MOD', 'CarGo 3', 'MOD CarGo 3 review: Texas-tested electric cargo bike!', 'model'),
    # names the brand and the family
    ('Retrospec', 'Abbot Rev 2 (and Step Through)', 'Retrospec Abbott Rev is a Speedy Commuter Ebike', 'family'),
    ('Retrospec', 'Boca Rev 2 Electric Tricycle', 'Retrospec Boca Rev Trike Review - Retro Cool With Comfort For Days', 'family'),
    ('Retrospec', 'Joe Rev 2 BMX Electric Bike', 'FINALLY! An affordable BMX E-Bike | Retrospec Joe Rev Review', 'family'),
    ('Specialized', 'Turbo Como 5.0 IGH', 'Specialized COMO IGH First Touch!', 'family'),
    ('Specialized', 'Turbo Vado 2 (4.0)', 'Specialized Turbo Vado 4.0 Review - $3.6k', 'family'),
    ('Trek', 'Charter+ 4S', 'Charter+ | Trek’s Premium Comfort E-Bike', 'family'),
    ('Fuji', 'E-Traverse 1.1+ (and ST)', 'Fuji E Traverse Classic + Review', 'family'),
    ('Pedego', 'Avenue Core', 'Pedego Avenue Review - $2k', 'family'),
    ('Himiway', 'D5 Pro', 'Chris Tested the Himiway D5 Against His 2000W E-Bikes — Here’s the Truth', 'family'),
    ('Emojo', 'Bull Trail', 'This Electric TRIKE Surprised Me! - Emojo Bull Review', 'family'),
    ('Tern', 'Vektron P10', 'Tern Vektron Gen 4 with Bosch Smart System: Owner Briefing', 'family'),
    ('Sixthreezero', 'EVRYjourney NEW 500W (Men\'s Sport Hybrid)', 'Sixthreezero EVRYjourney Electric Bike — Real World Ride Test', 'family'),
    ('Cannondale', 'Tesoro Carbon 1', 'One Ride Away | Escape to Raus | Cannondale Tesoro', 'family'),
    # not this bike: another number or code after the name
    ('Retrospec', 'Koa Rev 3 (and Step Through)', 'Retrospec Koa Rev 2 ST Review | Stable & Simple', None),
    ('Retrospec', 'Chatham Rev 3 (and Step Through)', 'Retrospec Chatham Rev 2 Review | A Pleasant Surprise For Only $900', None),
    ('Himiway', 'D5 Pro', 'I Tried the Himiway D5 20 Inch… Is It Better Than My Current E-Bike?', None),
    ('Himiway', 'D5 Pro ST', 'CRAZY Range! The Himiway D5 ST 2.0 Goes WAY Farther Than It Should', None),
    ('Specialized', 'Turbo Vado 2 (4.0)', 'Specialized Turbo Vado 5.0 Review - $5.2k', None),
    ('Specialized', 'Turbo Vado 2 (5.0 IGH)', 'Specialized Vado SL 2 Review #ebike #specialized', None),
    ('Yuba', 'Spicy Curry+', 'Yuba Spicy Curry V4 Review: The Ultimate Electric Cargo Bike for Families', None),
    ('Zooz', 'Ultra Flex G2 Low Bar', 'STEALTH ELECTRIC BMX BIKE // ZooZ Ultra Flex 1200', None),
    ('Cannondale', 'Tesoro Carbon 1', 'Cannondale Tesoro Carbon 3 review', None),
    ('Fuji', 'E-Traverse 1.1+ (and ST)', 'NEW Fuji Traverse 1.7 Trekking Bike!', None),
    ('Eunorau', 'E-FAT-MN', 'Unboxing: EUNORAU FAT-HD 2.0', None),
    ('Eunorau', 'E-FAT-STEP', 'Unboxing: EUNORAU FAT-HD 2.0', None),
    ('Eunorau', 'E-FAT-STEP', 'THIS is the ULTIMATE Off-Road Bicycle - Eunorau FAT AWD 2.0 eBike Review', None),
    ('Eunorau', 'E-FAT-STEP', 'UNBOXING: EUNORAU E-FAT-STEP', 'model'),
    ('Fuji', 'E-Traverse 1.1+ (and ST)', '2020 Fuji Traverse 1.1 Dual Sport Hybrid bike  Feature Review & Weight', None),
    # not this bike: another model's word after the name
    ('Retrospec', 'Koa Rev 3 (and Step Through)', 'Retrospec KOA rev+ e-bike review part 2 | Ride along', None),
    ('Retrospec', 'Chatham Rev 3 (and Step Through)', 'Retrospec Chatham Rev + Step Through Review | Simple, Classic Fun!', None),
    # not this bike: names another model
    ('Specialized', 'Globe Haul LT', 'Specialized Globe Haul ST review', None),
    ('Specialized', 'Turbo Vado 3 X', 'Introducing the Vado 3 Evo', None),
    ('Trek', 'FX+ 2', 'Trek FX+ 2S review', None),
    ('Himiway', 'D5 Pro', 'Himiway D5 (Zebra) - Upgraded Torque Sensor Off-Road E-Bike Review | BikeRide.com', None),
    ('Himiway', 'D5 (Zebra)', 'Himiway D5 2.0 Review', None),
    ('Pedego', 'Avenue Core', 'Pedego Avenue Pro review', None),
    ('Cannondale', 'Adventure Neo', 'Cannondale Adventure Neo Allroad Review: Bike Shop Brand at an Affordable Price!?', None),
    ('Cannondale', 'Tesoro X 2', 'Long Distance Cycling on an eBike (Cannondale Neo Tesoro X1)', None),
    ('Emojo', 'Bull Trail', 'EMOJO Bull Trail Urban Cruiser Review – The Ultimate Family E-Trike?', None),
    ('Tern', 'Quick Haul P9 Sport', 'The NEW Tern Quick Haul Long vs GSD - Review, Comparison & Feature Overview', None),
    ('Tern', 'Quick Haul D8', 'Tern Quick Haul Long review', None),
    ('Yuba', 'Spicy Curry+', 'Why does Yuba do it like that? Spicy Curry and new Boda Boda Review', None),
    ('Electra', 'Cruiser Go!', 'Smart Tech in a Beach Cruiser? Electra Townie Go! S Review', None),
    # not this bike: words that only happen to be in the title
    ('Omnium', 'Cargo V3', 'THIS eBike Is INSANE for $999! Dual Motor, 60V, Full Suspension! PUJH PU3 PRO', None),
    ('Omnium', 'Cargo V3', 'Electric Cargo Bike (Omnium) carries folded Brompton on 6.9 km ride', None),
    ('MOD', 'CarGo 3', 'MOD Groove SideCar 3 – The Ultimate Step-Thru Beach Cruiser with a Sidecar', None),
    ('Pedego', 'Cargo', 'Pedego Stretch | Electric Cargo Bike | Pedego Electric Bikes', None),
    ('Cannondale', 'Adventure Neo', 'Cannondale Waves: Scottish Highland Adventure', None),
    ('Radio Flyer', 'Flyer Via', 'Radio Flyer SmarTrike Review from a 2-Year Old! #toyreview #radioflyer', None),
    ('Himiway', 'D5 ST (Zebra ST)', 'So You Think You Want an E-Bike? Watch This 1st - Himiway D5 2.0 20 | RV Travel', None),
    ('Urtopia', 'Carbon Fusion GT', 'The New Urtopia Joy Carbon Ebike is Lightweight, Compact, and Strong', None),
    ('Retrospec', 'Joe Rev BMX Electric Bike (Rev 1)', 'Retrospec Rev 1 helmet', None),
    # a bike listed without a model number: a numbered review is its newer version; after the whole name a number is a trim
    ('Mokwheel', 'Basalt', 'Is The Mokwheel Basalt 2.0 Worth It?', 'model'),
    ('Pedego', 'Ridge Rider', 'Is This the Ultimate SUV E-Bike? Pedego Ridge Rider 2 Review', 'model'),
    ('Trek', 'Allant+', 'Trek FX+7 vs Allant+7 - Best Commuter Hybrid E-bike in 2026?', 'model'),
    ('Specialized', 'Turbo Vado 3 X', 'This E-Bike Is Built for Commuting AND Adventure | Specialized Turbo Vado 3x 5.0 Review', 'model'),
    ('Bulls', 'Iconic Evo TR', 'BULLS ICONIC EVO TR 1 750 Review - $6.3k', 'model'),
    ('Lectric', 'XP4 500', 'Lectric XP4 500W vs 750 | The Real World Range Difference', 'model'),
    ('Lectric', 'XP4 500', 'Lectric XP4 750 Review - Still the Best?', None),
    ('Lectric', 'XP Trike2 750 (Long-Range)', 'MAX POWER - Lectric XP Trike 2.0 750W Motor Review', 'model'),
    ('Pedego', 'Element 2', 'Pedego Element V2 - Walk Around Review and Torture Test!', 'family'),
    ('Tern', 'GSD P10', 'Tern GSD Update | S10 | S00 | P10', 'family'),
    ('Tern', 'Quick Haul D8', 'Tern Quick Haul -- the Lightest Cargo E-Bike that Money Can Buy', 'family'),
    ('Bulls', 'Iconic Evo 1', 'Bulls Iconic 1 750 Diamond', 'family'),
    ('Riese and Muller', 'Load4 60 vario', 'Riese and Muller Load 60 Review', 'family'),
    ('Riese and Muller', 'Load4 60 vario', 'Riese & Müller Load4 60 Review - The ultimate cargo eBike for adventure!', 'family'),
    ('Cannondale', 'Tesoro X 1', 'CANNONDALE TESORO NEO X1  ( 2022 ) E-Bike WALK-AROUND', 'family'),
    ('Tern', 'Orox R14 (27.5")', 'No Trucks Given! Tern Orox (and HSD) MTB Cargo Bike 6 month test.', 'family'),
    # other names, word orders and brand spellings
    ('Pedego', 'Interceptor Platinum Edition', 'Pedego Platinum Interceptor Review - 3.8k', 'model'),
    ('Bunch', 'The Original 4+', 'BUNCHES of Fun! Bunch Bikes FULL Review The Original', 'family'),
    ('Salsa', 'Confluence Apex 1', 'NEW Gravel eBike from Salsa Cycles: Confluence first look', 'family'),
    ('Radio Flyer', 'Flyer Via Pro', 'Flyer Via Pro Review | A Two-Wheeled Wagon For Carrying Kids & Cargo', 'model'),
    ('Radio Flyer', 'Flyer Loop', '🚲 We Fit 2 Kids on This! | Radio Flyer Flyer Loop Review', 'model'),
    ('Retrospec', 'Roo Rev XL Cargo Electric Bike', 'Can One E-Bike Really Carry 4 Kids? | Retrospec Rev Roo XL Review', 'model'),
    ('Cannondale', 'Adventure Neo Allroad EQ', 'Go Electric, Go Anywhere: All-New Adventure Neo Allroad | Cannondale Essentials', 'family'),
    ('Omnium', 'Cargo V3', 'OMNIUM CARGO BIKE in-depth REVIEW', 'family'),
    ('MOD', 'CarGo 3', 'MOD Cargo review: Texas-tested electric cargo bike!', 'family'),
    ('MOD', 'CarGo 3', 'Not all cargo bikes are the same | MOD Bikes Cargo Review #ebike #cargobike', 'family'),
    ('Xtracycle', 'The Hopper', 'Xtracycle Hopper Review: Lower-Cost Premium Cargo E-Bike!', 'model'),
    ('Izip', 'Simi', 'IZIP E3 Simi Review - $1.6k', 'model'),
    # not in English
    ('Cannondale', 'Tesoro Carbon 1', '⚡Cannondale Tesoro Carbon 1 im Test – Das leichte und dynamische E-Bike für den Alltag!', None),
    ('Specialized', 'Turbo Como 4.0 IGH', 'Wir Testen  das E-Bike Specialized Turbo Como 4.0 IGH', None),
    ('Specialized', 'Turbo Como 4.0 IGH', 'Specialized Turbo Como 4.0 IGH – miejskie wydanie komfortu, stylu i mocy!', None),
]


def run():
    bikes = bikes_from([(b, m) for b, ms in MODELS.items() for m in ms])
    failed = []
    for brand, model, title, want in CASES:
        got, why = bikes[f'{brand}|{model}'].match(title)
        if got != want: failed.append(f'{brand} {model} | {title}\n    expected {want}, got {got} {why}')
    return failed


if __name__ == '__main__':
    failed = run()
    print('\n'.join(failed) or f'all {len(CASES)} title rules pass')
    raise SystemExit(1 if failed else 0)
