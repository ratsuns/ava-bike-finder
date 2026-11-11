// The site files test: what the published files tell search engines, and where old links are forwarded.
//   node tests/files_test.js <repo folder>
// Reads the built files exactly as they are published. Each test names the break it catches.
const fs=require('fs'),path=require('path'),vm=require('vm');
const ROOT=path.resolve(process.argv[2]||'.');
const read=f=>fs.readFileSync(path.join(ROOT,f),'utf8');
const OFFICIAL=new URL(JSON.parse(read('src/site.json')).url).origin;   // the one address the site lives at
const fail=msg=>{throw new Error(msg)};

// the absolute addresses a page gives search engines and link previews
const pageAddresses=f=>{const h=read(f),out=[];
 for(const m of h.matchAll(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"/g))out.push(['canonical',m[1]]);
 for(const m of h.matchAll(/<meta[^>]+(?:property|name)="(og:url|og:image|og:video|twitter:image)"[^>]+content="([^"]+)"/g))out.push([m[1],m[2]]);
 return out};

const tests=[
 ['robots.txt points search engines to the sitemap on the official address', ()=>{
  // breaks if: robots.txt isn't written, or its Sitemap line points anywhere else
  const t=read('robots.txt'),m=t.match(/^Sitemap:\s*(\S+)\s*$/m);
  if(!m)fail('robots.txt has no Sitemap line:\n'+t);
  if(m[1]!==OFFICIAL+'/sitemap.xml')fail(`Sitemap is ${m[1]}, want ${OFFICIAL}/sitemap.xml`);
  if(!/^User-agent:\s*\*\s*$/m.test(t)||/^Disallow:\s*\/\s*$/m.test(t))fail('robots.txt does not let every search engine in:\n'+t);
 }],
 ['every page in the sitemap is on the official address', ()=>{
  // breaks if: the sitemap lists an old or preview address, or is empty
  const locs=[...read('sitemap.xml').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1]);
  if(!locs.length)fail('sitemap.xml lists no pages');
  const bad=locs.filter(u=>new URL(u).origin!==OFFICIAL);if(bad.length)fail('not on '+OFFICIAL+': '+bad.join(', '));
 }],
 ['each page tells search engines and link previews its official address', ()=>{
  // breaks if: a page's canonical, share link or preview image points at an old or preview address
  for(const f of ['index.html','browse-vendors/index.html']){const a=pageAddresses(f);
   if(!a.some(([k])=>k==='canonical'))fail(f+' has no canonical address');
   const bad=a.filter(([,u])=>new URL(u).origin!==OFFICIAL);if(bad.length)fail(f+': '+bad.map(([k,u])=>k+' = '+u).join(', '))}
 }],
 ['an old link is forwarded to the same page on the new address, keeping what follows it', ()=>{
  // breaks if: the old /ava-bike-finder part isn't dropped, or the ?query or #section is lost
  const cases=[ // old address (path, query, hash) -> where it must land
   ['/ava-bike-finder/','','','https://www.ebikerebatefinder.com/'],
   ['/ava-bike-finder','','','https://www.ebikerebatefinder.com/'],
   ['/ava-bike-finder/index.html','','','https://www.ebikerebatefinder.com/'],
   ['/ava-bike-finder/browse-vendors/','','','https://www.ebikerebatefinder.com/browse-vendors/'],
   ['/ava-bike-finder/','?utm_source=qr','#rebate','https://www.ebikerebatefinder.com/?utm_source=qr#rebate'],
   ['/ava-bike-finder/browse-vendors/','','#map','https://www.ebikerebatefinder.com/browse-vendors/#map']];
  for(const f of ['docs/index.html','docs/404.html']){   // 404.html answers every old link that isn't the front page
   const js=[...read(f).matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');if(!js)fail(f+' has no forwarding script');
   for(const [pathname,search,hash,want] of cases){let got=null;
    vm.runInNewContext(js,{location:{pathname,search,hash,replace:u=>{got=u}}});
    if(got!==want)fail(`${f}: ${pathname}${search}${hash} went to ${got}, want ${want}`)}}
 }],
];

let bad=0;for(const [name,fn] of tests){try{fn();console.log('PASS '+name)}catch(e){bad++;console.log('FAIL '+name+'\n      '+e.message.split('\n').join('\n      '))}}
console.log(bad?`${bad} file test(s) failed`:'all file tests pass');process.exit(bad?1:0);
