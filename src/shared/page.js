/* What both pages do the same way: windows (the E-bike guide, Rebate info and, on the home page, every other window),
   the top nav's phone menu, the light / dark toggle and the visitor's saved location. Runs after the page's markup. */
const $=id=>document.getElementById(id);
const REDUCE=matchMedia('(prefers-reduced-motion: reduce)');
/* the CSS breakpoints, so scripts use the same numbers (media queries can't read CSS variables, so the CSS writes them out too):
   phones and small tablets (bike window as a bottom sheet, phone menu), and phones (search window as a bottom sheet) */
const BP={mobile:'(max-width: 760px)',small:'(max-width: 600px)'};const MOBILE=matchMedia(BP.mobile);
const THEME=__THEME__;
/* keyboard users get focus handed back to what opened a window; touch and mouse users get no leftover outline */
let KBD=false;addEventListener('keydown',e=>{if(e.key==='Tab'||e.key==='Escape'||e.key.startsWith('Arrow')||e.key==='Enter')KBD=true},true);addEventListener('pointerdown',()=>{KBD=false},true);

/* Windows open with show(), not showModal(): showModal makes the browser mark all ~11,000 elements behind it as blocked,
   which took 60-90ms on a mid-range phone. The dim layer, Escape, outside taps and keeping Tab inside the window are handled here instead.
   The page behind stays still while a window or the phone menu is open. */
function lockScroll(){document.documentElement.classList.toggle('locked',!!document.querySelector('dialog[open]:not([data-state="closing"]),#navmenu:popover-open'))}
/* the page can follow the windows: stack(on) runs whenever the dim layer shows or goes, closed(d) once a window has fully closed */
const WINDOW_HOOKS={stack:()=>{},closed:()=>{}};
const DSTACK=[];const SCRIM=document.createElement('div');SCRIM.id='scrim';SCRIM.setAttribute('aria-hidden','true');document.body.append(SCRIM);
const scrim=on=>{SCRIM.classList.toggle('on',on);WINDOW_HOOKS.stack(on)};
SCRIM.addEventListener('click',()=>{const d=DSTACK[DSTACK.length-1];if(d)d.close()});
document.addEventListener('keydown',e=>{const d=DSTACK[DSTACK.length-1];if(!d)return;
 if(e.key==='Escape'){e.preventDefault();d.close();return}
 if(e.key==='Tab'){const f=[...d.querySelectorAll('button,[href],input,select,textarea,summary,[tabindex]:not([tabindex="-1"])')].filter(x=>!x.disabled&&x.getClientRects().length);if(!f.length)return;
  const a=f[0],z=f[f.length-1],c=document.activeElement;
  if(!d.contains(c)){e.preventDefault();a.focus();return}
  if(e.shiftKey&&(c===a||c===d)){e.preventDefault();z.focus()}else if(!e.shiftKey&&c===z){e.preventDefault();a.focus()}}});
/* fn runs once el's transitions have finished (the fallback, longer than any of the pages' motions, covers a browser that never reports them) */
function afterMotion(el,fn){let t=setTimeout(go,400);function go(){if(!t)return;clearTimeout(t);t=0;fn()}Promise.all(el.getAnimations().map(a=>a.finished)).then(go,go)}
/* close() plays the exit animation first, then really closes */
const NCLOSE=HTMLDialogElement.prototype.close;
function animClose(){const d=this;if(!d.open||d.dataset.state==='closing')return;
 scrim(DSTACK.some(x=>x!==d));
 if(d.classList.contains('instant')){NCLOSE.call(d);d.dataset.state='';return}
 d.dataset.state='closing';lockScroll();const ae=document.activeElement;if(d.contains(ae)&&!KBD)ae.blur();
 afterMotion(d,()=>{if(d.dataset.state!=='closing')return;NCLOSE.call(d);d.dataset.state='';d.style.transition='';d.style.transform=''})}
function showDlg(d,opener){if(d.open)return;d._opener=opener||document.activeElement;d.tabIndex=-1;d.setAttribute('aria-modal','true');DSTACK.push(d);d.style.transform='';d.dataset.state='closed';d.show();d.offsetWidth;d.dataset.state='open';scrim(true);d.focus({preventScroll:true});lockScroll();const body=d.querySelector('.dbody,.cbody');if(body)body.scrollTop=0}
document.querySelectorAll('dialog').forEach(d=>{d.close=animClose;
 d.addEventListener('close',()=>{const i=DSTACK.indexOf(d);if(i>=0)DSTACK.splice(i,1);scrim(DSTACK.length>0);lockScroll();WINDOW_HOOKS.closed(d);const o=d._opener;if(KBD&&o&&o.isConnected&&o.focus)o.focus({preventScroll:true});else if(d.contains(document.activeElement)||document.activeElement===d)document.activeElement.blur()});
 d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()});
 d.querySelectorAll('.dclose').forEach(x=>x.onclick=()=>d.close())});

