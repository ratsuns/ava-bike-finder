// The analytics events test: what the site reports to Vercel Analytics when people use it.
//   node tests/events_test.js <site url>
// Runs the real pages. Vercel's script isn't served here, so the page's own va() stub keeps every call in
// window.vaq, and the test reads that queue: no mocks. Each test names the break it catches.
const {chromium}=require('playwright');
const URL0=process.argv[2]||'http://localhost:8765/';
const HOST=new URL(URL0).host;

// every call the page made to va('event', ...), oldest first
const events=p=>p.evaluate(()=>(window.vaq||[]).map(a=>[...a]).filter(a=>a[0]==='event').map(a=>a[1]));
const fail=(msg)=>{throw new Error(msg)};
const same=(got,want,what)=>{const g=JSON.stringify(got),w=JSON.stringify(want);if(g!==w)fail(`${what}\n      want ${w}\n      got  ${g}`)};

// a bike and one of its shops that has a phone, email, website and address, read from the site's own data
const pickBikeWithFullShop=p=>p.evaluate(()=>{const S=window.AVA_S;
 for(let i=0;i<B.length;i++)for(const x of B[i].shops||[]){const s=S[x];
  if(s&&s.phone&&s.email&&s.url&&s.address)return {i,bike:B[i].brand+' '+B[i].model,shop:s.name}}
 return null});

