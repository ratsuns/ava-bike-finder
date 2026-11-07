# Chris's answers (spec check), 2026-11-06
1. Maker-only specs (746): KEEP all (show maker's number). "I want to have the information in there."
2. Not-backed specs (358): LOOK HARDER first, then decide.
3. Disagree (224): show the MAKER's number.
4. Corrections (151): FIX to the number maker + another site agree on.
5. New specs (99): FILL them in.
6. Top speed: show the HIGHEST speed it can reach (e.g. 28 mph), not the ships-at speed. (Class still = how it ships.) -> a source's "max_mph" (in bikes/<id>.json) is used when given.
7. Tern sale-only prices (9 bikes): use the DEALER's regular price.
7a. Price never goes up: when the site's price is lower than the sources' price, the site's price stays ("use the cheaper prices"; Lectric's crossed-out prices, for one, are higher than what people pay).
8. ERideHero: COUNT it as a source.
9. Discontinued (Chris's words):
   - Still available (do NOT mark): BMC AMP 257, Radio Flyer Flyer Via, Retrospec Beaumont Rev 2, Retrospec Judd Rev, Senada Gladiator, Austin V2, Moto Cargo (and Osprey V2: he gave a live source).
   - Discontinued: Macfox X19, Aventon Sinch 2.5.
   - "Replaced by newer (4): these are updated to the newer model, use that" -> needs clarifying which bikes (he also called Beaumont Rev 2 / Judd Rev still available).
   - Pedego Element Platinum: discontinued AND not on his original Excel list.
   - Sources he gave: Radio Flyer Flyer Via specs https://ridereview.com/products/radio-flyer-via ; Senada Osprey https://www.bikeberry.com/products/senada-bikes-500w-48v-osprey-all-terrain-comfort-long-range-step-thru-fat-tire-electric-bike
   - Swap to newer model: Lectric Xpeak -> XPeak 2.0, Lectric XPedition -> XPedition 2.0. Beaumont Rev 2 and Judd Rev stay as they are.
10. Pedego Element Platinum Edition: REMOVE from site (not on his original list).
11. Serfas Atlas: REMOVE from site.
12. Trek Allant+: KEEP, marked discontinued (already marked).
13. Urban Arrow Shorty: KEEP as is.
14. Tern Quick Haul Long duplicate: KEEP BOTH.
15. 17 Trek shop links: FIX (test each first).
2a. Recheck result: 19 specs where sources give a different number -> KEEP the site's number (verify/spec_keep_site.json).
2b. Recheck: 185 specs still unfound -> KEEP the site's number (listed as unverified: `python3 -m bikespecs.check unverified`, 173 on Nov 6).
16. Lectric XPedition 2.0 price: $1,399 (not the $1,804 Black Friday 'was' price).
7 (updated). Tern prices: use TERN's own US store regular price (maker), not the dealer's.
1a. The 91 maker-only specs that differ from the site: show the MAKER's number.
15 (result). Tested all 24 Trek/Electra www links today: every current link loads the right page (200). The earlier Server Error was temporary; removing /us/en_US just redirects back. No link change needed.

Done (Nov 6, 2026): 10 and 11 removed Pedego Element Platinum Edition and Serfas Atlas from the site; 9 renamed Lectric Xpeak to XPeak 2.0 and XPedition to XPedition 2.0. The code that did it is gone; the four old source files (lectric-xpeak, lectric-xpedition, pedego-element-platinum-edition, serfas-atlas) were deleted.

Audit answers (Nov 7, 2026):
- Range: every card shows one number, the farthest the bike goes on pedal assist (Medeo T9 "40–95" shows 95; throttle-only numbers are never shown).
- The 26 bikes hand-marked discontinued with no source: look each up (maker + two other sites) and show Chris the list before changing anything. Trek Allant+ stays marked.
- Class and type tips on the cards keep their own short wording (not the guide's).
- Discontinued lookup (Nov 7, 2026; results in verify/discontinued-lookup.csv): 7 bikes on sale new were unmarked and added
  to STILL_SOLD (Scott Sub Cross eRIDE 30, Scott Silence eRIDE 20 Speed, Scott Sub Active eRIDE 20, Serfas Quest,
  Giant Roam E+, Giant Explore E+, Hase Kettwiesel ONE). The other 18 stay marked discontinued.
