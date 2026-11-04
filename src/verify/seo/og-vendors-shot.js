// Makes og-vendors.jpg, the share card for browse-vendors/: the real page at 1200x630 (2x), on the share card's grid
// (72px sides like og.jpg, brand mark top-left, no top nav). og-vendors-map.jpg is the real map (OpenFreeMap, OSM Bright)
// at the page's start view for this map size (590x540, zoom 10), captured in a browser.
// Run: node og-vendors-shot.js <site folder> shot   (GEIST=path to Geist-Variable.woff2 from the geist npm package)
// then scale og-vendors.png to 1200x630 and save as og-vendors.jpg
const pw=require('playwright'),http=require('http'),fs=require('fs'),path=require('path');
const T={html:'text/html',js:'text/javascript',css:'text/css',webp:'image/webp',svg:'image/svg+xml',png:'image/png',jpg:'image/jpeg'};
const root=process.argv[2];const s=http.createServer((q,r)=>{const u=decodeURIComponent(q.url.split('?')[0]);const f=path.join(root,u.endsWith('/')?u+'index.html':u);fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end();return}r.writeHead(200,{'content-type':T[f.split('.').pop()]||'application/octet-stream'});r.end(d)})}).listen(9954);
const STYLE=JSON.stringify({version:8,sources:{openmaptiles:{type:'vector',url:'https://tiles.openfreemap.org/planet'}},layers:[{id:'bg',type:'background',paint:{'background-color':'#f8f4f0'}},{id:'w',type:'fill',source:'openmaptiles','source-layer':'water',paint:{'fill-color':'#9cf'}}]});
const TJ=JSON.stringify({tiles:['https://tiles.openfreemap.org/planet/TEST/{z}/{x}/{y}.pbf'],minzoom:0,maxzoom:14});
const ok=(c,m)=>console.log((c?'PASS ':'FAIL ')+m);
// Open Graph card for browse-vendors/: the real page at 1200x630 on the share card's grid (72px sides, brand mark top-left, no top nav)
const W=__dirname,MODE=process.argv[3]||'measure';
const OGCSS='<style id="ogcard">html,body{scrollbar-width:none!important}html::-webkit-scrollbar,body::-webkit-scrollbar{display:none}.topnav,.topbar{visibility:hidden!important}main.wrap.spg{padding-left:72px!important;padding-right:72px!important}.ogbrand{position:absolute;left:72px;top:62px;z-index:50;display:flex;align-items:center;gap:12px;font:600 21px/1 Geist,sans-serif;letter-spacing:-.01em;color:var(--fg,#fff)}*{caret-color:transparent!important}</style>';
(async()=>{const b=await pw.chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const c=await b.newContext({viewport:{width:1200,height:630},deviceScaleFactor:2});
 await c.route(/fonts\.googleapis\.com/,r=>r.fulfill({contentType:'text/css',body:"@font-face{font-family:'Geist';font-style:normal;font-weight:400 700;font-display:block;src:url(https://fonts.gstatic.com/geist.woff2) format('woff2')}"}));
 await c.route(/fonts\.gstatic\.com/,r=>r.fulfill({contentType:'font/woff2',body:fs.readFileSync(process.env.GEIST||path.join(W,'Geist-Variable.woff2'))}));
 await c.route(/tiles\.openfreemap/,r=>{const u=r.request().url();if(/\/styles\//.test(u))return r.fulfill({contentType:'application/json',body:STYLE});if(/\/planet$/.test(u))return r.fulfill({contentType:'application/json',body:TJ});return r.fulfill({status:204,body:''})});
 await c.route(/\/__maptop\.jpg/,r=>r.fulfill({contentType:'image/jpeg',body:fs.readFileSync(path.join(W,'og-vendors-map.jpg'))}));
 await c.route(/browse-vendors\/$/,async r=>{const res=await r.fetch();const t=(await res.text()).replace('</head>',OGCSS+'</head>');r.fulfill({response:res,body:t})});
 const p=await c.newPage();await p.addInitScript(()=>{let v;Object.defineProperty(window,'maplibregl',{configurable:true,get(){return v},set(x){v=x;const o=x.Map.prototype.addControl;x.Map.prototype.addControl=function(...q){window.__m=this;return o.apply(this,q)}}})});
 await p.goto('http://localhost:9954/browse-vendors/');await p.waitForFunction(()=>document.getElementById('list').classList.contains('hasmap'),null,{timeout:20000});
 await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(1500);
 const g=await p.evaluate(()=>{const m=document.getElementById('map'),r=m.getBoundingClientRect(),l=document.querySelector('.shop').getBoundingClientRect(),h=document.querySelector('#sph2,.spg h2');const hr=h?h.getBoundingClientRect():null;
  return {w:m.clientWidth,h:m.clientHeight,mapLeft:r.left,mapRight:r.right,mapTop:r.top,cardLeft:l.left,headLeft:hr&&hr.left,c:__m.getCenter(),z:__m.getZoom()}});
 console.log(JSON.stringify(g));
 if(MODE==='shot'){
  await p.evaluate(()=>{const br=document.createElement('div');br.className='ogbrand';br.innerHTML='<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="5.5" cy="17" r="3.5"/><circle cx="18.5" cy="17" r="3.5"/><path d="M5.5 17 9 9h6l3.5 8M12 17l3-8M8 6h3"/></svg>Ava Bike Finder';document.body.append(br);
   const cc=document.querySelector('#map .maplibregl-canvas-container'),im=document.createElement('img');cc.querySelector('canvas').style.opacity='0';im.src='/__maptop.jpg';im.style.cssText='position:absolute;left:0;top:0;width:100%;pointer-events:none';cc.parentNode.insertBefore(im,cc);document.activeElement&&document.activeElement.blur()});
  await p.waitForTimeout(600);await p.screenshot({path:path.join(W,'og-vendors.png')})}
 await b.close();s.close()})();
