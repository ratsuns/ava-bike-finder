# Ava Rebate Bike Finder

Every e-bike on the Ava Bike Electric rebate list (Oct 8, 2026), with photos, prices, what you pay after the rebate, specs and East Bay shops.

Live site: https://ratsuns.github.io/ava-bike-finder/

## What's in this folder

- The published site (served by GitHub Pages), all written by the build: `index.html`, `browse-vendors/` (the shop
  directory), `shops.html` (forwards to it), `data-*.js` (bikes and shops), `videos-*.json`, `img/`, icons,
  `og-*.jpg`, `site.webmanifest`, `sitemap.xml`, `llms.txt`, `llms-full.txt`. `vendor/` holds the scrollbar and map libraries.
- `src/`: everything the site is built from (see `src/README.md`).
- `.github/workflows/`: the weekly video refresh and the IndexNow ping.
- `.claude/` and `skills-lock.json`: the Claude skills this project uses.

## Rebuild

Needs Python 3 with Pillow, and Node with Playwright. From `src/`: `SITE_DIR=.. python3 build2.py`
