# Source

Everything the live site is built from.

- `build2.py` - builds the whole site: from here, `SITE_DIR=.. python3 build2.py` writes it into the repo root and
  removes old photos, share images and data files nothing uses any more. It first runs the spec and video title tests
  and stops if either fails. Needs Python 3 with Pillow and wordfreq 3.1.1 (`pip install Pillow wordfreq==3.1.1`), and Node with Playwright (it re-makes the shop directory's
  share card when that page changes).
- `verify/cards.json` - the bike list, one entry per bike, read and written only through `bikedata.py` (which
  describes the fields). Each bike has a fixed `id`, its type (sets the rebate), shops, specs, price, main photo and
  colors (each with its color family). Photos are `verify/cardphotos/<name>.webp`.
- `shops.json` - every shop the bikes list, keyed by the name the bike list uses: address, phone, hours, map location,
  website, and `logo` (a file in `verify/shoplogos/`). Castro Valley Cyclery has no website link on purpose: its site's
  security certificate has expired. The build stops if a bike lists a shop that isn't here.
- `site.json` - site facts: address, name, theme colors, rebate amounts per bike type, status labels and the FAQ
  (`{Cargo}`, `{Standard_income}`, `{gear}` and so on are filled in with the amounts). The pages get them as
  `window.AVA_SITE` from the data file.
- `site_tpl.html` - the home page template (layout, styles, scripts).
- `shops_tpl.html` - the shop directory template (browse-vendors/: every shop as a card, next to a map).
- `shared/` - what both pages use, put into each page by `build2.py`: `page.css` (the colour, type, motion, nav-height and
  stacking tokens, light and dark themes, the top nav and phone menu, the E-bike guide and Rebate info panels, shop cards,
  the dim layer), `page.js` (windows, phone menu, theme toggle, the breakpoints the scripts use), `nav.html`, `info.html` (the
  two info panels), `shop.js` (shop card markup and order) and `scrollbar.html`. The CSS breakpoints (760px phones and small
  tablets, 600px phones) are written out in each media query, since media queries can't use variables; scripts read them from
  `BP` in `page.js`.
- `bikespecs/` - checks each bike's specs against the maker and other sites and writes them into the bike list
  (`python3 -m bikespecs.apply`); Chris's decisions are in `bikespecs/DECISIONS.md` and `policy.py`.
- `videos/`, `videos.csv` - the video reviews: `videos.csv` is the list, `videos/` checks and publishes it.
- `tests/` - `site_test.js` (phone/desktop, light/dark) and `snapshot.js` + `compare.py` (before/after comparison
  of a built site), served with `serve.js`.
- `verify/` - photos, shop logos, the hero video, the data files `bikespecs/` and `videos/` keep, and `seo/` (share images, icons, the vendor share card maker,
  and `lastmod.json`, the day each page's content last changed).
