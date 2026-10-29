# Ava Rebate Bike Finder

Every e-bike on the Ava Bike Electric rebate list (Oct 8, 2026), with photos, prices, what you pay after the rebate, specs and East Bay shops.

Live site: https://ratsuns.github.io/ava-bike-finder/

## What's in this folder

- `index.html`, `img/`, icons, `og-*.jpg`, `site.webmanifest`, `sitemap.xml`: the published site (served by GitHub Pages).
- `src/`: everything the site is built from.
  - `site_tpl.html`: the page design.
  - `build2.py`: combines the design with the data into the site.
  - `shops.json`, `bikes.json`, `res_all.json`, `fill*.json`, `specs/`, `cargo_specs.py`: the bike list, prices, specs and shop addresses.
  - `verify/`: checked photos, photo fixes, the hero video, the share card and icons.
- `PRODUCT.md`: what the product is and who it's for (read by the Impeccable design skill).
- `.claude/` and `skills-lock.json`: the Claude design skills this project uses (Impeccable, Emil Kowalski's animation skills, frontend-design).

## Rebuild

From `src/`: `SITE_DIR=.. python3 build2.py`