/* the phone menu: a full-screen page under its button; the button turns into a close icon while it's open */
const NAVM=$('navmenu'),MBTN=document.querySelector('.menubtn');
/* the nav's window buttons; in the menu, the menu goes away and its button gets focus back when the window closes */
document.querySelectorAll('[data-open]').forEach(b=>b.addEventListener('click',()=>{const inMenu=NAVM.contains(b);if(inMenu&&NAVM.matches(':popover-open'))NAVM.hidePopover();showDlg($(b.dataset.open),inMenu?MBTN:b)}));
/* the button reads the menu's actual state on every open/close and again after any tap or key, so it can't get stuck
   on the X if a browser (iPhone Safari) skips a close event */
const syncNav=()=>{const o=NAVM.matches(':popover-open');if(MBTN.getAttribute('aria-expanded')!==String(o)){MBTN.setAttribute('aria-expanded',o);MBTN.setAttribute('aria-label',o?'Close menu':'Menu')}lockScroll()};
NAVM.addEventListener('toggle',syncNav);NAVM.addEventListener('beforetoggle',()=>requestAnimationFrame(syncNav));
['click','keyup','pointerup'].forEach(t=>document.addEventListener(t,()=>requestAnimationFrame(syncNav),true));addEventListener('pageshow',syncNav);
/* links to this same page close the menu; a link to another page leaves it open while that page loads (no flash of this page in
   between) and the menu is put away once this page is gone, so coming back with the browser's back button finds it closed */
NAVM.addEventListener('click',e=>{const a=e.target.closest('.nml a'),here=a&&a.getAttribute('aria-current')==='page';if(here)e.preventDefault();
 if((here||e.target.closest('.nml button')||(a&&(a.getAttribute('href')||'').startsWith('#')))&&NAVM.matches(':popover-open'))NAVM.hidePopover()});
addEventListener('pagehide',()=>{if(NAVM.matches(':popover-open'))NAVM.hidePopover()});
MOBILE.addEventListener('change',e=>{if(!e.matches&&NAVM.matches(':popover-open'))NAVM.hidePopover()});

/* mark a scrolling panel when there is more below or above, so it can fade that edge */
(()=>{const els=[...document.querySelectorAll('.bmb,.dbody,.cbody')];
 const upd=el=>{el.classList.toggle('has-more',el.scrollHeight-el.scrollTop-el.clientHeight>4);el.classList.toggle('has-above',el.scrollTop>4)};
 const ro=new ResizeObserver(es=>es.forEach(e=>upd(e.target)));
 els.forEach(el=>{el.addEventListener('scroll',()=>upd(el),{passive:true});ro.observe(el);new MutationObserver(()=>requestAnimationFrame(()=>upd(el))).observe(el,{childList:true,subtree:true,attributes:true,attributeFilter:['open','hidden']})});
 document.querySelectorAll('dialog').forEach(d=>d.addEventListener('toggle',()=>requestAnimationFrame(()=>els.forEach(upd))))})();

/* light / dark toggle: remembered per browser; the page crossfades between themes where view transitions exist */
(()=>{const b=$('themebtn'),H=document.documentElement;
 const cur=()=>H.dataset.theme==='light'?'light':'dark';
 const label=()=>{const t=cur();b.setAttribute('aria-label',t==='dark'?'Switch to light mode':'Switch to dark mode');b.dataset.tip=b.getAttribute('aria-label');b.setAttribute('data-tiphover','')};
 const apply=t=>{H.dataset.theme=t;document.querySelector('meta[name="color-scheme"]').content=t;document.querySelector('meta[name="theme-color"]').content=THEME[t];try{localStorage.setItem('theme',t)}catch(e){}label()};
 label();
 b.addEventListener('click',()=>{const next=cur()==='dark'?'light':'dark';
  if(document.startViewTransition&&!REDUCE.matches){b.style.viewTransitionName='themebtn';const vt=document.startViewTransition(()=>apply(next));vt.finished.finally(()=>{b.style.viewTransitionName=''})}else apply(next)})})();

/* the visitor's location: kept for up to 10 minutes in this tab only (sessionStorage, never sent anywhere), so both pages show it at once */
const NEAR={TTL:600000,
 saved(){try{const v=JSON.parse(sessionStorage.getItem('ava-near')||'null');if(v&&Date.now()-v.t<NEAR.TTL)return v}catch(e){}return null},
 save(u,t){try{sessionStorage.setItem('ava-near',JSON.stringify({lat:u.lat,lng:u.lng,t}))}catch(e){}},
 drop(){try{sessionStorage.removeItem('ava-near')}catch(e){}},
 /* a reading under a minute old is used as it is; an older one shows at once while a fresh one is taken quietly */
 fresh:t=>Date.now()-t<60000,
 /* the position shown only follows a real move, so distances don't jitter */
 moved:(a,b)=>miles(a,b)>0.25,
 ask:(ok,err,o)=>navigator.geolocation.getCurrentPosition(p=>ok({lat:p.coords.latitude,lng:p.coords.longitude}),err,{enableHighAccuracy:false,timeout:15000,maximumAge:60000,...o})};