const tests=[
 ['opening a bike from its card sends one Bike details event naming that bike', async p=>{
  // breaks if: the event is missing, sent twice, or names another bike
  const card=p.locator('article.c').first();
  const want=await card.evaluate(e=>{const b=B[+e.dataset.b];return {bike:b.brand+' '+b.model,brand:b.brand}});
  await card.locator('button.more').click();await p.waitForFunction(()=>BIKE.open);   // "See details" covers the card, as for people
  same(await events(p),[{name:'Bike details',data:want}],'events after opening one bike');
 }],
 ['each way to contact a shop from a bike counts the shop and the contact type, and which bike led there', async p=>{
  // breaks if: a link type is labelled wrong, the bike is missing, or one tap is counted more or less than once
  const t=await pickBikeWithFullShop(p);if(!t)fail('no bike has a shop with phone, email, website and address');
  await p.evaluate(i=>openBike(i),t.i);await p.waitForFunction(()=>BIKE.open);
  const li=p.locator('#bike .bmshop').filter({has:p.locator('b',{hasText:t.shop})}).first();
  for(const [sel,action] of [['a.maplink.tel','Call'],['a.maplink.mail','Email'],['a.web','Website'],['a.maplink:not(.tel):not(.mail)','Map'],['a.slogo','Website']]){
   await p.evaluate(()=>{window.vaq=[]});
   await li.locator(sel).click();
   same(await events(p),[{name:'Shop contact',data:{shop:t.shop,action}},{name:'Bike to shop',data:{bike:t.bike,shop:t.shop+' · '+action}}],`events after tapping ${sel}`);
  }
 }],
 ['a shop with only a contact form counts as Email when its form is opened', async p=>{
  // breaks if: the contact-form link is counted as Website (it opens the shop's site, but the visitor wants to write to them)
  await p.goto(URL0+'browse-vendors/');await p.waitForSelector('.shop b');
  const card=p.locator('.shop').filter({has:p.locator('a.maplink.mail:not([href^="mailto:"])')}).first();
  if(!await card.count())fail('no shop with only a contact form on the vendors page');
  const shop=(await card.locator('b').first().textContent()).trim();
  await p.evaluate(()=>{window.vaq=[]});await card.locator('a.maplink.mail').click();
  same(await events(p),[{name:'Shop contact',data:{shop,action:'Email'}}],'events after opening a contact form');
 }],
 ['a shop tap on the vendors page counts the contact, with no bike', async p=>{
  // breaks if: vendor-page taps aren't counted, or a bike leaks into them
  await p.goto(URL0+'browse-vendors/');await p.waitForSelector('.shop b');
  const card=p.locator('.shop').filter({has:p.locator('a.maplink.tel')}).first();
  const shop=(await card.locator('b').first().textContent()).trim();
  await p.evaluate(()=>{window.vaq=[]});await card.locator('a.maplink.tel').click();
  same(await events(p),[{name:'Shop contact',data:{shop,action:'Call'}}],'events after calling from the vendors page');
 }],
 ['Directions on a map shop card counts as Directions', async p=>{
  // breaks if: the map's Directions button is counted as Map or Website, or not counted
  await p.goto(URL0+'browse-vendors/');await p.waitForFunction(()=>document.querySelector('.mcard a.mcbtn.pri'),null,{timeout:15000});
  const card=p.locator('.mcard').filter({has:p.locator('a.mcbtn.pri')}).first();
  const shop=(await card.locator('b').first().textContent()).trim();
  await p.evaluate(()=>{window.vaq=[]});await card.locator('a.mcbtn.pri').dispatchEvent('click');
  same(await events(p),[{name:'Shop contact',data:{shop,action:'Directions'}}],'events after Directions');
 }],
 ['a search is counted once, after the visitor stops typing', async p=>{
  // breaks if: every keystroke is sent, nothing is sent, or the query isn't what was typed
  await p.evaluate(()=>qOpen());await p.locator('#cq').pressSequentially('Lectric',{delay:80});
  await p.waitForTimeout(500);same(await events(p),[],'events while still typing (half a second after the last key)');
  await p.waitForTimeout(1500);same(await events(p),[{name:'Search',data:{query:'lectric'}}],'events after a pause');
 }],
 ['a one-letter search is not counted', async p=>{
  // breaks if: the 2-letter minimum is dropped
  await p.evaluate(()=>qOpen());await p.locator('#cq').pressSequentially('x');await p.waitForTimeout(2000);
  same(await events(p),[],'events after typing one letter');
 }],
 ['the same search twice in a row is counted once', async p=>{
  // breaks if: repeats aren't filtered out
  await p.evaluate(()=>qOpen());const q=p.locator('#cq');
  await q.pressSequentially('rad',{delay:60});await p.waitForTimeout(2000);
  await q.press('End');await q.pressSequentially('x');await q.press('Backspace');await p.waitForTimeout(2000);
  same(await events(p),[{name:'Search',data:{query:'rad'}}],'events after searching "rad" twice');
 }],
 ['each page loads each Vercel script once', async p=>{
  // breaks if: a tracking script is added twice (each visit would count twice) or dropped
  for(const path of ['','browse-vendors/']){const seen=[];
   const h=r=>{const u=new URL(r.url());if(u.pathname.startsWith('/_vercel/'))seen.push(u.pathname)};p.on('request',h);
   await p.goto(URL0+path);await p.waitForLoadState('load');await p.waitForTimeout(300);p.off('request',h);
   same(seen.sort(),['/_vercel/insights/script.js','/_vercel/speed-insights/script.js'],`Vercel scripts loaded by /${path}`);
  }
 }],
];

(async()=>{const br=await chromium.launch();let bad=0;
 for(const [vname,vp,mob] of [['desktop',{width:1366,height:900},false],['phone',{width:390,height:844},true]]){
  for(const [name,fn] of tests){
   const ctx=await br.newContext({viewport:vp,hasTouch:mob,isMobile:mob});
   await ctx.route(u=>u.host!==HOST,r=>r.abort());                  // shop sites, maps and videos: never leave the test
   await ctx.route(/\/_vercel\//,r=>r.fulfill({status:404,body:''}));// keep the page's own va() queue in place
   const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
   await p.goto(URL0);await p.waitForFunction(()=>typeof VIDS!=='undefined'&&VIDS,null,{timeout:20000});
   try{await fn(p);if(errs.length)fail('page errors: '+errs.slice(0,2).join(' | '));console.log(`PASS ${vname}: ${name}`)}
   catch(e){bad++;console.log(`FAIL ${vname}: ${name}\n      ${e.message.split('\n').join('\n      ')}`)}
   await ctx.close()}
 }
 await br.close();console.log(bad?`${bad} event test(s) failed`:'all event tests pass');process.exit(bad?1:0)})();
