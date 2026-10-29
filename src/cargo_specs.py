# specs gathered earlier (brand/model -> fields), from group A/B/C research and shop pages
CS={
('Lectric','XP 4'):dict(price=1299,price_note='XP4 750 $1,299 at Niles Bicycles; 500W version $999',motor='750W hub (1,310W peak)',torque_nm=85,top_speed_mph=28,battery_wh=840,max_load_lb=330,rider_height="4'10\"–6'3\""),
('Lectric','XPedition'):dict(motor='750W hub (1,310W peak)',torque_nm=85,top_speed_mph=28,battery_wh=1248,max_load_lb=450,rider_height="4'11\"–6'5\""),
('Himiway','C3'):dict(motor='750W hub',torque_nm=86,top_speed_mph=20,battery_wh=960,max_load_lb=440,rider_height="5'2\"–6'3\"",weight_lb=80),
('Aventon','Abound'):dict(motor='750W hub (1,188W peak)',torque_nm=80,top_speed_mph=28,battery_wh=733,max_load_lb=440,rider_height="4'11\"–6'3\""),
('Letrigo','Minivan & Minivan SE'):dict(motor='750W hub (1,200W peak)',torque_nm=90,top_speed_mph=28,battery_wh=672,max_load_lb=450),
('Letrigo','Koda'):dict(motor='750W hub (1,500W peak)',torque_nm=100,top_speed_mph=28,battery_wh=960,max_load_lb=500),
('Letrigo','Workhorse'):dict(motor='500W mid-drive (750W peak)',torque_nm=130,top_speed_mph=28,battery_wh=960,max_load_lb=500,weight_lb=78),
('MOD','CarGo 3'):dict(motor='750W hub',torque_nm=69,top_speed_mph=28,battery_wh=720,max_load_lb=400,rider_height="5'2\"–6'8\""),
('Pedego','Cargo'):dict(motor='750W hub (1,500W peak)',torque_nm=85,top_speed_mph=28,battery_wh=672,max_load_lb=400),
('Radio Flyer','Flyer Loop'):dict(motor='750W (1,200W peak)',torque_nm=87,top_speed_mph=20,battery_wh=687,max_load_lb=440,rider_height="4'11\"–6'3\""),
('Radio Flyer','Flyer Via'):dict(motor='500W',torque_nm=53,top_speed_mph=20,battery_wh=687,max_load_lb=400),
('Radio Flyer','Flyer Via Pro'):dict(motor='750W',torque_nm=85,top_speed_mph=20,battery_wh=687,max_load_lb=400),
('Retrospec','Roo Rev and Roo Rev XL'):dict(motor='750W (1,150W peak)',torque_nm=85,top_speed_mph=20,battery_wh=700,max_load_lb=400,rider_height="5'5\"–6'5\""),
('Revi Bikes','Runabout.2'):dict(motor='750W (1,040W peak)',torque_nm=80,top_speed_mph=28,battery_wh=780,max_load_lb=350,rider_height="4'11\"–6'2\""),
('Segway','Muxi'):dict(motor='750W',torque_nm=85,top_speed_mph=23,battery_wh=717,max_load_lb=418,weight_lb=73),
('Senada','Osprey V2'):dict(motor='500W (700W peak)',torque_nm=62,top_speed_mph=28,battery_wh=960,max_load_lb=350),
('Senada','Gladiator'):dict(motor='750W (900W peak)',torque_nm=75,top_speed_mph=28,battery_wh=720,max_load_lb=350,rider_height="5'2\"–6'2\""),
('Serfas','Atlas'):dict(motor='750W Bafang hub',top_speed_mph=28,battery_wh=672,max_load_lb=440),
('Serfas','Quest'):dict(motor='750W Bafang hub',battery_wh=720,max_load_lb=330),
('Specialized','Haul'):dict(motor='700W hub',top_speed_mph=28,battery_wh=772,max_load_lb=419,rider_height="4'5\"–6'4\""),
('Trek','Fetch+'):dict(motor='Bosch Performance Line Cargo',torque_nm=85,top_speed_mph=20,battery_wh=500,max_load_lb=440,rider_height="4'11\"–6'5\""),
('Velotric','Fold 1 & Fold 1 Plus'):dict(motor='750W (1,100W peak)',torque_nm=75,top_speed_mph=28,battery_wh=608,max_load_lb=450,rider_height="4'9\"–6'5\""),
('Velotric','Go 1'):dict(motor='500W (900W peak)',torque_nm=65,top_speed_mph=25,battery_wh=691,max_load_lb=440,rider_height="5'0\"–6'6\""),
('Velotric','Packer 1'):dict(motor='750W',torque_nm=75,top_speed_mph=25,battery_wh=691,max_load_lb=440,rider_height="5'3\"–6'6\"",weight_lb=75),
}
CS[('Tern','HSD')]=dict(price=4999,price_note='$4,999 at The New Wheel (Oakland)',source='https://newwheel.net/products/tern-hsd-gen-3')
CS[('Tern','Quick Haul')]=dict(price=2999,price_note='$2,999 at The New Wheel; D8 $3,000 at Alameda Bicycle',source='https://newwheel.net/products/tern-quick-haul')
CS[('Tern','Quick Haul Long')]=dict(price=3499,price_note='$3,499 at The New Wheel',source='https://newwheel.net/products/tern-quick-haul-long')
CS[('Tern','GSD')]=dict(price=4999,price_note='$4,999 at The New Wheel',source='https://newwheel.net/products/tern-gsd')
CS[('Tern','Orox')]=dict(price=4999,price_note='$4,999 at The New Wheel',source='https://newwheel.net/products/tern-orox')
CS[('Benno','Boost')]=dict(price=3499,price_note='$3,499 at The New Wheel',source='https://newwheel.net/products/benno-boost-2024')
CS[('Benno','Remidemi')]=dict(price=3499,price_note='$3,499 at The New Wheel',source='https://newwheel.net/products/benno-remidemi')
CS[('Urban Arrow','Breeze')]=dict(price=6999,price_note='$6,999 at The New Wheel',source='https://newwheel.net/products/urban-arrow-breeze')
CS[('Lectric','XP 4')].update(price=999,price_note='XP4 (500W) $999 at Niles Bicycles. XP4 750 is $1,299 (you pay $399): 85 Nm, 28 mph. Specs shown are for the 750.',source='https://niles-bicycles.cloveronline.com/')
CS[('Lectric','XP Trike')]=dict(price=1499,price_note='XP Trike2 $1,499 at Niles Bicycles; XP Trike2 750 $1,799',source='https://niles-bicycles.cloveronline.com/')
PL='https://dealers.pedegoelectricbikes.com/pages/dealers/livermore'
CS[('Pedego','Interceptor (All)')]=dict(price=1949,price_note='Starting at $1,949 at Pedego Livermore',source=PL)
CS[('Pedego','Boomerang')]=dict(price=2495,price_note='Starting at $2,495 at Pedego Livermore',source=PL)
CS[('Pedego','Latch')]=dict(price=2095,price_note='Starting at $2,095 at Pedego Livermore',source=PL)
CS[('Bulls','Evo 2 Speed')]=dict(price=2599,price_note='Clearance $2,599 (MSRP $4,399)')
CS[('Bulls','Evo TR 1')]=dict(price=3299,price_note='Clearance $3,299 (MSRP $5,799)')
CS[('Liv','Thrive E+')]=dict(price=3499.95,price_note='Sale $3,499.95 (MSRP $4,299.99)')
CS[('Senada','Austin V2')]=dict(price=1599,price_note='$1,599 sale at Ebikes2U Fremont (reg $1,799)',source='https://ebikes2u.com/product/senada-austin-v2-900w-peak-city-cargo-dual-seat-folding-ul-2849-certified-fremont/')
CS[('Velotric','Breeze 1')]=dict(price=1799,price_note='$1,799 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-breeze-1-ebike')
CS[('Velotric','Nomad 2')]=dict(price=1849,price_note='$1,849 high-step, $1,999 step-thru at Electric Bike Center',source='https://electricbikeca.com/products/velotric-nomad-2-fat-tire-ebike-high-step')
CS[('Velotric','Tempo')]=dict(price=1499,price_note='$1,499 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-tempo-ebike')
CS[('Velotric','Discover M')]=dict(price=2499,price_note='$2,499 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-discover-m-ebike')
CS[('Velotric','GoMad')]=dict(price=1999,price_note='$1,999 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-gomad-ebike')
CS[('Velotric','Triker 1')]=dict(price=2499,price_note='$2,499 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-triker-electric-folding-tricycle')
CS[('Velotric','Summit 1 & 2')]=dict(price=2099,price_note='Summit 2 $2,099 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-summit-2-ebike')
CS[('Velotric','Discover 2 & 3')]=dict(price=1999,price_note='Discover 3 $1,999 at Electric Bike Center',source='https://electricbikeca.com/products/velotric-discover-3-ebike')
CS[('Aventon','Pace (All)')]=dict(price=1599,price_note='Pace 5 REC $1,599 at Sports Basement; $1,799 at The New Wheel',source='https://shop.sportsbasement.com/products/pace-5-rec')
CS[('Aventon','Level')]=dict(price=1799,price_note='Level 4 REC $1,799 at Sports Basement; Level 4 $1,999 at The New Wheel',source='https://shop.sportsbasement.com/products/level-4-rec-step-over')
CS[('Aventon','Aventure')]=dict(price=1799,price_note='Aventure 3 step-through $1,799 at Sports Basement; $1,999 at The New Wheel',source='https://shop.sportsbasement.com/products/aventure-3-step-through-ebike')
CS[('Aventon','Soltera')]=dict(price=1199,price_note='Soltera 2.5 $1,199; Soltera 3 $1,499 at The New Wheel',source='https://newwheel.net/products/aventon-soltera-lightweight-ebike')
CS[('X-Lab','SP5+')]=dict(price=1899,price_note='$1,899 at Sports Basement',source='https://shop.sportsbasement.com/products/sp5')
for k in [('Giant','Stormguard E+'),('Izip','Simi'),('Sunseeker','E-Eco Tad B1 SX Electric Tadpole'),('Sunseeker','E-Delta B1 SX Electric Delta')]:
    CS[k]=dict(price=None,price_note='No reliable current US price found')
