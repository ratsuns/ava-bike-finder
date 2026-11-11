// The site test: every bike's window shows that bike and its videos, 20 windows really open and close, 4 real taps,
// no console errors; on phone and desktop, light and dark.   node tests/site_test.js <site url>
const {chromium}=require('playwright');
// a third argument runs just one setup (GitHub runs the four side by side): 'phone light', 'phone dark', 'desktop light' or 'desktop dark'
const ONLY=process.argv[3]||'',SETUPS=['phone light','phone dark','desktop light','desktop dark'];
if(ONLY&&!SETUPS.includes(ONLY)){console.log(`FAIL no setup is called "${ONLY}" (have: ${SETUPS.join(', ')})`);process.exit(1)}
(async()=>{const br=await chromium.launch();let fail=0;
for(const [name,vp,scheme] of [['phone light',{width:390,height:844},'light'],['phone dark',{width:390,height:844},'dark'],['desktop light',{width:1366,height:900},'light'],['desktop dark',{width:1366,height:900},'dark']].filter(c=>!ONLY||c[0]===ONLY)){
 const ph=name.startsWith('phone');const p=await br.newPage({viewport:vp,colorScheme:scheme,hasTouch:ph,isMobile:ph});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/ERR_FAILED|net::|Failed to load resource/.test(m.text()))errs.push(m.text())});
 await p.route(/ytimg|youtube|googleapis|gstatic/,r=>r.abort());
 await p.goto(process.argv[2]||'http://localhost:8765/');const t0=Date.now();await p.waitForFunction(()=>VIDS,null,{timeout:15000});const vt=Date.now()-t0;
 const r=await p.evaluate(async()=>{const bad=[];let withV=0;const ks=[...B.keys()].sort(()=>Math.random()-.5);
  // 1) every bike: build its window (what a tap does first) and check every part belongs to that bike
  for(const i of ks){const b=B[i],k=b.id,exp=(VIDS[k]||[]).map(v=>v[0]);
   try{buildBike(i)}catch(e){bad.push(b.name+': '+e.message);continue}
   const s=$('bike-vids'),got=s?[...s.querySelectorAll('.vit')].map(x=>x.dataset.v):null;
   if(!s||s.dataset.k!==k||!$('bike-h').textContent.includes(b.mn))bad.push(b.name+': shows another bike');
   else if(got.join()!==exp.join())bad.push(b.name+': wrong videos');
   else if(!s.querySelector('.vmore[href*="youtube.com/results?search_query="]'))bad.push(b.name+': no YouTube link');
   else if(!exp.length&&!s.querySelector('.vnone'))bad.push(b.name+': no empty message');
   if(got&&got.length)withV++}
  // 2) 20 random bikes: really open and close the window
  const opened=[];for(const i of ks.slice(0,20)){const a=performance.now();buildBike(i);openBike(i);
   while(!BIKE.open&&performance.now()-a<10000)await new Promise(r=>setTimeout(r,2));   // a busy test machine can take seconds
   if(!BIKE.open)bad.push(B[i].name+`: did not open within 10 s`);else if($('bike-vids').dataset.k!==B[i].id)bad.push(B[i].name+': opened showing another bike');
   BIKE.close();const e=performance.now();while(BIKE.open&&performance.now()-e<3000)await new Promise(r=>setTimeout(r,5))}
  return {bikes:B.length,withVideos:withV,problems:bad}});
 // 3) real taps/clicks on 4 cards on screen. The page scrolls smoothly, and on a phone a tap while it is still scrolling
 //    only stops the scroll (for people too), so jump to the card and wait until it sits still for 3 frames before tapping
 let real=0;const tapBad=[];const cards=await p.$$('article.c');
 for(const c of cards.slice(0,4)){const k=await c.evaluate(e=>{e.scrollIntoView({block:'center',behavior:'instant'});return B[+e.dataset.b].id});
  await c.evaluate(e=>new Promise(res=>{let last=null,same=0;const f=()=>{const y=e.getBoundingClientRect().top;same=y===last?same+1:0;last=y;same>=3?res():requestAnimationFrame(f)};f()}));
  const bb=await (await c.$('.ph img')).boundingBox();const x=bb.x+bb.width/2,y=bb.y+bb.height/3;await (ph?p.touchscreen.tap(x,y):p.mouse.click(x,y));
  await p.waitForFunction(()=>BIKE.open,null,{timeout:10000}).catch(()=>{});   // a busy test machine can take seconds
  const got=await p.evaluate(()=>BIKE.open?$('bike-vids').dataset.k:null);
  if(got===k)real++;else tapBad.push(got===null?k+': the tap did not open it':k+': the tap opened '+got);
  await p.keyboard.press('Escape');await p.waitForFunction(()=>!BIKE.open,null,{timeout:10000}).catch(()=>{})}
 const ok=!errs.length&&!r.problems.length&&real===4;if(!ok)fail++;
 console.log((ok?'PASS ':'FAIL ')+name,JSON.stringify({bikesChecked:r.bikes,withVideos:r.withVideos,problems:r.problems.slice(0,5),problemCount:r.problems.length,realTaps:real+'/4',tapProblems:tapBad,videoFileReadyMs:vt}),'console errors:',errs.length,errs.slice(0,2));
 await p.close()}
await br.close();process.exit(fail?1:0)})();
