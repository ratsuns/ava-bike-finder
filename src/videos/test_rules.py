"""Real titles for every matching rule. Run from src/:  python3 -m videos.test_rules   (the build runs it too)

Each case: (bike id, title, expected): 'model', 'family', or why the title is not about this bike. The titles are
matched against the real bike list (verify/cards.json), because a title's result depends on the brand's other models.
When a rule changes, every case here must still pass; add the title that showed the problem.
"""
import bikedata
from .rules import bikes_from

NOT_NAMED = 'title does not name this bike'
NOT_ENGLISH = 'title looks like it is not in English'


def other(name):
    return f'title names another model ({name})'


CASES = [
    # names the model
    ('lectric-xp4-750-long-range', 'Lectric XP4 750 Review - Still the Best?', 'model'),
    ('himiway-d5-st-zebra-st', 'Himiway Zebra Step-Thru - Good For Seniors and More? - Review and Test Ride', 'model'),
    ('himiway-d5-2-0', 'Himiway D5 2.0 Review', 'model'),
    ('specialized-turbo-vado-3-evo', 'Introducing the Vado 3 Evo', 'model'),
    ('specialized-globe-haul-st', 'Specialized Globe Haul ST review', 'model'),
    ('trek-fx-plus-2s', 'Trek FX+ 2S review', 'model'),
    ('trek-fx-plus-1', 'Trek&#39;s First Throttle-Equipped E-Bike |Trek FX+1 Review', 'model'),
    ('sunseeker-e-delta-b1-sx-electric-delta', 'Sun Seeker Eco Delta Electric Trike Review - 1.8k', 'model'),
    ('sunseeker-e-eco-tad-b1-sx-electric-tadpole', 'Sun Seeker Eco Tad Electric Trike Review - 1.9k', 'model'),
    ('omnium-min-max-v3', 'Game-Changer: Omnium Mini Max Cargo Bike Review (2026)', 'model'),
    ('pedego-avenue-core', 'Pedego Avenue Core vs Avenue Pro', 'model'),
    ('electra-townie-go-s', 'Smart Tech in a Beach Cruiser? Electra Townie Go! S Review', 'model'),
    ('mod-cargo-3', 'MOD CarGo 3 review: Texas-tested electric cargo bike!', 'model'),
    # names the brand and the family
    ('retrospec-abbot-rev-2-and-step-through', 'Retrospec Abbott Rev is a Speedy Commuter Ebike', 'family'),
    ('retrospec-boca-rev-2-electric-tricycle', 'Retrospec Boca Rev Trike Review - Retro Cool With Comfort For Days', 'family'),
    ('retrospec-joe-rev-2-bmx-electric-bike', 'FINALLY! An affordable BMX E-Bike | Retrospec Joe Rev Review', 'family'),
    ('specialized-turbo-como-5-0-igh', 'Specialized COMO IGH First Touch!', 'family'),
    ('specialized-turbo-vado-2-4-0', 'Specialized Turbo Vado 4.0 Review - $3.6k', 'family'),
    ('trek-charter-plus-4s', 'Charter+ | Trek’s Premium Comfort E-Bike', 'family'),
    ('fuji-e-traverse-1-1-plus-and-st', 'Fuji E Traverse Classic + Review', 'family'),
    ('pedego-avenue-core', 'Pedego Avenue Review - $2k', 'family'),
    ('himiway-d5-pro', 'Chris Tested the Himiway D5 Against His 2000W E-Bikes — Here’s the Truth', 'family'),
    ('emojo-bull-trail', 'This Electric TRIKE Surprised Me! - Emojo Bull Review', 'family'),
    ('tern-vektron-p10', 'Tern Vektron Gen 4 with Bosch Smart System: Owner Briefing', 'family'),
    ('sixthreezero-evryjourney-new-500w-men-s-sport-hybrid', 'Sixthreezero EVRYjourney Electric Bike — Real World Ride Test', 'family'),
    ('cannondale-tesoro-carbon-1', 'One Ride Away | Escape to Raus | Cannondale Tesoro', 'family'),
    # not this bike: another number or code after the name
    ('retrospec-koa-rev-3-and-step-through', 'Retrospec Koa Rev 2 ST Review | Stable & Simple', other('koa rev 2')),
    ('retrospec-chatham-rev-3-and-step-through', 'Retrospec Chatham Rev 2 Review | A Pleasant Surprise For Only $900', other('chatham rev 2')),
    ('himiway-d5-pro', 'I Tried the Himiway D5 20 Inch… Is It Better Than My Current E-Bike?', other('d 5 20')),
    ('himiway-d5-pro-st', 'CRAZY Range! The Himiway D5 ST 2.0 Goes WAY Farther Than It Should', other('d 5 2')),
    ('specialized-turbo-vado-2-4-0', 'Specialized Turbo Vado 5.0 Review - $5.2k', other('vado 5')),
    ('specialized-turbo-vado-2-5-0-igh', 'Specialized Vado SL 2 Review #ebike #specialized', other('vado sl')),
    ('yuba-spicy-curry-plus', 'Yuba Spicy Curry V4 Review: The Ultimate Electric Cargo Bike for Families', other('spicy curry v')),
    ('zooz-ultra-flex-g2-low-bar', 'STEALTH ELECTRIC BMX BIKE // ZooZ Ultra Flex 1200', other('ultra flex 1200')),
    ('cannondale-tesoro-carbon-1', 'Cannondale Tesoro Carbon 3 review', other('tesoro carbon 3')),
    # not this bike: the name without its leading "E-" (the Fuji Traverse and Eunorau FAT-HD are other bikes)
    ('fuji-e-traverse-1-1-plus-and-st', 'NEW Fuji Traverse 1.7 Trekking Bike!', NOT_NAMED),
    ('eunorau-e-fat-mn', 'Unboxing: EUNORAU FAT-HD 2.0', NOT_NAMED),
    ('eunorau-e-fat-step', 'Unboxing: EUNORAU FAT-HD 2.0', NOT_NAMED),
    ('eunorau-e-fat-step', 'THIS is the ULTIMATE Off-Road Bicycle - Eunorau FAT AWD 2.0 eBike Review', NOT_NAMED),
    ('eunorau-e-fat-step', 'UNBOXING: EUNORAU E-FAT-STEP', 'model'),
    ('fuji-e-traverse-1-1-plus-and-st', '2020 Fuji Traverse 1.1 Dual Sport Hybrid bike  Feature Review & Weight', NOT_NAMED),
    # not this bike: another model's word after the name
    ('retrospec-koa-rev-3-and-step-through', 'Retrospec KOA rev+ e-bike review part 2 | Ride along', other('koa rev plus')),
    ('retrospec-chatham-rev-3-and-step-through', 'Retrospec Chatham Rev + Step Through Review | Simple, Classic Fun!', other('chatham rev plus')),
    # not this bike: names another model
    ('specialized-globe-haul-lt', 'Specialized Globe Haul ST review', other('globe haul st')),
    ('specialized-turbo-vado-3-x', 'Introducing the Vado 3 Evo', NOT_NAMED),
    ('trek-fx-plus-2', 'Trek FX+ 2S review', other('fx plus 2 s')),
    ('himiway-d5-pro', 'Himiway D5 (Zebra) - Upgraded Torque Sensor Off-Road E-Bike Review | BikeRide.com', other('zebra')),
    ('himiway-d5-zebra', 'Himiway D5 2.0 Review', other('d 5 2')),
    ('pedego-avenue-core', 'Pedego Avenue Pro review', other('avenue pro')),
    ('cannondale-adventure-neo', 'Cannondale Adventure Neo Allroad Review: Bike Shop Brand at an Affordable Price!?', other('adventure neo allroad')),
    ('cannondale-tesoro-x-2', 'Long Distance Cycling on an eBike (Cannondale Neo Tesoro X1)', other('tesoro x 1')),
    ('emojo-bull-trail', 'EMOJO Bull Trail Urban Cruiser Review – The Ultimate Family E-Trike?', other('bull trail urban')),
    ('tern-quick-haul-p9-sport', 'The NEW Tern Quick Haul Long vs GSD - Review, Comparison & Feature Overview', other('quick haul long')),
    ('tern-quick-haul-d8', 'Tern Quick Haul Long review', other('quick haul long')),
    ('yuba-spicy-curry-plus', 'Why does Yuba do it like that? Spicy Curry and new Boda Boda Review', other('boda boda')),
    ('electra-cruiser-go', 'Smart Tech in a Beach Cruiser? Electra Townie Go! S Review', NOT_NAMED),
    # not this bike: words that only happen to be in the title
    ('omnium-cargo-v3', 'THIS eBike Is INSANE for $999! Dual Motor, 60V, Full Suspension! PUJH PU3 PRO', NOT_NAMED),
    ('omnium-cargo-v3', 'Electric Cargo Bike (Omnium) carries folded Brompton on 6.9 km ride', NOT_NAMED),
    ('mod-cargo-3', 'MOD Groove SideCar 3 – The Ultimate Step-Thru Beach Cruiser with a Sidecar', NOT_NAMED),
    ('pedego-cargo', 'Pedego Stretch | Electric Cargo Bike | Pedego Electric Bikes', NOT_NAMED),
    ('cannondale-adventure-neo', 'Cannondale Waves: Scottish Highland Adventure', NOT_NAMED),
    ('radio-flyer-flyer-via', 'Radio Flyer SmarTrike Review from a 2-Year Old! #toyreview #radioflyer', NOT_NAMED),
    ('himiway-d5-st-zebra-st', 'So You Think You Want an E-Bike? Watch This 1st - Himiway D5 2.0 20 | RV Travel', other('d 5 2')),
    ('urtopia-carbon-fusion-gt', 'The New Urtopia Joy Carbon Ebike is Lightweight, Compact, and Strong', NOT_NAMED),
    ('retrospec-joe-rev-bmx-electric-bike-rev-1', 'Retrospec Rev 1 helmet', NOT_NAMED),
    # a bike listed without a model number: a numbered review is its newer version; after the whole name a number is a trim
    ('mokwheel-basalt', 'Is The Mokwheel Basalt 2.0 Worth It?', 'model'),
    ('pedego-ridge-rider', 'Is This the Ultimate SUV E-Bike? Pedego Ridge Rider 2 Review', 'model'),
    ('trek-allant-plus', 'Trek FX+7 vs Allant+7 - Best Commuter Hybrid E-bike in 2026?', 'model'),
    ('specialized-turbo-vado-3-x', 'This E-Bike Is Built for Commuting AND Adventure | Specialized Turbo Vado 3x 5.0 Review', 'model'),
    ('bulls-iconic-evo-tr', 'BULLS ICONIC EVO TR 1 750 Review - $6.3k', 'model'),
    ('lectric-xp4-500', 'Lectric XP4 500W vs 750 | The Real World Range Difference', 'model'),
    ('lectric-xp4-500', 'Lectric XP4 750 Review - Still the Best?', other('xp 4 750')),
    ('lectric-xp-trike2-750-long-range', 'MAX POWER - Lectric XP Trike 2.0 750W Motor Review', 'model'),
    ('pedego-element-2', 'Pedego Element V2 - Walk Around Review and Torture Test!', 'family'),
    ('tern-gsd-p10', 'Tern GSD Update | S10 | S00 | P10', 'family'),
    ('tern-quick-haul-d8', 'Tern Quick Haul -- the Lightest Cargo E-Bike that Money Can Buy', 'family'),
    ('bulls-iconic-evo-1', 'Bulls Iconic 1 750 Diamond', 'family'),
    ('riese-and-muller-load4-60-vario', 'Riese and Muller Load 60 Review', 'family'),
    ('riese-and-muller-load4-60-vario', 'Riese & Müller Load4 60 Review - The ultimate cargo eBike for adventure!', 'family'),
    ('cannondale-tesoro-x-1', 'CANNONDALE TESORO NEO X1  ( 2022 ) E-Bike WALK-AROUND', 'family'),
    ('tern-orox-r14-27-5', 'No Trucks Given! Tern Orox (and HSD) MTB Cargo Bike 6 month test.', 'family'),
    # other names, word orders and brand spellings
    ('pedego-interceptor-platinum-edition', 'Pedego Platinum Interceptor Review - 3.8k', 'model'),
    ('bunch-the-original-4-plus', 'BUNCHES of Fun! Bunch Bikes FULL Review The Original', 'family'),
    ('salsa-confluence-apex-1', 'NEW Gravel eBike from Salsa Cycles: Confluence first look', 'family'),
    ('radio-flyer-flyer-via-pro', 'Flyer Via Pro Review | A Two-Wheeled Wagon For Carrying Kids & Cargo', 'model'),
    ('radio-flyer-flyer-loop', '🚲 We Fit 2 Kids on This! | Radio Flyer Flyer Loop Review', 'model'),
    ('retrospec-roo-rev-xl-cargo-electric-bike', 'Can One E-Bike Really Carry 4 Kids? | Retrospec Rev Roo XL Review', 'model'),
    ('cannondale-adventure-neo-allroad-eq', 'Go Electric, Go Anywhere: All-New Adventure Neo Allroad | Cannondale Essentials', 'family'),
    ('omnium-cargo-v3', 'OMNIUM CARGO BIKE in-depth REVIEW', 'family'),
    ('mod-cargo-3', 'MOD Cargo review: Texas-tested electric cargo bike!', 'family'),
    ('mod-cargo-3', 'Not all cargo bikes are the same | MOD Bikes Cargo Review #ebike #cargobike', 'family'),
    ('xtracycle-the-hopper', 'Xtracycle Hopper Review: Lower-Cost Premium Cargo E-Bike!', 'model'),
    ('izip-simi', 'IZIP E3 Simi Review - $1.6k', 'model'),
    # not in English
    ('cannondale-tesoro-carbon-1', '⚡Cannondale Tesoro Carbon 1 im Test – Das leichte und dynamische E-Bike für den Alltag!', NOT_ENGLISH),
    ('specialized-turbo-como-4-0-igh', 'Wir Testen  das E-Bike Specialized Turbo Como 4.0 IGH', NOT_ENGLISH),
    ('specialized-turbo-como-4-0-igh', 'Specialized Turbo Como 4.0 IGH – miejskie wydanie komfortu, stylu i mocy!', NOT_ENGLISH),
]


def run():
    bikes = bikes_from(bikedata.load())
    failed = []
    for bike, title, want in CASES:
        if bike not in bikes: failed.append(f'{bike}: not in the bike list any more; move this case to another bike'); continue
        kind, why = bikes[bike].match(title)
        if (kind or why) != want: failed.append(f'{bike} | {title}\n    expected {want}, got {kind or why}')
    return failed


if __name__ == '__main__':
    failed = run()
    print('\n'.join(failed) or f'all {len(CASES)} title rules pass')
    raise SystemExit(1 if failed else 0)
