// Records what the built site shows, so two builds can be compared (see compare.py):
// every bike card's text, every bike window's text, the shops page text, and screenshots of the main views,
// on phone and desktop, in light and dark.   node tests/snapshot.js <site url> <output folder>
const {chromium} = require('playwright');
const fs = require('fs');
const [url, out] = process.argv.slice(2);
fs.mkdirSync(out, {recursive: true});
const CONFIGS = [['phone-light', {width: 390, height: 844}, 'light'], ['phone-dark', {width: 390, height: 844}, 'dark'],
                 ['desktop-light', {width: 1366, height: 900}, 'light'], ['desktop-dark', {width: 1366, height: 900}, 'dark']];
const BIKES = ['Lectric|XP4 500', 'Trek|FX+ 1', 'Tern|GSD P00', 'Urban Arrow|Shorty', 'Velotric|Fold 1 Plus'];

(async () => {
  for (const [name, vp, scheme] of CONFIGS) {
    const br = await chromium.launch();   // one browser per setting: a long-lived one stalls loading pages
    const phone = name.startsWith('phone');
    const p = await br.newPage({viewport: vp, colorScheme: scheme, hasTouch: phone, isMobile: phone, reducedMotion: 'reduce'});
    await p.addInitScript(t => { try { localStorage.setItem('theme', t) } catch (e) {} }, scheme);
    await p.route(/ytimg|youtube|googleapis|gstatic|openfreemap|maptiler|tiles/, r => r.abort());
    await p.goto(url, {waitUntil: 'domcontentloaded'}); await p.waitForFunction(() => typeof VIDS !== 'undefined' && VIDS, null, {timeout: 20000});
    await p.addStyleTag({content: 'video,canvas,.hero-media{visibility:hidden!important}*{caret-color:transparent!important}'});
    await p.waitForTimeout(400);
    const shot = async n => p.screenshot({path: `${out}/${name}-${n}.png`});
    await shot('home');
    const text = await p.evaluate(async () => {
      const bikes = {}, cards = {};
      for (const i of B.keys()) { const b = B[i]; buildBike(i); bikes[b.brand + '|' + b.model] = document.getElementById('bike').innerText; }
      for (let k = 0; k < 40; k++) { const m = document.getElementById('more-btn'); if (!m || m.offsetParent === null) break; m.click(); await new Promise(r => setTimeout(r, 30)); }
      for (const c of document.querySelectorAll('article.c')) { const b = B[+c.dataset.b]; cards[b.brand + '|' + b.model] = c.innerText; }
      return {bikes, cards, page: document.body.innerText.slice(0, 4000)};
    });
    fs.writeFileSync(`${out}/${name}-text.json`, JSON.stringify(text, null, 1));
    await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(200);
    for (const k of BIKES) {
      await p.evaluate(k => { const i = B.findIndex(b => b.brand + '|' + b.model === k); buildBike(i); openBike(i); }, k);
      await p.waitForFunction(() => BIKE.open, null, {timeout: 4000}).catch(() => {}); await p.waitForTimeout(500);
      await shot('bike-' + k.replace(/\W+/g, '-'));
      await p.keyboard.press('Escape'); await p.waitForFunction(() => !BIKE.open, null, {timeout: 4000}).catch(() => {}); await p.waitForTimeout(300);
    }
    for (const d of ['rebate', 'guide']) {
      const ok = await p.evaluate(d => { const a = document.querySelector(`[data-open="${d}"]`); if (a) { a.click(); return true } return false }, d);
      if (ok) { await p.waitForTimeout(600); await shot('dialog-' + d); await p.keyboard.press('Escape'); await p.waitForTimeout(500); }
    }
    await p.close(); await br.close();
    const b2 = await chromium.launch();
    const s = await b2.newPage({viewport: vp, colorScheme: scheme, hasTouch: phone, isMobile: phone, reducedMotion: 'reduce'});
    await s.addInitScript(t => { try { localStorage.setItem('theme', t) } catch (e) {} }, scheme);
    await s.route(/ytimg|youtube|googleapis|gstatic|openfreemap|maptiler|tiles/, r => r.abort());
    for (let t = 0; t < 3; t++) {   // the local test server sometimes stalls on this page; try again
      try { await s.goto(url.replace(/\/?$/, '/') + 'browse-vendors/', {waitUntil: 'domcontentloaded', timeout: 15000}); break; }
      catch (e) { if (t === 2) throw e; }
    }
    await s.waitForTimeout(1500);
    await s.addStyleTag({content: 'canvas,.maplibregl-canvas{visibility:hidden!important}'});
    await s.screenshot({path: `${out}/${name}-shops.png`});
    fs.writeFileSync(`${out}/${name}-shops.txt`, await s.evaluate(() => document.body.innerText));
    await b2.close();
  }
})();
