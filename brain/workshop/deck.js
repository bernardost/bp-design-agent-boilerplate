/* deck.js — the workshop deck: every board, the corners, the Deck panel, and saving.

   Ported from Far Wall v24, the design of record of AE Kickoff, without the playground canvas,
   the persona photos or the roster. What changed on the way:
     · the boards come from the deck itself (deck.json → S.boards), so a workshop holds any mix
       from brain/workshop/library.json, and an agent can write its own question boards
     · Agile sliders became Personality: a pair of words per row, a dot on seven steps between them
     · the cover's lockup is two names set as text; no mark is drawn
     · the ending downloads notes.md instead of a PDF
     · every change is kept in this browser at once and sent to brain/workshop.py a moment later.
       A dropped connection, a stopped server or a refresh loses nothing; reopening lands on the
       board you were on, with the time spent on each board kept.

   State: S is the deck. Question, row and goal boards keep their content under their own key
   (S.gq, S.brand…); the one-of-a-kind boards use fixed keys (S.team, S.tl, S.pers, S.raci,
   S.traits, S.week, S.steps). */

/* ── state ── */
let S=null,H=[],ROOT=null;
const U={endEx:3,lit:{},pick:null,tmr:{},arm:null,dragged:false,entered:{},qper:'4',psel:0,ptab:0,popen:null,panel:false,col:null,tl:{fresh:true,ghostMs:null,focus:null}};
const PACE={t:{},cur:null,paused:false,last:0};
const html=document.documentElement;
const WID=decodeURIComponent(location.pathname.split('/').filter(Boolean)[1]||'');
const API='/api/workshops/'+encodeURIComponent(WID);

const BD=k=>S.boards.find(b=>b.key===k);
const KIND=k=>(BD(k)||{}).kind;
const NAME=k=>(BD(k)||{}).name||'';
const VIS=()=>S.boards.map(b=>b.key).filter(k=>!S.off[k]);
const ofKind=kind=>S.boards.filter(b=>b.kind===kind).map(b=>b.key);
const FIXED=k=>!!(BD(k)||{}).fixed;

const parts=p=>p.split('.').map(x=>/^\d+$/.test(x)?+x:x);
const get=p=>parts(p).reduce((o,k)=>o==null?o:o[k],S);
const put=(p,v)=>{const k=parts(p),last=k.pop();k.reduce((o,x)=>o[x],S)[last]=v};
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const t=s=>(s||'').trim();
const plural=(n,one,many)=>n===1?one:many;
const and=a=>a.length<2?(a[0]||''):a.slice(0,-1).join(', ')+' and '+a[a.length-1];
const DAYNAMES=['Monday','Tuesday','Wednesday','Thursday','Friday'];
const client=()=>t(S.cover.client)||'the client';
const n2=i=>String(i+1).padStart(2,'0');
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const motionOn=()=>html.dataset.motion!=='none'&&!matchMedia('(prefers-reduced-motion:reduce)').matches;
const cssn=k=>parseFloat(getComputedStyle(html).getPropertyValue(k))||0;
const snap=()=>{H.push({s:JSON.stringify(S),b:null,what:''});if(H.length>60)H.shift()};

/* ── lists: what a new item in each list looks like ── */
function listOf(a){const p=a.split('.'),k=p[0],kind=KIND(k);
  if(p.length===1){if(kind==='team')return()=>({name:'',role:''});if(kind==='steps')return()=>({who:'',what:''});if(kind==='questions')return()=>({q:'',d:'',a:[]})}
  if((k==='week'||k==='week2')&&p.length===2)return()=>({name:'',dur:''});
  if((kind==='questions'||kind==='goals')&&p.length===3&&p[2]==='a')return()=>'';
  return null}
function itemOf(p){const k=p.split('.');for(let n=k.length-1;n>0;n--){if(/^\d+$/.test(k[n])){const a=k.slice(0,n).join('.');if(listOf(a))return {a,i:+k[n],rest:k.slice(n+1).join('.')}}}return null}
const isPrimary=r=>r===''||['name','what','q'].includes(r);
function firstField(a,i){const v=get(a+'.'+i);if(typeof v==='string'||v==null)return a+'.'+i;return a+'.'+i+'.'+['q','what','name'].find(k=>k in v)}

/* ── people: initials in a circle for anyone on Team; anyone else gets the person icon ── */
const PERSON='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4.3"/><path d="M3.4 21.5c.9-4.9 4.4-7.6 8.6-7.6s7.7 2.7 8.6 7.6z"/></svg>';
const team=()=>S.team||[];
function member(name){const n=t(name).toLowerCase();if(!n)return null;const ms=team().filter(m=>t(m.name));
  const full=ms.find(m=>t(m.name).toLowerCase()===n);if(full)return full;
  const first=ms.filter(m=>t(m.name).split(/\s+/)[0].toLowerCase()===n);return first.length===1?first[0]:first.length>1?{name:t(name)}:null}
const initials=n=>{const w=t(n).split(/\s+/);return ((w[0]||'')[0]||'')+(w.length>1?w[w.length-1][0]:'')};
function av(name,m){if(!t(name)||isAll(name))return '';m=m||member(name);
  return `<span class="av" aria-hidden="true">${m?`<b>${esc(initials(m.name).toUpperCase())}</b>`:PERSON}</span>`}
const namesIn=s=>String(s||'').split(/,|\n|\s+and\s+|&|\//).map(t).filter(Boolean);
const avs=s=>namesIn(s).map(n=>av(n)).join('');
const EVERYONE='Everyone';
const isAll=n=>/^(everyone|all|the whole team)$/i.test(t(n));
function people(){const ms=team().map(m=>t(m.name)).filter(Boolean);const first=ms.map(n=>n.split(/\s+/)[0]);
  return ms.map((n,i)=>first.filter(f=>f===first[i]).length>1?n:first[i])}
function names(){const out=people(),seen=new Set(out.map(n=>n.toLowerCase()));
  const add=n=>{n=t(n);if(!n||isAll(n)||member(n)||seen.has(n.toLowerCase()))return;seen.add(n.toLowerCase());out.push(n)};
  (S.raci||[]).forEach(r=>['R','A','C','I'].forEach(k=>namesIn(r[k]).forEach(add)));(S.steps||[]).forEach(x=>add(x.who));
  return [...out,EVERYONE]}

/* ── live figures: counts over stored values only ── */
const answered=q=>(q.a||[]).some(x=>t(x));
const PQ=()=>(BD('pers')||{}).questions||[];
const pdone=p=>p.qs.filter(answered).length;
const colName=c=>String(c).replace('{client}',t(S.cover.client)||'Client');
const LV={
  team:{fig:()=>String(team().filter(m=>t(m.name)).length),cap:()=>plural(team().filter(m=>t(m.name)).length,'person','people')},
  rows:{fig:k=>String(S[k].rows.reduce((n,r)=>n+r.v.filter(v=>!t(v)).length,0)),cap:()=>'left to write'},
  raci:{fig:()=>String(S.raci.reduce((n,r)=>n+['R','A','C','I'].filter(k=>!t(r[k])).length,0)),
    cap:()=>{const r=S.raci[U.lit.raci];return r?`open · ${['R','A','C','I'].filter(x=>!t(r[x])).length} in this row`:'open'},
    note:()=>{const n=S.raci.filter(r=>!t(r.A)).length;return n?`${n} ${plural(n,'role has','roles have')} no one accountable`:''}},
  personas:{note:()=>{const p=S.pers[U.psel];return p?`${pdone(p)} of ${PQ().length} answered`:''}},
  steps:{fig:()=>String(S.steps.filter(s=>!t(s.who)).length),cap:()=>`of ${S.steps.length} ${plural(S.steps.length,'has','have')} no owner`,
    note:()=>{const c={};S.steps.forEach(s=>{if(t(s.who))c[s.who]=(c[s.who]||0)+1});const max=Math.max(0,...Object.values(c));if(max<2)return '';
      const lead=Object.keys(c).filter(k=>c[k]===max);return lead.length===1?`${lead[0]} owns ${max} steps`:`${and(lead)} own ${max} steps each`}},
  questions:{fig:k=>String(S[k].filter(q=>!answered(q)).length),cap:k=>`of ${S[k].length} unanswered`}};
function liveFn(id){const i=id.lastIndexOf('.'),k=id.slice(0,i),f=id.slice(i+1);const fn=(LV[KIND(k)]||{})[f];return fn?()=>fn(k):null}
function live(sec,tick=true){if(!sec)return;
  sec.querySelectorAll('[data-live]').forEach(el=>{const fn=liveFn(el.dataset.live);if(!fn)return;
    const v=fn();if(el.textContent===v)return;el.textContent=v;
    if(el.classList.contains('fig')){v==='0'?el.setAttribute('data-zero',''):el.removeAttribute('data-zero');if(tick)retick(el)}else if(tick&&el.classList.contains('tk'))retick(el)})}
function livePers(){const s=sec('pers');if(!s)return;const i=U.psel,p=S.pers[i],N=PQ().length;
  s.querySelectorAll('.ring').forEach(r=>{const q=+r.dataset.psel,d=pdone(S.pers[q]);r.querySelector('.arc').setAttribute('stroke-dashoffset',(RC*(1-d/N)).toFixed(1));r.classList.toggle('full',d===N);
    if(q===i)r.querySelector('.nmr').textContent=t(p.name)||'Unnamed audience'})}
function openZone(z){const j=+z.dataset.z,i=U.psel;
  if(!z.classList.contains('has')){U.popen=i+':'+j;render('pers')}
  const fs=sec('pers').querySelectorAll(`[data-p^="pers.${i}.qs.${j}.a."]`),last=fs[fs.length-1];if(last)focusField(last.dataset.p)}
function retick(el){el.classList.remove('tick');void el.offsetWidth;el.classList.add('tick')}
function paintColNames(){ROOT?.querySelectorAll('[data-coln]').forEach(el=>{const k=el.closest('.bd').dataset.board,v=colName(S[k].cols[+el.dataset.coln]);if(el.textContent!==v)el.textContent=v})}

/* ── markup helpers ── */
const F=(p,o={})=>`<span class="f${o.cls?' '+o.cls:''}" contenteditable="plaintext-only" spellcheck="false" data-p="${p}"${o.ph?` data-ph="${esc(o.ph)}"`:''}${o.label||o.ph?` aria-label="${esc(o.label||o.ph)}"`:''}>${esc(get(p))}</span>`;
const head=(b,title,right='')=>`<header class="hd"><div><p class="eb lbl"><i class="tri"></i>${esc(BD(b).eyebrow||BD(b).name)}</p><h2 class="ttl" id="t-${b}">${esc(title??BD(b).title)}</h2></div><div class="hr">${tools(b)}${right?`<div class="hfig">${right}</div>`:''}</div></header>`;
const figure=(b,ink='')=>`<p class="fig${ink}" data-live="${b}.fig"></p><p class="lbl cap" data-live="${b}.cap"></p>${(LV[KIND(b)]||{}).note?`<p class="lbl cap note" data-live="${b}.note"></p>`:''}`;

/* ── the corners ── */
const IC={
  undo:'<svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>',
  gear:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  play:'<svg class="g play" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5a1 1 0 0 1 1.52-.86l12 7.5a1 1 0 0 1 0 1.72l-12 7.5A1 1 0 0 1 7 19.5z"/></svg>',
  pause:'<svg class="g pause" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="4" width="4.5" height="16" rx="1"/><rect x="13.5" y="4" width="4.5" height="16" rx="1"/></svg>',
  down:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 19h14"/></svg>',
  plus:'<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 3.5v13M3.5 10h13"/></svg>',
  minus:'<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 10h13"/></svg>',
  x:'<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 2.5l7 7M9.5 2.5l-7 7"/></svg>'};
function toolsHTML(b){const h=H[H.length-1],what=h&&h.b===b?t(h.what).replace(/\.$/,''):'';
  return (h&&h.b===b?`<button type="button" class="ib" data-undo data-tip="${what?'Undo: '+esc(what):'Undo'}" aria-label="${what?'Undo: '+esc(what):'Undo'}">${IC.undo}</button>`:'')+
    `<button type="button" class="ib gear" data-gear data-tip="Workshop" aria-label="Workshop settings" aria-expanded="${U.panel}">${IC.gear}</button>`}
const tools=b=>`<span class="tools" data-tools="${b}">${toolsHTML(b)}</span>`;
function paintTools(){ROOT?.querySelectorAll('[data-tools]').forEach(el=>{el.innerHTML=toolsHTML(el.dataset.tools)})}
function navHTML(b){const v=VIS(),cur=v.indexOf(b),next=v[cur+1];
  return `<div class="bf-nav"><div class="bf-stack"><div class="bf-dock" tabindex="0" role="slider" aria-label="Boards: ${cur+1} of ${v.length}, ${esc(NAME(b))}. Arrows choose a board, Enter goes to it" aria-valuemin="1" aria-valuemax="${v.length}" aria-valuenow="${cur+1}">${v.map((k,i)=>`<span class="bf-cl${i<=cur?' on':''}" data-i="${i}"><i></i></span>`).join('')}<span class="bf-dl" aria-hidden="true"></span></div>
  ${next?`<span class="bf-upn">Up next<b>${esc(NAME(next))}</b></span>`:''}</div></div>`}
function timeHTML(b){if(S.call.tk&&(S.mins[b]||0)>0)return `<button type="button" class="bf-pace" data-pace data-state="${PACE.paused?'paused':'running'}"><span class="bf-el" aria-hidden="true"></span><span class="bf-rw"><svg class="bf-ring" viewBox="0 0 40 40" aria-hidden="true"><circle class="trk" cx="20" cy="20" r="17"/><circle class="brd" cx="20" cy="20" r="17" pathLength="100"/></svg>${IC.play}${IC.pause}</span></button>`;
  return tmrHTML(b)}
const TMIN=[1,2,3,5,10,15];
function tmrHTML(b){const x=U.tmr[b];
  if(!x)return `<button type="button" class="bf-keep" data-tadd="${b}">+ Timer</button>`;
  if(x.pick)return `<span class="bf-pick" role="group" aria-label="Timer length">${TMIN.map(m=>`<button type="button" class="bf-chip" data-tset="${b}" data-m="${m}">${m} min</button>`).join('')}<button type="button" class="bf-keep on" data-tx="${b}">Cancel</button></span>`;
  return `<span class="bf-tmr"><button type="button" class="bf-keep bf-tx" data-treset="${b}">Reset</button><button type="button" class="bf-keep bf-tx" data-tx="${b}">Remove</button><button type="button" class="bf-pace" data-ttog="${b}" data-state="running"><span class="bf-el" aria-hidden="true"></span><span class="bf-rw"><svg class="bf-ring" viewBox="0 0 40 40" aria-hidden="true"><circle class="trk" cx="20" cy="20" r="17"/><circle class="brd" cx="20" cy="20" r="17" pathLength="100"/></svg>${IC.play}${IC.pause}</span></button></span>`}
function paintTmr(){for(const b in U.tmr){const x=U.tmr[b];if(x.pick)continue;if(x.end){x.left=Math.max(0,(x.end-Date.now())/1000);if(!x.left)x.end=null}
  const btn=sec(b)?.querySelector(`[data-ttog="${b}"]`);if(!btn)continue;const left=Math.ceil(x.left),done=left===0;
  const brd=btn.querySelector('.brd');brd.style.setProperty('--p',1-x.left/x.total);brd.classList.toggle('over',done);btn.dataset.state=x.end||done?'running':'paused';
  btn.querySelector('.bf-el').innerHTML=done?'<span class="or">Time’s up</span>':`<b>${mmss(left)}</b><span class="of"> left</span>${x.end?'':'<span class="pz"> · paused</span>'}`;
  btn.setAttribute('aria-label',`Timer, ${done?'finished. Press to run it again':mmss(left)+' left. Press to '+(x.end?'pause':'resume')}`)}}
setInterval(()=>{if(ROOT&&Object.values(U.tmr).some(x=>x.end))paintTmr()},250);
const LOCAL=Intl.DateTimeFormat().resolvedOptions().timeZone;
const zoneShort=tz=>(new Intl.DateTimeFormat('en-US',{timeZone:tz,timeZoneName:'short'}).formatToParts(new Date()).find(p=>p.type==='timeZoneName')||{}).value||'';
function todText(){const tz=S.call.tz||LOCAL,now=new Date(),c=html.dataset.clock==='24';
  return `${new Intl.DateTimeFormat('en-US',{hour:'numeric',minute:'2-digit',hour12:!c,timeZone:tz}).format(now)}${tz!==LOCAL?`<span class="tz">${zoneShort(tz)}</span>`:''}`}
const foot=b=>`<footer class="ft bf" data-bf="${b}">${navHTML(b)}<div class="bf-right">${timeHTML(b)}<span class="bf-save" data-save></span>${S.call.tod?`<span class="bf-tday" data-tod>${todText()}</span>`:''}</div></footer>`;
const mmss=x=>`${Math.floor(x/60)}:${String(Math.floor(x)%60).padStart(2,'0')}`;
function paintPace(only){ROOT?.querySelectorAll('[data-bf]').forEach(f=>{const b=f.dataset.bf;if(only&&b!==only)return;const btn=f.querySelector('.bf-pace[data-pace]');if(!btn)return;
  const el=PACE.t[b]||0,min=S.mins[b]||0,P=min*60,over=P>0&&el>P;const p=P?Math.min(1,el/P):0;
  const brd=btn.querySelector('.brd');brd.style.setProperty('--p',p);brd.classList.toggle('over',over);btn.dataset.state=PACE.paused?'paused':'running';
  const pz=PACE.paused?'<span class="pz"> · paused</span>':'';
  btn.querySelector('.bf-el').innerHTML=over?`<span class="or">${mmss(el-P)} over</span>${pz}`:`<b>${mmss(el)}</b><span class="of"> of ${min} min</span>${pz}`;
  btn.setAttribute('aria-label',`${PACE.paused?'Resume':'Pause'} the clock. ${NAME(b)}: ${over?mmss(el-P)+' over':mmss(el)+' of '+min+' minutes'}`)})}
function paintTod(){if(!S.call.tod)return;const v=todText();ROOT?.querySelectorAll('[data-tod]').forEach(e=>{if(e.innerHTML!==v)e.innerHTML=v})}
let paceTick=0;
setInterval(()=>{const now=Date.now(),dt=PACE.last?(now-PACE.last)/1000:0;PACE.last=now;if(!S||!ROOT)return;
  const b=PACE.cur;if(S.call.tk&&!PACE.paused&&b&&KIND(b)!=='cover'&&KIND(b)!=='end'&&dt<5){PACE.t[b]=(PACE.t[b]||0)+dt;paintPace(b);if(++paceTick%40===0)keep()}},250);
setInterval(()=>{if(ROOT&&S)paintTod()},5000);
setInterval(()=>{if(ROOT&&S)paintSave()},1000);
function dockAt(d,x){const cells=[...d.querySelectorAll('.bf-cl')],r=d.getBoundingClientRect(),cw=r.width/cells.length,v=VIS();
  const reach=+(html.dataset.reach||2),hot=Math.max(0,Math.min(cells.length-1,Math.floor(x/cw)));
  cells.forEach((cl,i)=>{const dist=Math.abs((i+.5)*cw-x)/cw;let f=reach===0?(i===hot?1:0):Math.max(0,1-dist/(reach+.5));f=f*f*(3-2*f);cl.style.setProperty('--f',f.toFixed(3));cl.classList.toggle('hot',i===hot)});
  const lab=d.querySelector('.bf-dl'),cx=(hot+.5)*cw;lab.innerHTML=`<b>${n2(hot)}</b>${esc(NAME(v[hot]))}`;
  lab.style.setProperty('--x',cx+'px');lab.style.setProperty('--tx',cx-lab.offsetWidth/2<0?`${-cx}px`:'-50%');
  d.classList.add('open');d.setAttribute('aria-valuetext',`${hot+1} of ${v.length}, ${NAME(v[hot])}`);d._hot=hot;return hot}
function dockOff(d){d.classList.remove('open');d.querySelectorAll('.bf-cl').forEach(cl=>{cl.style.setProperty('--f',0);cl.classList.remove('hot')});d._hot=null}
function dockKey(d,i){const cw=d.getBoundingClientRect().width/d.querySelectorAll('.bf-cl').length;dockAt(d,(i+.5)*cw)}
function goBoard(i){const k=VIS()[i];const s=sec(k);if(s)s.scrollIntoView({behavior:motionOn()?'smooth':'auto',block:'start'})}

const addBtn=(path,text,empty)=>`<button type="button" class="add${empty?' always':''}" data-add="${path}">+ ${text}</button>`;
const spot=(b,cls,style='')=>`class="${cls}${U.lit[b]>=0?' has-on':''}" data-spot="${b}"${style?` style="${style}"`:''}`;
const on=(b,i)=>U.lit[b]===i?' on':'';
const GRIP='<svg viewBox="0 0 10 16" aria-hidden="true"><circle cx="2.5" cy="3" r="1.4"/><circle cx="7.5" cy="3" r="1.4"/><circle cx="2.5" cy="8" r="1.4"/><circle cx="7.5" cy="8" r="1.4"/><circle cx="2.5" cy="13" r="1.4"/><circle cx="7.5" cy="13" r="1.4"/></svg>';
const grip=(list,i,what)=>`<button type="button" class="grip" data-grip="${list}" data-i="${i}" aria-label="Move ${esc(what)}. Drag, or use the arrow keys">${GRIP}</button>`;
const num=(list,i,what)=>`<span class="n hn"><span class="num">${n2(i)}</span>${grip(list,i,what)}</span>`;
const pinitials=n=>t(n).split(/\s+/).slice(0,2).map(w=>w[0]||'').join('').toUpperCase();
const portrait=(i,cls)=>{const nm=S.pers[i]&&S.pers[i].name;return `<span class="${cls}">${pinitials(nm)?esc(pinitials(nm)):PERSON}</span>`};
const RC=2*Math.PI*46;
const ringArc=d=>`stroke-dasharray="${RC.toFixed(1)}" stroke-dashoffset="${(RC*(1-d/Math.max(1,PQ().length))).toFixed(1)}"`;

/* questions as columns: one per question, the answers a hairline list under it */
function qcols(k){const n=S[k].length,per=n===5?5:4;
  const cols=n<per?`repeat(${n},minmax(0,1fr)) calc(40 * var(--u))`:`repeat(${per},minmax(0,1fr))`;
  return `<div class="body"><div ${spot(k,'qgrid',`grid-template-columns:${cols}`)}>${S[k].map((q,i)=>`<div class="row qcol${on(k,i)}${answered(q)?' done':''}" data-i="${i}">
    <span class="qn"><span class="n">${n2(i)}</span><span class="qr"><button type="button" class="qx" data-qx="${k}" data-i="${i}" aria-label="Remove question ${n2(i)}">Remove</button></span></span>
    <span class="qq">${F(`${k}.${i}.q`,{ph:'Question'})}</span>${t(q.d)?`<span class="sub">${esc(q.d)}</span>`:''}
    <div class="qa-list" data-list="${k}.${i}.a">${(q.a.length?q.a:['']).map((_,j)=>`<span class="qans dr" data-item="${j}" style="--i:${i};--j:${j}"><span>${F(`${k}.${i}.a.${j}`,{label:'Answer'})}</span>${grip(`${k}.${i}.a`,j,'this answer')}</span>`).join('')}</div></div>`).join('')}
    <button type="button" class="qadd" data-add="${k}" aria-label="Add a question">+</button></div></div>`}

/* ── the boards, one renderer per kind ── */
const lockup=edit=>`<div class="lk"><span class="nm">${edit?F('cover.us',{ph:'Your studio',cls:'quiet'}):esc(t(S.cover.us))}${edit||t(S.cover.us)?'<span class="sep" aria-label="and"></span>':''}${edit?F('cover.client',{ph:'Client'}):esc(t(S.cover.client)||'Client')}</span></div>`;
const RK={R:'Responsible',A:'Accountable',C:'Consulted',I:'Informed'};
const RKD={R:'Does the work',A:'Answers for it; one person',C:'Asked before it is decided',I:'Told after it is decided'};
const PAIRW=['Very','Quite','A little','Both','A little','Quite','Very'];
const R={
cover:()=>`<div class="top"><p class="eb lbl"><i class="tri"></i>${F('cover.eyebrow',{ph:'Workshop'})}</p><div class="corner"><p class="lbl">${F('cover.date',{ph:'Date'})}</p>${tools('cover')}</div></div>
  <div class="big"><h1>${F('cover.title',{ph:'Project name'})}</h1></div>
  <div class="ft">${lockup(true)}<p class="guar">${F('cover.line',{ph:'One line under the names',cls:'quiet'})}</p></div>`,

agenda:k=>{const it=VIS().filter(x=>!['cover','agenda','end'].includes(KIND(x))).map(NAME),half=Math.ceil(it.length/2);
  const row=(s,i)=>`<button type="button" class="row${on(k,i)}" data-i="${i}" aria-pressed="${U.lit[k]===i}"><span class="n">${n2(i)}</span><span>${esc(s)}</span></button>`;
  return head(k)+`<div ${spot(k,'cols grow fit',`--rows:${Math.max(4,half)};--k:330`)}><div class="list">${it.slice(0,half).map(row).join('')}<div class="close"></div></div><div class="list">${it.slice(half).map((s,i)=>row(s,i+half)).join('')}<div class="close"></div></div></div>
  <div style="flex:1"></div>`+foot(k)},

team:k=>head(k,undefined,figure(k,' ink'))+
  `<div class="body"><div class="chr ch"><p class="lbl">Role</p><p class="lbl">Name</p></div>
  <div ${spot(k,'list grow fit',`--rows:${Math.max(4,S.team.length)};--k:270`)}>${S.team.map((m,i)=>`<div class="row${on(k,i)}" data-i="${i}"><span class="lbl">${F(`team.${i}.role`,{ph:'Role'})}</span><span><span class="avslot">${av(m.name,m)}</span>${F(`team.${i}.name`,{ph:'Name'})}</span></div>`).join('')}</div>
  <div class="close"></div>${addBtn('team','Add a person',!S.team.length)}</div>`+foot(k),

rows:k=>{const x=S[k],nc=x.cols.length;return head(k,undefined,figure(k))+
  `<div class="body"><div class="chr ch" style="--nc:${nc}"><p class="lbl">&nbsp;</p>${x.cols.map((c,j)=>`<p class="lbl" data-coln="${j}">${esc(colName(c))}</p>`).join('')}</div>
  <div ${spot(k,'list mark'+(nc===1?' one':''),`--nc:${nc}`)}>${x.rows.map((r,i)=>`<div class="row${on(k,i)}" data-i="${i}"><span class="lbl ink">${esc(r.label)}<span class="sub">${esc(r.def)}</span></span>${r.v.map((_,j)=>`<span>${F(`${k}.rows.${i}.v.${j}`,{label:`${colName(x.cols[j])}: ${r.label}`})}</span>`).join('')}</div>`).join('')}</div>
  <div class="close"></div></div>`+foot(k)},

goals:k=>head(k)+
  `<div class="cols">${S[k].map((bk,i)=>`<div class="bucket"><h3>${F(`${k}.${i}.q`,{ph:'Bucket'})}</h3><p class="lbl sub">${F(`${k}.${i}.d`,{ph:'Add a description'})}</p>
    <div class="list" data-list="${k}.${i}.a">${(bk.a.length?bk.a:['']).map((_,j)=>`<div class="gl dr" data-item="${j}"><span>${F(`${k}.${i}.a.${j}`,{label:t(bk.q)||'Entry'})}</span>${grip(`${k}.${i}.a`,j,'this entry')}</div>`).join('')}</div>
    ${addBtn(`${k}.${i}.a`,bk.add||'Add',!bk.a.length)}</div>`).join('')}</div>`+foot(k),

questions:k=>head(k,undefined,figure(k))+qcols(k)+foot(k),

personas:k=>{const d=BD(k),Q=PQ(),G=d.groups||[['Questions',Q.map((_,i)=>i)]];const i=Math.min(U.psel,S.pers.length-1),p=S.pers[i];if(!p)return '';
  const rings=S.pers.map((x,q)=>{const dn=pdone(x),nm=t(x.name)||'Unnamed audience';return `<button type="button" class="ring${q===i?' on':''}${dn===Q.length?' full':''}" data-psel="${q}" title="${esc(nm)}" aria-pressed="${q===i}" aria-label="${esc(nm)}, ${dn} of ${Q.length} answered"><span class="rr"><svg viewBox="0 0 100 100" aria-hidden="true"><circle class="bg" cx="50" cy="50" r="46"/><circle class="arc" cx="50" cy="50" r="46" ${ringArc(dn)}/></svg>${portrait(q,'ph')}</span><span class="nmr">${esc(nm)}</span></button>`}).join('');
  const tab=Math.min(U.ptab,G.length-1),idx=G[tab][1],zones=tab===0?idx.filter(j=>j!==0):idx;
  const zone=j=>{const q=p.qs[j],has=answered(q)||U.popen===i+':'+j;
    return `<div class="zone${has?' has':''}" data-z="${j}"${has?'':` tabindex="0" role="button" aria-label="Answer: ${esc(Q[j].q)}"`}><p class="q"><i class="dot"></i>${esc(Q[j].q)}</p>${Q[j].prompt?`<p class="pr">${esc(Q[j].prompt)}</p>`:''}<div class="as">${(q.a.length?q.a:['']).map((_,m)=>`<span class="a">${F(`pers.${i}.qs.${j}.a.${m}`,{label:Q[j].short||Q[j].q})}</span>`).join('')}</div></div>`};
  return `<div class="pe"><p class="eb lbl"><i class="tri"></i>${esc(d.eyebrow||d.name)} · ${n2(i)} · <span class="note" data-live="pers.note"></span></p>${tools(k)}</div>
  <header class="phd"><div class="pt">${portrait(i,'photo')}</div>
    <div class="pnm"><h2>${F(`pers.${i}.name`,{ph:'Name this audience',label:'Audience name'})}</h2><p class="role">${F(`pers.${i}.qs.0.a.0`,{label:Q[0]?Q[0].q:'Role'})}</p></div>
    <nav class="rings${S.pers.length>5?' many':''}" aria-label="Audiences" style="--n:${S.pers.length+1}">${rings}<button type="button" class="addp" data-padd aria-label="Add an audience"><span>+</span></button></nav></header>
  <nav class="tabs" aria-label="Question groups">${G.map(([name],x)=>`<button type="button" class="pill" data-ptab="${x}" aria-pressed="${x===tab}">${esc(name)}</button>`).join('')}</nav>
  <div class="pgrid${zones.length<2?' one':''}">${zones.map(zone).join('')}</div>`+foot(k)},

raci:k=>{const ppl=names();return head(k,undefined,figure(k))+
  `<div class="body"><div class="chr ch"><p class="lbl">Role</p>${['R','A','C','I'].map(x=>`<p class="lbl${x==='A'?' ink':''}">${RK[x]}<span class="sub">${RKD[x]}</span></p>`).join('')}</div>
  <div ${spot(k,'list grow'+(U.arm?' armed':''))}>${S.raci.map((r,i)=>`<div class="row${on(k,i)}" data-i="${i}"><span class="lbl">${F(`raci.${i}.role`,{ph:'Role'})}</span>${['R','A','C','I'].map(x=>`<span class="cell" data-k="${x}" data-kl="${RK[x]}" data-cell="${i}.${x}"><span class="avs">${avs(r[x])}</span>${F(`raci.${i}.${x}`,{cls:x==='A'?'acc':'',label:`${r.role}, ${RK[x]}`})}</span>`).join('')}</div>`).join('')}</div>
  <div class="close"></div>
  ${ppl.length?`<div class="tray${U.arm?' on':''}" role="group" aria-label="People"><span class="lbl">The team and names used in this workshop · tap to add to the cell you’re in, or drag onto any cell</span><span class="chips">${ppl.map(n=>`<button type="button" class="chip pp" data-person="${esc(n)}" aria-pressed="${U.arm===n}">${av(n)}${esc(n)}</button>`).join('')}</span></div>`:''}
  </div>`+foot(k)},

traits:k=>head(k,undefined,`<p class="ord" data-sl-ord></p><p class="lbl cap" data-sl-cap></p>`)+
  `<div class="body"><div class="chr ch"><p class="lbl"></p><div class="ticks">${PAIRW.map((x,j)=>`<p class="lbl${j===3?' mid':''}" data-tick="${j+1}">${x}</p>`).join('')}</div><p class="lbl"></p></div>
  ${S.traits.map((s,i)=>`<div class="srow" data-i="${i}"><div class="pa">${F(`traits.${i}.a`,{ph:'Word'})}</div>
    <div class="track" data-i="${i}">${[1,2,3,4,5,6,7].map(j=>`<button type="button" class="slot" data-slot="${j}" data-i="${i}" aria-label="${esc(PAIRW[j-1])} ${j<4?esc(s.a):j>4?esc(s.b):'both'}"></button>`).join('')}<span class="knob"></span></div>
    <div class="pb">${F(`traits.${i}.b`,{ph:'Word'})}</div></div>`).join('')}
  <div class="close"></div><div data-ins>${trInsHTML()}</div></div>`+foot(k),

week:k=>{const two=S.cadence===2;
  const band=(wk,w)=>`<div class="wk" data-wk="${w}">${two?`<p class="lbl wkl">Week ${w}</p>`:''}<div class="days">${S[wk].map((evs,d)=>`<div class="day"><h3>${DAYNAMES[d]}<span class="lbl">${evs.length} ${plural(evs.length,'event','events')}</span></h3>
    <div class="list" data-list="${wk}.${d}">${evs.map((e,i)=>`<div class="ev dr" data-item="${i}"><span>${F(`${wk}.${d}.${i}.name`,{ph:'Event'})}<span class="lbl">${F(`${wk}.${d}.${i}.dur`,{ph:'Duration'})}</span></span>${grip(wk+'.'+d,i,t(e.name)||'event')}</div>`).join('')}</div>
    ${addBtn(wk+'.'+d,'Add',!evs.length)}</div>`).join('')}</div></div>`;
  return head(k,BD(k).title||(two?'Two weeks with us':'A week with us'),
    `<div class="seg" role="group" aria-label="Rhythm"><button type="button" class="chip sm" data-cadence="1" aria-pressed="${!two}">1 week</button><button type="button" class="chip sm" data-cadence="2" aria-pressed="${two}">2 weeks</button></div>`)+
  `<div class="weeks">${band('week',1)}${two?band('week2',2):''}</div>`+foot(k)},

steps:k=>head(k,undefined,figure(k))+
  `<div class="body"><div class="chr ch"><p class="lbl">#</p><p class="lbl">Owner</p><p class="lbl">Step</p></div>
  <div class="list" data-list="steps">${S.steps.map((s,i)=>`<div class="row dr" data-i="${i}" data-item="${i}">${num('steps',i,`step ${n2(i)}`)}<span><button type="button" class="whob${t(s.who)?'':' none'}" data-who="${i}" aria-label="${t(s.who)?`Owner: ${esc(s.who)}. Change`:'Pick an owner'}" aria-expanded="${U.pick===i}">${t(s.who)?av(s.who)+esc(t(s.who)):''}</button></span><span>${F(`steps.${i}.what`,{ph:'Step'})}</span>
    ${U.pick===i?`<div class="pk" role="group" aria-label="Owner">${names().map(n=>`<button type="button" class="chip" data-owner="${esc(n)}" aria-pressed="${n===t(s.who)}">${av(n)}${esc(n)}</button>`).join('')}<span class="chip in"><span class="f" contenteditable="plaintext-only" spellcheck="false" data-newowner="${i}" data-ph="Someone else" aria-label="Type an owner, then Enter"></span></span><button type="button" class="chip no" data-owner="" aria-pressed="${!t(s.who)}">No owner</button></div>`:''}</div>`).join('')}</div>
  <div class="close"></div>${addBtn('steps','Add a step',!S.steps.length)}</div>`+foot(k),

timeline:()=>tlBoard(),
end:()=>endBoard()
};
const CLS={cover:'cover',agenda:'agenda',team:'team',rows:'mvv',goals:'goals',timeline:'tlb',questions:'qs',personas:'pers',raci:'raci',traits:'sl tr',week:'week',steps:'steps',end:'end'};

/* ── Personality: where each pair sits, and what the whole reads as ── */
const lean=s=>!s.pos?null:s.pos===4?0:s.pos<4?-1:1;
const leanWord=s=>s.pos<4?t(s.a):t(s.b);
const strength=s=>Math.abs((s.pos||4)-4);
function trInsHTML(){const tr=S.traits||[],un=tr.filter(x=>!x.pos).length;
  if(un)return `<div class="ins wait"><p class="lbl ink">What this says</p><p class="lbl">Place every pair to read the personality. ${un} not placed.</p></div>`;
  const strong=tr.filter(x=>strength(x)===3),leaning=tr.filter(x=>strength(x)===1||strength(x)===2).sort((a,b)=>strength(b)-strength(a)),both=tr.filter(x=>x.pos===4);
  const item=x=>`<div class="it"><h4>${esc(x.pos===4?`${t(x.a)} and ${t(x.b)}`:leanWord(x))}<span class="at">${x.pos===4?'both':'over '+esc(x.pos<4?t(x.b):t(x.a))}</span></h4></div>`;
  const col=(cls,label,list)=>`<div class="${cls}"><span class="tag">${label}<span class="ct">${list.length}</span></span>${list.length?list.map(item).join(''):'<p class="none">Nothing</p>'}</div>`;
  return `<div class="ins"><p class="lbl ink">What this says</p>${col('most','Balanced',both)}${col('mid','Leaning',leaning)}${col('least','Strongly',strong)}</div>`}
function paintTraits(tick=true){const s=sec('traits');if(!s||s.hidden)return;
  s.querySelectorAll('.srow').forEach(row=>{const i=+row.dataset.i,x=S.traits[i],k=row.querySelector('.knob'),l=lean(x);
    k.style.setProperty('--vp',x.pos||4);k.style.setProperty('--d',strength(x));k.dataset.pos=x.pos;
    k.textContent=!x.pos?'':x.pos===4?'Both':leanWord(x)||'—';
    k.className='knob'+(!x.pos?' un':strength(x)===3?' top':'');
    row.querySelector('.pa').classList.toggle('lean',l===-1);row.querySelector('.pb').classList.toggle('lean',l===1)});
  const placed=S.traits.filter(x=>x.pos&&x.pos!==4).sort((a,b)=>strength(b)-strength(a));
  const v=placed.slice(0,3).map(leanWord).join(' · ')||(S.traits.some(x=>x.pos)?'Balanced so far':'Nothing placed yet');
  const ord=s.querySelector('[data-sl-ord]');if(ord.textContent!==v){ord.textContent=v;if(tick)retick(ord)}
  const un=S.traits.filter(x=>!x.pos).length;s.querySelector('[data-sl-cap]').textContent=un?`${un} not placed`:'All placed';
  const ins=s.querySelector('[data-ins]');if(ins){const h=trInsHTML();if(ins.innerHTML!==h)ins.innerHTML=h}
  requestAnimationFrame(clampKnobs)}
function clampKnobs(){sec('traits')?.querySelectorAll('.track').forEach(tr=>{const k=tr.querySelector('.knob');if(k.classList.contains('held'))return;const W=tr.clientWidth,p=+(k.style.getPropertyValue('--vp')||4),cx=W*(p-.5)/7,h=k.offsetWidth/2;
  let n=0;if(cx-h<0)n=h-cx;if(cx+h>W)n=W-(cx+h);k.style.setProperty('--nudge',n+'px')})}
function placeTrait(i,k){const x=S.traits[i];if(x.pos===k){paintTraits(false);return}snap();x.pos=k;save();paintTraits();
  say('traits',k===4?`${t(x.a)} and ${t(x.b)}: both.`:`${t(x.a)} or ${t(x.b)}: ${PAIRW[k-1].toLowerCase()} ${leanWord(x).toLowerCase()}.`)}

/* ── the timeline: week 1 starts on the Monday of the workshop's week, read from the cover's date ── */
const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],WD=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
const WORDS={4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen',16:'sixteen',17:'seventeen',18:'eighteen',19:'nineteen',20:'twenty'};
const MI={jan:0,feb:1,mar:2,apr:3,may:4,jun:5,jul:6,aug:7,sep:8,oct:9,nov:10,dec:11};
function parseDate(s){s=t(s);let m=s.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);if(m)return new Date(+m[1],m[2]-1,+m[3]);
  m=s.match(/(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})/);if(m&&m[2].toLowerCase() in MI)return new Date(+m[3],MI[m[2].toLowerCase()],+m[1]);
  m=s.match(/([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})/);if(m&&m[1].toLowerCase() in MI)return new Date(+m[3],MI[m[1].toLowerCase()],+m[2]);return null}
function kickoff(){const d=parseDate(S.cover.date)||(S.created?new Date(S.created):new Date());return new Date(d.getFullYear(),d.getMonth(),d.getDate())}
function kickMon(){const k=kickoff();return new Date(k.getFullYear(),k.getMonth(),k.getDate()-(k.getDay()+6)%7)}
const dayAt=d=>{const m=kickMon();return new Date(m.getFullYear(),m.getMonth(),m.getDate()+d)};
const fmtD=d=>`${d.getDate()} ${MON[d.getMonth()]}`,fmtW=d=>`${WD[d.getDay()]} ${fmtD(d)}`;
const tlStart=p=>dayAt(p.s*7),tlEnd=p=>dayAt((p.s+p.n-1)*7+4);
const day7=w=>Math.round(w*7)/7,msDate=m=>dayAt(Math.round(m.w*7));
const wkS=p=>p.n===1?`W${p.s+1}`:`W${p.s+1}–W${p.s+p.n}`;
const wkM=w=>fmtW(dayAt(Math.round(w*7)));
const tlStk=()=>matchMedia('(max-width:720px)').matches;
const TLP=(name,s,n)=>({name,s,n}),TLM=(name,w)=>({name,w});
function tlBlock(){const T=S.tl,N=T.n,p=T.phases.find(p=>p.s+p.n>N-1);if(p)return t(p.name)||'An unnamed phase';const m=T.ms.find(m=>m.w>N-1);return m?(t(m.name)||'An unnamed milestone'):''}
function tlBoard(){const T=S.tl,N=T.n,st=U.tl,stk=tlStk(),fresh=st.fresh;
  const title=BD('tl').title||`The next ${WORDS[N]||N} weeks`;
  const block=tlBlock(),less=block?`${block} is in week ${N}`:`Remove week ${N}`;
  const weeks=`<div class="tl-wks"><span class="wn">${N} weeks</span><button type="button" class="ib sm" data-tlweeks="-1" data-tip="${esc(less)}" aria-label="${esc(less)}"${block||N<=4?' disabled':''}>${IC.minus}</button><button type="button" class="ib sm" data-tlweeks="1" data-tip="Add week ${N+1}" aria-label="Add week ${N+1}"${N>=26?' disabled':''}>${IC.plus}</button></div>`;
  let ticks='';for(let i=0;i<N;i++)ticks+=`<div class="tl-tick" data-w="${i}" style="left:${(i/N*100).toFixed(3)}%"><b>W${i+1}</b><span>${fmtD(dayAt(i*7))}</span></div>`;
  const ms=T.ms.map((m,i)=>{const x=m.w/N;return `<div class="tl-ms${fresh?' in':''}${x<.08?' l':x>.92?' e':''}" data-m="${i}" style="left:${(x*100).toFixed(3)}%;--i:${T.phases.length+i}">
      <div class="tl-dia" tabindex="0" role="button" aria-label="${esc(t(m.name)||'Unnamed milestone')}, ${fmtW(msDate(m))}. Arrow keys move it by a day, shift and arrows by a week; Backspace removes it."></div>
      <div class="ml"><b class="tl-nm tl-mn" contenteditable="plaintext-only" spellcheck="false" data-ph="Name this milestone" data-m="${i}">${esc(m.name)}</b><span>${fmtD(msDate(m))}</span></div>
      <button type="button" class="tl-x" data-tlx="ms" data-i="${i}" aria-label="Remove ${esc(t(m.name)||'this milestone')}">${IC.x}</button></div>`}).join('');
  const g=st.ghostMs,ghost=`<div class="tl-ms ghost${g==null?' off':''}" data-tlghost style="left:${g==null?0:(g/N*100).toFixed(3)}%"><div class="tl-dia"></div><div class="ml"><b>Add milestone</b><span>${g==null?'':fmtW(msDate({w:g}))}</span></div></div>`;
  const lines=T.ms.map(m=>`<div class="tl-mline" style="left:${(m.w/N*100).toFixed(3)}%"></div>`).join('');
  const rows=T.phases.map((p,i)=>`<div class="tl-row" data-i="${i}"><div class="tl-ph"><b data-tlph="${i}">${esc(p.name)}</b><span class="mu">${wkS(p)} · ${fmtD(tlStart(p))} – ${fmtD(tlEnd(p))}</span></div>
      <div class="tl-trk"><div class="tl-bar${fresh?' in':''}" data-i="${i}" tabindex="0" style="left:${(p.s/N*100).toFixed(3)}%;width:${(p.n/N*100).toFixed(3)}%;--i:${i}" aria-label="${esc(t(p.name)||'Unnamed phase')}, ${wkS(p)}, ${fmtD(tlStart(p))} to ${fmtD(tlEnd(p))}. Arrow keys move it; shift and arrows change its end; Enter edits the name; Backspace removes it.">
        <div class="tl-hl" aria-hidden="true"></div><span class="tl-nm" contenteditable="plaintext-only" spellcheck="false" data-ph="Name this phase" data-i="${i}">${esc(p.name)}</span><div class="tl-hr" aria-hidden="true"></div>
        <button type="button" class="tl-x" data-tlx="phase" data-i="${i}" aria-label="Remove ${esc(t(p.name)||'this phase')}">Remove${IC.x}</button></div></div></div>`).join('');
  const msl=T.ms.map((m,i)=>({m,i})).sort((a,b)=>a.m.w-b.m.w).map(({m,i})=>`<div class="mi"><i class="tl-dia"></i><b class="tl-mn" contenteditable="plaintext-only" spellcheck="false" data-m="${i}">${esc(m.name)}</b><span>${fmtW(msDate(m))}</span></div>`).join('');
  return head('tl',title,weeks)+`<div class="body"><div class="tl-wrap${stk?' stk':''}" data-tlmotion="${html.dataset.tlmotion||'draw'}">
    <div class="tl-span"><b>${fmtD(dayAt(0))} – ${fmtD(dayAt(N*7-3))}</b><span class="mu">${N} weeks from ${fmtW(kickoff())}</span></div>
    <div class="tl-axis addable" tabindex="0" role="button" aria-label="Add a milestone: click a day on the axis, or press Enter">${ticks}</div>
    <div class="tl-area"><div class="tl-grid" style="grid-template-columns:repeat(${N},1fr)">${'<i></i>'.repeat(N)}</div><div class="tl-lane">${ms}${ghost}</div>
      <div class="tl-rows">${lines}${rows}<button type="button" class="tl-addrow${T.phases.length?'':' always'}" data-tladd="phase">+ Phase</button></div></div>
    <div class="tl-msl">${msl}<button type="button" class="addms" data-tladd="ms">+ Milestone</button></div>
  </div></div>`+foot('tl')}
function tlAfter(s){s.style.setProperty('--rows',Math.max(S.tl.phases.length+1,1));U.tl.fresh=false;tlFit(s);tlPlace(s);
  if(U.tl.focus){const f=s.querySelector(U.tl.focus);U.tl.focus=null;if(f){f.focus({preventScroll:true});if(f.isContentEditable){const r=document.createRange();r.selectNodeContents(f);r.collapse(false);const g=getSelection();g.removeAllRanges();g.addRange(r)}}}}
function tlFit(s){s.querySelectorAll('.tl-bar').forEach(b=>{b.classList.remove('out');const nm=b.querySelector('.tl-nm');if(!nm)return;const pad=parseFloat(getComputedStyle(b).paddingLeft)*2;if(nm.scrollWidth+pad>b.clientWidth+1)b.classList.add('out')})}
function tlPlace(s){const lane=s.querySelector('.tl-lane');if(!lane)return;
  const ms=[...lane.querySelectorAll('.tl-ms:not(.ghost)')].map(el=>{el.style.removeProperty('--r');const r=el.querySelector('.ml').getBoundingClientRect();return {el,l:r.left,r:r.right}}).sort((a,b)=>a.l-b.l);
  const ends=[];let rows=0;for(const m of ms){let row=0;while(ends[row]!==undefined&&ends[row]+12>m.l)row++;ends[row]=m.r;rows=Math.max(rows,row+1);if(row)m.el.style.setProperty('--r',row)}
  lane.style.setProperty('--mrows',rows)}
function tlChange(what,fn,focus){snap();fn();save();U.tl.focus=focus||null;render('tl');say('tl',what);render('end')}
function tlWeeks(d){const N=S.tl.n,n=N+d;if(n<4||n>26||(d<0&&tlBlock()))return;tlChange(d>0?`Added week ${n}`:`Removed week ${N}`,()=>{S.tl.n=n},`[data-tlweeks="${d}"]`)}
function tlAddPhase(){const T=S.tl,i=T.phases.length;tlChange('Added a phase',()=>T.phases.push(TLP('',clamp(T.phases.reduce((m,q)=>Math.max(m,q.s+q.n),0),0,T.n-2),2)),tlStk()?`.tl-bar[data-i="${i}"]`:`.tl-bar[data-i="${i}"] .tl-nm`)}
function tlAddMs(w){const T=S.tl,i=T.ms.length;U.tl.ghostMs=null;tlChange(`Added a milestone on ${wkM(w)}`,()=>T.ms.push(TLM('',w)),tlStk()?`.tl-msl .tl-mn[data-m="${i}"]`:`.tl-ms[data-m="${i}"] .tl-mn`)}
function tlRemove(kind,i){const T=S.tl,x=kind==='phase'?T.phases[i]:T.ms[i];tlChange(`Removed ${t(x.name)||(kind==='phase'?'an unnamed phase':'an unnamed milestone')}`,()=>(kind==='phase'?T.phases:T.ms).splice(i,1))}
function tlX(e){const r=sec('tl').querySelector('.tl-rows').getBoundingClientRect();return clamp((e.clientX-r.left)/r.width,0,1)}
function tlLight(s0,n){sec('tl').querySelectorAll('.tl-tick').forEach(x=>{const w=+x.dataset.w;x.classList.toggle('on',s0!==null&&w>=s0&&w<s0+n)})}
function tlGhost(w){const g=sec('tl')?.querySelector('[data-tlghost]');if(!g)return;U.tl.ghostMs=w;if(w==null){g.classList.add('off');return}const N=S.tl.n;
  g.classList.remove('off');g.style.left=(w/N*100)+'%';g.classList.toggle('l',w/N<.08);g.classList.toggle('e',w/N>.92);g.querySelector('.ml span').textContent=fmtW(msDate({w}))}
function tlDragBar(bar,e,mode){const T=S.tl,i=+bar.dataset.i,p=T.phases[i],N=T.n,start={s:p.s,n:p.n},grab=tlX(e)*N-p.s;let moved=false,cur={...start};
  const paint=()=>{bar.style.left=(cur.s/N*100)+'%';bar.style.width=(cur.n/N*100)+'%';tlFit(sec('tl'));tlLight(cur.s,cur.n)};
  const move=ev=>{const x=tlX(ev)*N;let nx;if(mode==='move')nx={s:clamp(Math.round(x-grab),0,N-start.n),n:start.n};else if(mode==='right')nx={s:start.s,n:clamp(Math.round(x)-start.s,1,N-start.s)};
    else{const s0=clamp(Math.round(x),0,start.s+start.n-1);nx={s:s0,n:start.s+start.n-s0}}
    if(nx.s!==cur.s||nx.n!==cur.n){cur=nx;moved=true;bar.classList.add('drag');paint()}};
  const up=()=>{bar.removeEventListener('pointermove',move);bar.removeEventListener('pointerup',up);bar.removeEventListener('pointercancel',up);bar.classList.remove('drag');tlLight(null);
    if(!moved){if(mode==='move'&&!tlStk()){const nm=bar.querySelector('.tl-nm');nm.focus();const r=document.createRange();r.selectNodeContents(nm);r.collapse(false);const g=getSelection();g.removeAllRanges();g.addRange(r)}return}
    if(cur.s===start.s&&cur.n===start.n){render('tl');return}
    tlChange(`${mode==='move'?'Moved':'Stretched'} ${t(p.name)||'the unnamed phase'} to ${wkS(cur)}`,()=>Object.assign(T.phases[i],cur),`.tl-bar[data-i="${i}"]`)};
  try{bar.setPointerCapture(e.pointerId)}catch(_){}bar.addEventListener('pointermove',move);bar.addEventListener('pointerup',up);bar.addEventListener('pointercancel',up)}
function tlDragMs(dia,e){const T=S.tl,el=dia.closest('.tl-ms'),i=+el.dataset.m,m=T.ms[i],N=T.n,w0=m.w;let cur=w0,moved=false;
  const move=ev=>{const w=clamp(day7(tlX(ev)*N),0,N);if(w!==cur){cur=w;moved=true;el.classList.add('drag');el.style.left=(w/N*100)+'%';el.querySelector('.ml span').textContent=fmtD(msDate({w}));tlLight(Math.min(N-1,Math.floor(w)),1)}};
  const up=()=>{dia.removeEventListener('pointermove',move);dia.removeEventListener('pointerup',up);dia.removeEventListener('pointercancel',up);el.classList.remove('drag');tlLight(null);
    if(!moved||cur===w0){if(moved)render('tl');return}tlChange(`Moved ${t(m.name)||'the unnamed milestone'} to ${wkM(cur)}`,()=>{T.ms[i].w=cur},`.tl-ms[data-m="${i}"] .tl-dia`)};
  try{dia.setPointerCapture(e.pointerId)}catch(_){}dia.addEventListener('pointermove',move);dia.addEventListener('pointerup',up);dia.addEventListener('pointercancel',up)}
function tlKey(e){const tg=e.target,T=S.tl,N=T.n;
  if(tg.isContentEditable&&tg.closest('.tlb')){if(e.key==='Enter'||e.key==='Escape'){e.preventDefault();tg.blur();(tg.closest('.tl-bar')||tg.closest('.tl-ms')?.querySelector('.tl-dia'))?.focus()}return true}
  if(tg.matches('.tl-axis')&&(e.key==='Enter'||e.key===' ')){e.preventDefault();tlAddMs(Math.ceil(N/2));return true}
  if(tg.matches('.tl-bar')){const i=+tg.dataset.i,p=T.phases[i],d=e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:0;
    if(d){e.preventDefault();const nx=e.shiftKey?{s:p.s,n:clamp(p.n+d,1,N-p.s)}:{s:clamp(p.s+d,0,N-p.n),n:p.n};if(nx.s===p.s&&nx.n===p.n)return true;
      tlChange(`${e.shiftKey?'Stretched':'Moved'} ${t(p.name)||'the unnamed phase'} to ${wkS(nx)}`,()=>Object.assign(T.phases[i],nx),`.tl-bar[data-i="${i}"]`);return true}
    if(e.key==='Enter'){e.preventDefault();const nm=tg.querySelector('.tl-nm');if(nm&&!tlStk())nm.focus();return true}
    if(e.key==='Backspace'||e.key==='Delete'){e.preventDefault();tlRemove('phase',i);return true}return true}
  if(tg.matches('.tl-lane .tl-dia')){const i=+tg.closest('.tl-ms').dataset.m,m=T.ms[i],d=e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:0;
    if(d){e.preventDefault();const w=clamp(day7(m.w+d*(e.shiftKey?1:1/7)),0,N);if(w===m.w)return true;tlChange(`Moved ${t(m.name)||'the unnamed milestone'} to ${wkM(w)}`,()=>{T.ms[i].w=w},`.tl-ms[data-m="${i}"] .tl-dia`);return true}
    if(e.key==='Enter'){e.preventDefault();tg.closest('.tl-ms').querySelector('.tl-mn').focus();return true}
    if(e.key==='Backspace'||e.key==='Delete'){e.preventDefault();tlRemove('ms',i);return true}return true}
  return false}

/* ── the ending: the deck's last board, built by rules from the answers, never typed into ──
   Tiles in priority order: the count (the one ink tile) · mission, with vision under it ·
   personality · the next milestone · named audiences · the longest answer · the most-said word ·
   up to three excerpts, one per board · words written · the team. Tech answers and dull ones
   are counted, never quoted. Under six answers every answer is shown instead. */
const END_STOP=new Set('a an the and or of to in on at for with they them their our we us is are can say that this before after until then if nothing one two three four five from by whether into out off does do not it its who what when where how all any every each nobody someone without'.split(' '));
const wcount=x=>x.trim().split(/\s+/).filter(Boolean).length;
const END_HEAD=116,END_FOOT=44;
function clientCol(x){const i=x.cols.findIndex(c=>String(c).includes('{client}'));return i<0?x.cols.length-1:i}
function missionBoard(){return VIS().find(k=>KIND(k)==='rows'&&S[k].rows.some(r=>/^(mission|vision)$/i.test(t(r.label))))}
function endBoards(){
  const qa=(title,kind,list,pre='')=>({title,kind,answers:list.flatMap(x=>(x.a||[]).map(t).filter(Boolean).map(a=>({q:pre?`${pre} · ${x.q}`:x.q,a})))});
  return VIS().map(k=>{const d=BD(k);
    if(d.kind==='rows'){const x=S[k],ci=clientCol(x);return qa(d.name,'human',x.rows.map(r=>({q:r.label,a:[r.v[ci]||'']})))}
    if(d.kind==='goals')return qa(d.name,'neutral',S[k]);
    if(d.kind==='questions')return qa(d.name,d.tone||'human',S[k]);
    if(d.kind==='personas')return {title:d.name,kind:'human',answers:S.pers.flatMap(p=>qa('','human',p.qs.map((q,j)=>({q:(PQ()[j]||{}).short||'',a:q.a})),t(p.name)).answers)};
    return null}).filter(b=>b&&b.answers.length)}
function endTiles(maxEx){
  let sd=[...WID].reduce((a,c)=>(a*31+c.charCodeAt(0))%2147483647,7919)+13;const rnd=()=>(sd=(sd*16807)%2147483647)/2147483647;
  const mb=missionBoard(),mbName=mb?NAME(mb):null;
  const boards=endBoards(),all=boards.flatMap(b=>b.answers.map(a=>({...a,board:b.title,kind:b.kind,words:wcount(a.a),once:b.title===mbName&&/^(mission|vision)$/i.test(a.q)})));
  const n=all.length,nb=boards.length;
  const dull=a=>a.words<3||/https?:\/\/|www\./i.test(a.a)||/\d+\.\d+/.test(a.a)||(a.a.match(/\d/g)||[]).length>3||(a.a.match(/\b[A-Z]{2,}\b/g)||[]).length>=2||((a.a.match(/,/g)||[]).length>=3&&a.words<=10);
  const pool=all.filter(a=>a.kind!=='tech'&&!dull(a)&&!a.once);
  const score=a=>(a.kind==='human'?2:0)+(/\b(we|they|our|us|me|my|them|someone|nobody|everyone|anyone)\b/i.test(a.a)?1:0)+(a.words>=6&&a.words<=24?1:0)+rnd()*.5;
  const freq={},wb={};pool.forEach(a=>a.a.toLowerCase().replace(/[^a-z’' ]/g,' ').split(/\s+/).forEach(w=>{if(w.length<3||END_STOP.has(w))return;freq[w]=(freq[w]||0)+1;(wb[w]=wb[w]||new Set()).add(a.board)}));
  const top=Object.entries(freq).sort((a,b)=>b[1]-a[1]||b[0].length-a[0].length)[0];
  const total=all.reduce((x,a)=>x+a.words,0);
  let mission='',vision='';if(mb){const x=S[mb],ci=clientCol(x);mission=t((x.rows.find(r=>/^mission$/i.test(t(r.label)))||{v:[]}).v[ci]);vision=t((x.rows.find(r=>/^vision$/i.test(t(r.label)))||{v:[]}).v[ci])}
  const named=S.off.pers?[]:S.pers.map((p,i)=>({i,name:t(p.name),role:t(p.qs[0]?.a?.[0])})).filter(p=>p.name);
  const nteam=S.off.team?0:team().filter(m=>t(m.name)).length;
  const T=[];
  T.push({kind:'hero',label:'The workshop',text:String(n),sub:n?`${n===1?'answer':'answers'} ${nb>1?`across ${nb} boards`:'on one board'}`:'Nothing answered yet',w:2,h:2,tone:'ink',big:true});
  if(mission)T.push({kind:'mission',label:vision?'Mission · Vision':'Mission',text:mission,sub:vision,subBig:true,w:2,h:2,tone:'or'});
  if(!S.off.traits&&S.traits&&S.traits.every(x=>x.pos)){const strong=S.traits.filter(x=>strength(x)===3),lean2=S.traits.filter(x=>strength(x)===1||strength(x)===2).sort((a,b)=>strength(b)-strength(a));
    const head=strong.length?strong:lean2;if(head.length)T.push({kind:'least',label:'Personality',text:and(head.map(leanWord)),sub:strong.length&&lean2.length?'Leaning '+and(lean2.slice(0,4).map(x=>leanWord(x).toLowerCase())):'',w:2,h:1,tone:'ln',big:head.length<=2})}
  const nms=S.off.tl?null:[...S.tl.ms].filter(m=>t(m.name)).sort((a,b)=>a.w-b.w)[0];
  if(nms)T.push({kind:'ms',label:'Next milestone',text:fmtD(msDate(nms)),sub:t(nms.name),w:1,h:1,big:true,side:true});
  if(named.length)T.push({kind:'personas',label:`${NAME('pers')} · ${named.length}`,text:'',people:named.slice(0,4),w:named.length>=3?3:2,h:2});
  if(n<6){all.filter(a=>!a.once).forEach(a=>T.push({kind:'quote',label:`${a.board} · ${a.q}`,text:a.a,w:2,h:2}))}
  else{
    const long=[...pool].sort((a,b)=>b.words-a.words)[0];
    if(long&&long.words>=8)T.push({kind:'quote',label:`Longest answer · ${long.board}`,text:long.a,sub:`${long.words} words`,w:2,h:2});
    if(top&&top[1]>=3&&wb[top[0]].size>=2)T.push({kind:'word',label:'Most said',text:top[0],sub:`${top[1]} times`,w:2,h:1,tone:mission?'':'or',big:true});
    const used=new Set(long?[long.board]:[]);let c=0;
    for(const a of pool.filter(a=>a!==long).map(a=>({a,s:score(a)})).sort((x,y)=>y.s-x.s).map(x=>x.a)){if(c>=maxEx)break;if(used.has(a.board))continue;used.add(a.board);T.push({kind:'excerpt',label:`${a.board} · ${a.q}`,text:a.a,w:a.a.length<60?2:3,h:1});c++}
    if(total>=300)T.push({kind:'count',label:'Words written',text:String(total),w:1,h:1,big:true,side:true});
    if(nteam>=3)T.push({kind:'count',label:'Team',text:String(nteam),w:1,h:1,big:true,side:true});
  }
  return endPack(T)}
const endLgap=()=>parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--end-lgap-n'))||16;
function endFit(s){if(innerWidth<760)return;s.querySelectorAll('.e-tile').forEach(t=>{let fs=parseFloat(t.style.getPropertyValue('--fs'))||0,g=0;
  while(fs>18&&t.scrollHeight>t.clientHeight+1&&g++<40){fs-=2;t.style.setProperty('--fs',fs)}})}
function endPack(T){
  T.forEach((t,i)=>t.o=i);
  const side=T.filter(t=>t.side).slice(0,4);T=T.filter(t=>!t.side);const W=side.length?5:6;
  if(T.length<=4&&T.reduce((x,t)=>x+t.w,0)<=W)T.forEach(t=>t.h=4);
  const blocks=[];let cur=null;
  T.forEach(t=>{if(!cur||cur.h+t.h>4){cur={tiles:[],h:0,w:0};blocks.push(cur)}cur.tiles.push(t);cur.h+=t.h;cur.w=Math.max(cur.w,t.w)});
  const kept=[];let width=0;
  for(const b of blocks){const rem=W-width;if(rem<=0)break;if(b.w>rem){b.tiles=b.tiles.filter(t=>t.w<=rem+1);if(!b.tiles.length)break;b.w=Math.min(rem,Math.max(...b.tiles.map(t=>t.w)));b.h=b.tiles.reduce((x,t)=>x+t.h,0)}kept.push(b);width+=b.w}
  let i=kept.length-1,guard=0;while(kept.length&&width<W&&guard++<40){const b=kept[i];if(b.w<4||kept.every(k=>k.w>=4)){b.w++;width++}i=(i-1+kept.length)%kept.length}
  if(side.length)kept.push({tiles:side.map(t=>({...t,h:1})),h:side.length,w:1});
  kept.forEach(b=>{if(b.h<4){const t=b.tiles[b.tiles.length-1];t.h+=4-b.h;b.h=4}});
  let col=1;kept.forEach(b=>{let row=1;b.tiles.forEach(t=>{t.col=col;t.row=row;t.span=b.w;row+=t.h});col+=b.w});
  const out=kept.flatMap(b=>b.tiles).sort((a,b)=>a.row-b.row||a.col-b.col);
  const colW=(1440-80-80)/6,rowH=(900-80-48-END_HEAD-16-END_FOOT-16)/4;
  out.forEach(t=>{const W=t.span*colW+(t.span-1)*16-64,H=t.h*rowH+(t.h-1)*16-(t.h===1?48:64)-30-endLgap()-(t.sub?(t.subBig?60:34):0);
    t.py=t.h===1?24:32;t.pxx=t.h===1&&t.span>1?32:t.h===1?24:32;
    if(t.big){let fs=t.kind==='least'?52:t.side||t.h===1?64:t.h===2?150:240;fs=Math.min(fs,W/(t.text.length*.56));t.fs=Math.floor(fs);t.lh='.9';t.ls='-.05em'}
    else if(t.kind!=='personas'){let fs=Math.sqrt(H*W/(t.text.length*.5*1.12));fs=Math.min(fs,t.h===1?34:t.h===2?44:64,W/(Math.max(...t.text.split(' ').map(w=>w.length))*.56));t.fs=Math.max(18,Math.floor(fs));t.lh='1.1';t.ls='-.03em'}
    t.pd=t.h===4?120:t.span>=3?80:72});
  return out}
function endBoard(){const d=BD('end')||{};
  const tiles=endTiles(U.endEx);
  const dl=`<a class="ib" href="${API}/notes.md" download data-tip="Download the notes" aria-label="Download the notes as markdown">${IC.down}</a>`;
  return `<div class="e-bento"><header class="e-head"><div class="e-top"><p class="eb lbl"><i class="tri"></i>${esc(d.eyebrow||'That’s the workshop')}</p><span class="tools"><button type="button" class="ib gear" data-gear data-tip="Workshop" aria-label="Workshop settings" aria-expanded="${U.panel}">${IC.gear}</button>${dl}</span></div><h2 class="ttl" id="t-end">${esc(d.title||'Thank you, everyone.')}</h2></header><div class="e-grid" role="list">${tiles.map((x,i)=>`<div class="e-tile${x.tone?' e-'+x.tone:''}${x.big?' e-big':''}" role="listitem" style="--i:${i};--c:${x.col};--cs:${x.span};--r:${x.row};--rs:${x.h};--py:${x.py};--pxx:${x.pxx};--fs:${x.fs||0};--lh:${x.lh||1};--ls:${x.ls||0};--pd:${x.pd};--o:${x.o}">
    <p class="lbl">${x.kind==='ms'?'<i class="e-dia"></i>':''}${esc(x.label)}</p>
    ${x.people?`<div class="e-ppl">${x.people.map(p=>`<div class="e-pp"><span class="e-ep">${portrait(p.i,'ph')}</span><div><p class="e-nm">${esc(p.name)}</p>${p.role?`<p class="e-rl">${esc(p.role)}</p>`:''}</div></div>`).join('')}</div>`:`<p class="e-tx">${esc(x.text)}</p>`}
    ${x.sub?`<p class="e-sb${x.subBig?'':' e-m'}" style="--sg:${x.subBig?18:x.h===1?6:14};--ss:${x.subBig?22:15};--sw:${x.subBig?400:700}">${esc(x.sub)}</p>`:''}
  </div>`).join('')}</div><div class="e-foot">${lockup(false)}</div></div>`}

/* ── rendering ── */
const sec=b=>ROOT&&ROOT.querySelector(`[data-board="${b}"]`);
const LITK=['agenda','team','rows','questions','raci'];
const GROWK=['agenda','team','raci'];
function resetLit(){U.lit={};for(const b of S.boards)if(LITK.includes(b.kind))U.lit[b.key]=-1;U.psel=0;U.ptab=0;U.popen=null}
function litLen(k){const kind=KIND(k);if(kind==='agenda')return VIS().length;if(kind==='rows')return S[k].rows.length;return (S[k]||[]).length}
function clampLit(){for(const b in U.lit)if(U.lit[b]>=litLen(b))U.lit[b]=-1;if(U.psel>=S.pers.length)U.psel=Math.max(0,S.pers.length-1)}
function render(b){const s=sec(b);if(!s)return;const d=BD(b);s.hidden=!!S.off[b];if(s.hidden){s.innerHTML='';return}s.innerHTML=R[d.kind](b);live(s,false);
  if(d.kind==='traits')paintTraits(false);if(d.kind==='timeline')tlAfter(s);if(d.kind==='end')endFit(s);paintPace(b);paintTmr();paintSave()}
function renderAll(except){clampLit();paintTheme();for(const d of S.boards){const s=sec(d.key);if(except&&s&&s.contains(except))continue;render(d.key)}}
function focusField(p){const el=ROOT.querySelector(`[data-p="${p}"]`);if(!el)return;el.focus();const r=document.createRange();r.selectNodeContents(el);r.collapse(false);const s=getSelection();s.removeAllRanges();s.addRange(r)}
function land(sel){ROOT.querySelector(sel)?.classList.add('landed')}
function light(b,i){if(!(b in U.lit)||U.lit[b]===i)return;U.lit[b]=i;const s=sec(b),sp=s.querySelector('[data-spot]');if(!sp)return;
  sp.querySelectorAll('.row[data-i]').forEach(r=>{r.classList.toggle('on',+r.dataset.i===i);if(r.tagName==='BUTTON')r.setAttribute('aria-pressed',String(+r.dataset.i===i))});
  sp.classList.toggle('has-on',i>=0);live(s)}
function say(b,text,info){if(info)return;const h=H[H.length-1];if(h&&!h.b){h.b=b;h.what=text}paintTools()}
function undo(){const prev=H.pop();if(!prev)return;const at=S.at;S=JSON.parse(prev.s);S.pace=PACE.t;S.at=at;save();U.pick=null;U.arm=null;renderAll();if(U.panel)renderPanel()}
function paintTheme(){html.dataset.theme=(S&&S.call&&S.call.theme)||'light'}

/* ── the Deck panel, behind every gear: boards in and out, client and date, the call, the look ── */
const clockT=m=>`${Math.floor(m/60)%24}:${String(m%60).padStart(2,'0')}`;
const timed=()=>VIS().filter(k=>KIND(k)!=='end');
const total=()=>timed().reduce((a,k)=>a+(S.mins[k]||0),0);
function dpStatus(){const tt=total(),L=S.call.len,d=tt-L;return d>0?`<span class="over">${tt} of ${L} min · ${d} over</span>`:d<0?`<span class="note">${tt} of ${L} min · ${-d} free</span>`:`<span class="note">${tt} of ${L} min</span>`}
const DPF=(key,val,ph,cls='')=>`<span class="dp-f${cls?' '+cls:''}" contenteditable="plaintext-only" spellcheck="false" data-dpf="${key}" data-ph="${esc(ph)}" aria-label="${esc(ph)}">${esc(val)}</span>`;
const DPSW=(key,on,label)=>`<button type="button" class="dp-sw" role="switch" aria-checked="${on}" data-dpsw="${key}" aria-label="${esc(label)}"></button>`;
const ZONES=[['','This computer'],['America/Los_Angeles','Pacific'],['America/Denver','Mountain'],['America/Chicago','Central'],['America/New_York','Eastern'],['America/Sao_Paulo','São Paulo'],['Europe/London','London'],['Europe/Berlin','Central Europe'],['Asia/Singapore','Singapore'],['Australia/Sydney','Sydney']];
function dpMod(key,title,right,body,sum){const col=!!U.col[key];
  return `<section class="dp-mod${col?' col':''}" data-dpmod="${key}"><button type="button" class="dp-mh" data-dpcol="${key}" aria-expanded="${!col}"><span class="lbl">${title}</span><span class="note sm mr"><span class="open-r">${right||''}</span><span class="col-r">${sum||''}</span><i class="dp-chev" aria-hidden="true"></i></span></button><div class="dp-mcw"><div class="dp-mc">${body}</div></div></section>`}
function dpBoards(){const c=S.call;let st=0;
  return S.boards.map(({key:k,name,kind})=>{const on=!S.off[k],fixed=FIXED(k);let extra='';
    if(c.tk&&kind!=='end'){const ov=st+(S.mins[k]||0)>c.len;extra=`<span class="clk">${on?clockT(c.start+st):''}</span><span class="min${ov?' ov':''}">${DPF('min:'+k,on?S.mins[k]:'','min','num')} min</span>`}
    if(on&&kind!=='end')st+=S.mins[k]||0;
    const sw=fixed?`<span class="dp-sw fixed" role="switch" aria-checked="true" aria-disabled="true" title="Always in the workshop"></span>`:DPSW('on:'+k,on,`Show ${name}`);
    return `<div class="dp-brow${on?'':' off'}${c.tk&&kind!=='end'?' timed':''}">${sw}<span class="nm">${esc(name)}</span>${extra}</div>`}).join('')}
function dpSched(){const c=S.call,list=timed(),tt=total(),span=Math.max(c.len,tt);let st=0;
  const rows=list.map(k=>{const m=S.mins[k]||0,l=st/span*100,w=m/span*100,ov=st+m>c.len;
    const r=`<span class="st">${clockT(c.start+st)}</span><span class="sn">${esc(NAME(k))}</span><span class="sl"><span class="sb${ov?' ov':''}" style="left:${l}%;width:calc(${w}% - 2px)"><span class="eh" data-eh="${k}"></span><span class="smn">${m}</span></span>${tt>c.len?`<span class="end" style="left:${c.len/span*100}%"></span>`:''}</span>`;st+=m;return r}).join('');
  return `<div class="dp-sched">${rows}<span class="st">${clockT(c.start+st)}</span><span class="sn note">Ends</span><span class="sx">${tt>c.len?`<span class="over">${tt-c.len} min over</span>`:tt<c.len?`${c.len-tt} min free`:''}</span></div>`}
function dpHTML(){const c=S.call,n=timed().length;
  const fields=`<div class="dp-frow"><span class="lbl">Client</span>${DPF('client',S.cover.client,'Client')}</div><div class="dp-frow"><span class="lbl">Project</span>${DPF('title',S.cover.title,'Project name')}</div>
    <div class="dp-frow"><span class="lbl">Studio</span>${DPF('us',S.cover.us,'Your studio')}</div>
    <div class="dp-frow"><span class="lbl">Date</span>${DPF('date',S.cover.date,'Date of the workshop')}</div><div class="dp-frow"><span class="lbl">Starts</span>${DPF('start',clockT(c.start),'10:00')}</div>`;
  const tk=`<div class="dp-srow"><span>Keep time during the call<span class="sub">${c.tk?'Each board shows the time spent on it, from the moment it opens':'No ring and no minutes on the boards'}</span></span>${DPSW('tk',c.tk,'Keep time during the call')}</div>`;
  const len=c.tk?`<div class="dp-lrow"><span class="lbl">Length</span><div class="dp-chips">${[30,45,60,90,120].map(l=>`<button type="button" class="dp-chip" aria-pressed="${!c.custom&&c.len===l}" data-dplen="${l}">${l} min</button>`).join('')}<button type="button" class="dp-chip" aria-pressed="${!!c.custom}" data-dplen="custom">${c.custom?DPF('len',c.len,'min','num')+' min':'Custom'}</button></div></div>`:'';
  const tod=`<div class="dp-srow"><span>Show the time of day<span class="sub">${c.tod?'Small, bottom right of every board':'Hidden on every board'}</span></span>${DPSW('tod',c.tod,'Show the time of day')}</div>
    <div class="dp-frow"><span class="lbl">Time zone</span><select class="dp-tz" data-dptz aria-label="The time zone the clock shows">${ZONES.map(([z,l])=>`<option value="${z}"${(c.tz||'')===z?' selected':''}>${l} (${zoneShort(z||LOCAL)})</option>`).join('')}</select></div>`;
  const look=`<div class="dp-srow"><span>Light or dark<span class="sub">How the workshop looks in the room</span></span><span class="dp-seg" role="group" aria-label="Appearance"><button type="button" aria-pressed="${c.theme==='light'}" data-dptheme="light">Light</button><button type="button" aria-pressed="${c.theme==='dark'}" data-dptheme="dark">Dark</button></span></div>`;
  return `<div class="dp-veil" aria-hidden="true"><i></i><span></span><span></span><span></span><span></span><span></span></div>
    <div class="dp-hd"><p class="lbl">Workshop</p><button type="button" class="dp-x" data-dpclose aria-label="Close">×</button></div>
    <div class="dp-bd">
      ${dpMod('boards','Boards',c.tk?dpStatus():`${n} in the workshop`,dpBoards(),`${n} boards${c.tk?' · '+total()+' of '+c.len+' min':''}`)}
      ${dpMod('client','Client and date','',fields,[S.cover.client,S.cover.date].map(t).filter(Boolean).map(esc).join(' · ')||'Not filled yet')}
      ${dpMod('call','The call','',tk+len+tod,`${c.tk?c.len+' min, kept':'Time not kept'} · time of day ${c.tod?'shown':'hidden'}`)}
      ${c.tk?dpMod('sched','Schedule',`${clockT(c.start)} – ${clockT(c.start+c.len)} · drag a bar’s end`,dpSched(),`${clockT(c.start)} – ${clockT(c.start+c.len)}`):''}
      ${dpMod('look','Appearance','',look,c.theme==='dark'?'Dark':'Light')}
      <p class="dp-note" data-dpsave>${saveNote()}</p>
      <p class="dp-note"><a href="/">All workshops</a> · the notes download from the last board.</p>
    </div>`}
function renderPanel(){if(!ROOT)return;let el=ROOT.querySelector('.dp');
  if(!U.panel){if(el)el.hidden=true;paintTools();ROOT.querySelectorAll('.e-top .gear').forEach(g=>g.setAttribute('aria-expanded','false'));return}
  const y=el?.querySelector('.dp-bd')?.scrollTop||0,was=el&&!el.hidden;
  if(!el){el=document.createElement('aside');el.className='dp';el.setAttribute('aria-label','Workshop');ROOT.append(el)}
  el.innerHTML=dpHTML();el.hidden=false;if(was)el.style.animation='none';else el.style.animation='';el.querySelector('.dp-bd').scrollTop=y;
  paintTools();ROOT.querySelectorAll('.e-top .gear').forEach(g=>g.setAttribute('aria-expanded','true'))}
function setLen(len){const old=S.call.len;S.call.len=len;const list=timed(),tt=total();
  if(tt===old){list.forEach(k=>{S.mins[k]=Math.max(1,Math.round(S.mins[k]*len/old))});const drift=len-total();if(drift){const big=list.slice().sort((a,b)=>S.mins[b]-S.mins[a])[0];S.mins[big]+=drift}}}
function refreshFeet(){ROOT?.querySelectorAll('[data-bf]').forEach(f=>{f.outerHTML=foot(f.dataset.bf)});paintPace();paintTmr();paintSave()}
function coverChanged(){render('cover');paintColNames();render('tl');render('end');document.title=t(S.cover.title)||'Workshop'}
function dpCommit(key,text){const c=S.call,[k,b]=key.split(':');
  if(k==='min'){const n=parseInt(text,10);if(n>0)S.mins[b]=n}
  else if(k==='len'){const n=parseInt(text,10);if(n>0)setLen(n)}
  else if(k==='start'){const m=t(text).match(/^(\d{1,2})[:.h](\d{2})$/);if(m)c.start=(+m[1])*60+(+m[2])}
  else if(S.cover[k]!==text){S.cover[k]=text;coverChanged()}
  save();refreshFeet();requestAnimationFrame(renderPanel)}

/* one week or two. Week 2 eases in as a second band and eases out when hidden; its events are kept. */
function setCadence(n){if(S.cadence===n)return;snap();const s=sec('week');
  if(n===1){const kept=S.week2.reduce((a,d)=>a+d.filter(e=>t(e.name)).length,0);const band=s.querySelector('.wk[data-wk="2"]');
    let ran=false;const done=()=>{if(ran)return;ran=true;S.cadence=1;save();render('week');say('week',`Week 2 hidden. ${kept?`Its ${kept} ${plural(kept,'event is','events are')} kept.`:''}`.trim())};
    if(band&&motionOn()){band.classList.add('out');band.addEventListener('transitionend',done,{once:true});setTimeout(done,(cssn('--t-m')||260)+60)}else done();return}
  S.cadence=2;save();render('week');land('.wk[data-wk="2"]');say('week','Two weeks. Drag events into week 2, or → on a handle.')}

/* tidy a board's lists when you leave it: empty items go, open answers stay open */
function clean(b){const kind=KIND(b);
  if(kind==='goals')S[b].forEach(x=>x.a=x.a.filter(t));
  else if(kind==='team')S.team=S.team.filter(m=>t(m.name)||t(m.role));
  else if(kind==='steps')S.steps=S.steps.filter(x=>t(x.what)||t(x.who));
  else if(kind==='week'){S.week=S.week.map(d=>d.filter(e=>t(e.name)||t(e.dur)));S.week2=S.week2.map(d=>d.filter(e=>t(e.name)||t(e.dur)))}
  else if(kind==='personas')S.pers.forEach(p=>p.qs.forEach(q=>q.a=q.a.filter(t)));
  else if(kind==='questions'){S[b].forEach(q=>q.a=q.a.filter(t));S[b]=S[b].filter(q=>t(q.q)||q.a.length)}}

/* ── moving items: drag a handle, or focus it and use the arrow keys ── */
const group=l=>l.startsWith('week')?'week':/\.\d+\.a$/.test(l)?l.split('.')[0]+'.a':l;
const boardOf=l=>{const k=l.split('.')[0];return k==='week2'?'week':k};
function itemLabel(l,item){if(l.startsWith('week'))return t(item.name)||'the event';
  const s=typeof item==='string'?item:(item.q||item.what||'');const w=t(s).split(/\s+/);return w.length>5?'“'+w.slice(0,5).join(' ')+'…”':'“'+t(s)+'”'}
function moveItem(from,fi,to,ti){if(from===to&&fi===ti)return;snap();const item=get(from).splice(fi,1)[0];get(to).splice(ti,0,item);save();
  const b=boardOf(to);if(b in U.lit&&!/\.a$/.test(to)){const was=U.lit[b];U.lit[b]=was===fi&&from===to?ti:-1}
  render(b);land(`[data-list="${to}"] > [data-item="${ti}"]`);
  const where=to.startsWith('week')?DAYNAMES[+to.split('.')[1]]+(S.cadence===2?(to.startsWith('week2')?', week 2':', week 1'):''):from!==to?(KIND(b)==='goals'?t(S[b][+to.split('.')[1]].q)||'the bucket':/\.a$/.test(to)?'question '+n2(+to.split('.')[1]):'the list'):`position ${ti+1}`;
  say(b,`Moved ${itemLabel(to,item)} to ${where}.`);return b}
let drg=null;
function dropSpot(x,y){const el=document.elementFromPoint(x,y);let list=el&&el.closest('[data-list]');
  if(!list){const zone=el&&el.closest('.day,.bucket');list=zone&&zone.querySelector('[data-list]')}
  if(!list||group(list.dataset.list)!==group(drg.from))return null;
  const items=[...list.querySelectorAll(':scope > [data-item]')].filter(n=>n!==drg.row);
  let i=items.findIndex(n=>{const r=n.getBoundingClientRect();return y<r.top+r.height/2});if(i<0)i=items.length;
  return {list,i,items}}
function showLine(spot){let ln=document.querySelector('.drop-line');if(!spot){ln?.remove();return}
  if(!ln){ln=document.createElement('div');ln.className='drop-line';ROOT.append(ln)}
  const lr=spot.list.getBoundingClientRect();let y;
  if(spot.items.length===0)y=lr.top+2;else if(spot.i<spot.items.length)y=spot.items[spot.i].getBoundingClientRect().top;else y=spot.items[spot.items.length-1].getBoundingClientRect().bottom;
  Object.assign(ln.style,{left:lr.left+'px',width:lr.width+'px',top:(y-1)+'px'})}
addEventListener('pointermove',e=>{if(!drg)return;
  if(!drg.moving){if(Math.hypot(e.clientX-drg.x,e.clientY-drg.y)<5)return;drg.moving=true;
    const r=drg.row.getBoundingClientRect();drg.dx=drg.x-r.left;drg.dy=drg.y-r.top;
    const g=drg.row.cloneNode(true);g.classList.add('ghost');g.removeAttribute('data-item');g.style.width=r.width+'px';ROOT.append(g);drg.g=g;drg.row.classList.add('lifting');document.body.classList.add('dragging')}
  drg.g.style.left=(e.clientX-drg.dx)+'px';drg.g.style.top=(e.clientY-drg.dy)+'px';
  if(e.clientY<60)scrollBy(0,-14);else if(e.clientY>innerHeight-60)scrollBy(0,14);
  drg.spot=dropSpot(e.clientX,e.clientY);showLine(drg.spot)});
function endItemDrag(){if(!drg)return;const d=drg;drg=null;d.g?.remove();d.row.classList.remove('lifting');document.body.classList.remove('dragging');showLine(null);
  if(d.moving&&d.spot)moveItem(d.from,d.fi,d.spot.list.dataset.list,d.spot.i)}
addEventListener('pointerup',endItemDrag);addEventListener('pointercancel',endItemDrag);

/* ── RACI: people from the Team board, tapped or dragged into a cell ── */
function addPerson(i,k,name){const p=`raci.${i}.${k}`,cur=t(get(p)),role=S.raci[i].role;
  if(namesIn(cur).some(n=>n.toLowerCase()===name.toLowerCase())){say('raci',`${name} is already in ${role} · ${RK[k]}.`,true);return}
  snap();put(p,cur?cur+', '+name:name);save();const fig=sec('raci').querySelector('.fig')?.textContent;
  const active=document.activeElement?.dataset?.p;render('raci');if(sec('raci').querySelector('.fig').textContent!==fig)retick(sec('raci').querySelector('.fig'));
  if(active===p)focusField(p);land(`[data-cell="${i}.${k}"] .avs .av:last-child`);say('raci',`Added ${name} to ${role} · ${RK[k]}.`)}
let pdrag=null;
addEventListener('pointermove',e=>{if(!pdrag)return;
  if(!pdrag.moving){if(Math.hypot(e.clientX-pdrag.x,e.clientY-pdrag.y)<5)return;pdrag.moving=true;
    const g=pdrag.chip.cloneNode(true);g.classList.add('ghost','chipghost');ROOT.append(g);pdrag.g=g;document.body.classList.add('dragging')}
  pdrag.g.style.left=(e.clientX+8)+'px';pdrag.g.style.top=(e.clientY+8)+'px';
  const c=document.elementFromPoint(e.clientX,e.clientY)?.closest('.raci [data-cell]');if(c!==pdrag.over){pdrag.over?.classList.remove('target');c?.classList.add('target');pdrag.over=c}});
addEventListener('pointerup',()=>{if(!pdrag)return;const d=pdrag;pdrag=null;d.g?.remove();d.over?.classList.remove('target');document.body.classList.remove('dragging');
  if(d.moving){U.dragged=true;setTimeout(()=>U.dragged=false);if(d.over){const [i,k]=d.over.dataset.cell.split('.');addPerson(+i,k,d.chip.dataset.person)}}});
function disarm(){if(!U.arm)return;U.arm=null;const s=sec('raci');s.querySelectorAll('.chip.pp').forEach(c=>c.setAttribute('aria-pressed','false'));s.querySelector('[data-spot]').classList.remove('armed');s.querySelector('.tray')?.classList.remove('on')}

/* tapping a board's background puts it back the way it loaded */
function settle(b){const s=sec(b);if(b in U.lit)light(b,-1);if(s.contains(document.activeElement))document.activeElement.blur();
  if(b==='steps'&&U.pick!==null){U.pick=null;render('steps')}if(b==='raci')disarm()}

function enterAgenda(){const s=sec('agenda');if(!s||U.entered.agenda)return;U.entered.agenda=true;
  const rows=[...s.querySelectorAll('.row[data-i]')],tot=cssn('--ag-total')||2500;
  if(!motionOn()||!rows.length){s.dataset.enter='';return}
  const tm=cssn('--t-m')||260,step=Math.max(0,(tot-tm)/Math.max(1,rows.length-1));s.style.setProperty('--ag-step',step+'ms');rows.forEach((r,i)=>r.style.setProperty('--i',i));s.dataset.enter='travel';setTimeout(()=>{s.dataset.enter='';rows.forEach(r=>r.style.removeProperty('--i'))},tot+tm+50)}
let io=null,io2=null;const RATIO={};
function watch(){io?.disconnect();io=new IntersectionObserver(es=>es.forEach(x=>{if(!x.isIntersecting)return;const b=x.target.dataset.board;if(b==='agenda')enterAgenda();if(b==='end')render('end');if(b==='tl'){tlFit(x.target);tlPlace(x.target)}}),{threshold:.3});
  for(const b of ['agenda','end','tl']){const s=sec(b);if(s)io.observe(s)}
  io2?.disconnect();io2=new IntersectionObserver(es=>{es.forEach(x=>{RATIO[x.target.dataset.board]=x.isIntersecting?x.intersectionRect.height:0});
    let best=null,h=0;for(const k in RATIO)if(RATIO[k]>h){h=RATIO[k];best=k}if(best&&best!==PACE.cur){PACE.cur=best;if(S.at!==best){S.at=best;keep()}}},{threshold:[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]});
  ROOT.querySelectorAll('.bd').forEach(x=>io2.observe(x))}

/* ── wiring ── */
let drag=null;
function wire(root){
  root.addEventListener('pointerdown',e=>{
    const gp=e.target.closest('.grip');
    if(gp&&e.button===0){e.preventDefault();const row=gp.closest('[data-item]');drg={row,from:gp.dataset.grip,fi:+gp.dataset.i,x:e.clientX,y:e.clientY,moving:false};return}
    const ch=e.target.closest('.chip.pp');
    if(ch&&e.button===0){e.preventDefault();pdrag={chip:ch,x:e.clientX,y:e.clientY,moving:false};return}
    const k=e.target.closest('.tr .knob');
    if(k&&e.button===0){const tr=k.closest('.track');e.preventDefault();k.setPointerCapture(e.pointerId);drag={k,tr,i:+tr.dataset.i,x0:e.clientX,moved:false,slot:+k.dataset.pos||4};return}
    const cell=e.target.closest('.raci .armed [data-cell]');
    if(cell&&U.arm){e.preventDefault();const [i,kk]=cell.dataset.cell.split('.');const n=U.arm;disarm();addPerson(+i,kk,n);return}
    const dk=e.target.closest('.bf-dock');
    if(dk){if(e.pointerType!=='mouse'){dk.setPointerCapture(e.pointerId);dockAt(dk,e.clientX-dk.getBoundingClientRect().left)}return}
    const eh=e.target.closest('[data-eh]');
    if(eh){e.preventDefault();const k=eh.dataset.eh,m0=S.mins[k],x0=e.clientX,box=eh.closest('.sl').getBoundingClientRect(),span=Math.max(S.call.len,total());
      const mv=ev=>{const m=Math.max(1,m0+Math.round((ev.clientX-x0)/box.width*span));if(m!==S.mins[k]){S.mins[k]=m;renderPanel();ROOT.querySelector('.dp-sched')?.classList.add('dragging')}};
      const up=()=>{removeEventListener('pointermove',mv);removeEventListener('pointerup',up);save();renderPanel();refreshFeet()};
      addEventListener('pointermove',mv);addEventListener('pointerup',up);return}
    const s=e.target.closest('.bd');if(!s)return;const b=s.dataset.board,kind=KIND(b);
    if(kind==='timeline'){if(e.button!==0||e.target.closest('.tl-x,button,.bf'))return;
      const dia=e.target.closest('.tl-lane .tl-ms:not(.ghost) .tl-dia');if(dia){e.preventDefault();tlDragMs(dia,e);return}
      const bar=e.target.closest('.tl-bar');if(bar){if(tlStk())return;const nm=e.target.closest('.tl-nm');if(nm&&document.activeElement===nm)return;e.preventDefault();tlDragBar(bar,e,e.target.closest('.tl-hl')?'left':e.target.closest('.tl-hr')?'right':'move');return}
      if(!e.target.closest('.tl-axis,[contenteditable]'))settle(b);return}
    if(kind==='personas'){const z=e.target.closest('.zone');
      if(z&&!e.target.closest('[data-p],button')){e.preventDefault();openZone(z);return}
      if(!e.target.closest('[data-p],button,.bf'))settle(b);return}
    if(!e.target.closest('.row,[data-p],button,.knob,.track,.ev,.gl,.bucket h3,.line,.chip,.tray,.bf,.add,.pk,.ticks,.ins,a')){settle(b);return}
    if(kind==='questions'){const col=e.target.closest('.qcol');if(col&&!e.target.closest('[data-p],button')){e.preventDefault();const fs=col.querySelectorAll('.qa-list [data-p]'),last=fs[fs.length-1];if(last)focusField(last.dataset.p)}return}
    if(!GROWK.includes(kind)||kind==='agenda')return;
    if(e.target.closest('button,.add'))return;
    const row=e.target.closest('[data-spot] .row[data-i]');if(!row)return;
    const i=+row.dataset.i;if(e.target.closest('[data-p]')){light(b,i);return}
    light(b,U.lit[b]===i?-1:i)});
  root.addEventListener('pointermove',e=>{const dk=e.target.closest('.bf-dock')||(e.pointerType!=='mouse'&&ROOT.querySelector('.bf-dock.open'));
    if(dk&&(e.pointerType==='mouse'||dk.hasPointerCapture(e.pointerId)))dockAt(dk,e.clientX-dk.getBoundingClientRect().left);
    const ax=e.target.closest('.tl-axis');if(ax)tlGhost(clamp(day7(tlX(e)*S.tl.n),0,S.tl.n))});
  root.addEventListener('pointerout',e=>{const dk=e.target.closest?.('.bf-dock');if(dk&&e.pointerType==='mouse'&&!dk.contains(e.relatedTarget))dockOff(dk);
    const ax=e.target.closest?.('.tl-axis');if(ax&&!ax.contains(e.relatedTarget))tlGhost(null)});
  root.addEventListener('pointerup',e=>{const dk=e.target.closest('.bf-dock')||ROOT.querySelector('.bf-dock.open');if(!dk||!(dk.contains(e.target)||dk.hasPointerCapture?.(e.pointerId)))return;
    if(e.pointerType!=='mouse')dockAt(dk,e.clientX-dk.getBoundingClientRect().left);const i=dk._hot;dockOff(dk);if(i!=null)goBoard(i)});
  root.addEventListener('focusin',e=>{const dk=e.target.closest?.('.bf-dock');if(dk&&e.target===dk&&dk.matches(':focus-visible')){const v=VIS();dockKey(dk,v.indexOf(dk.closest('.bd').dataset.board))}});
  root.addEventListener('focusout',e=>{const dk=e.target.closest?.('.bf-dock');if(dk&&e.target===dk)dockOff(dk)});
  root.addEventListener('change',e=>{const z=e.target.closest('[data-dptz]');if(!z)return;S.call.tz=z.value;save();refreshFeet();renderPanel()});
  /* Team: a mouse resting on a person for a moment lights them, unless someone is typing on the board */
  let hov={t:0,row:null};
  root.addEventListener('pointermove',e=>{if(e.pointerType!=='mouse')return;
    const row=e.target.closest('.team [data-spot] .row[data-i]');if(row===hov.row)return;clearTimeout(hov.t);hov.row=row;if(!row)return;
    hov.t=setTimeout(()=>{const s=sec('team');if(!s||!row.isConnected)return;const a=document.activeElement;if(s.contains(a)&&a.closest('[data-p]'))return;
      const i=+row.dataset.i;if(U.lit.team===i||drg||pdrag)return;light('team',i)},160)});
  root.addEventListener('pointerleave',()=>{clearTimeout(hov.t);hov.row=null});
  /* Personality: drag a dot along its seven steps */
  root.addEventListener('pointermove',e=>{if(!drag)return;const r=drag.tr.getBoundingClientRect();
    if(!drag.moved){if(Math.abs(e.clientX-drag.x0)<4)return;drag.moved=true;drag.k.classList.add('held')}
    const x=Math.max(0,Math.min(r.width,e.clientX-r.left));drag.k.style.left=x+'px';drag.k.style.setProperty('--nudge','0px');
    const slot=Math.min(7,Math.floor(x/(r.width/7))+1);if(slot!==drag.slot){drag.slot=slot;
      drag.tr.querySelectorAll('.slot').forEach(s=>s.classList.toggle('over',+s.dataset.slot===slot));
      sec('traits').querySelectorAll('[data-tick]').forEach(t=>t.classList.toggle('over',+t.dataset.tick===slot))}});
  const endDrag=()=>{if(!drag)return;const d=drag;drag=null;d.tr.querySelectorAll('.slot.over').forEach(s=>s.classList.remove('over'));sec('traits').querySelectorAll('[data-tick].over').forEach(t=>t.classList.remove('over'));
    d.k.classList.remove('held');d.k.style.left='';if(d.moved)placeTrait(d.i,d.slot);else paintTraits(false)};
  root.addEventListener('pointerup',endDrag);root.addEventListener('pointercancel',endDrag);
  root.addEventListener('focusin',e=>{const f=e.target.closest('[data-p]');if(!f)return;const row=f.closest('[data-spot] .row[data-i]');if(row)light(row.closest('.bd').dataset.board,+row.dataset.i);
    setTimeout(()=>{if(document.activeElement!==f)return;const sel=getSelection();if(sel.rangeCount&&f.contains(sel.anchorNode))return;
      const r=document.createRange();r.selectNodeContents(f);r.collapse(false);sel.removeAllRanges();sel.addRange(r)})});
  root.addEventListener('input',e=>{const tn=e.target.closest('.tlb [contenteditable]');
    if(tn){if(!tn.textContent)tn.innerHTML='';if(tn.dataset.i!=null){S.tl.phases[+tn.dataset.i].name=tn.textContent;tlFit(sec('tl'));const ph=sec('tl').querySelector(`[data-tlph="${tn.dataset.i}"]`);if(ph)ph.textContent=tn.textContent}
      else if(tn.dataset.m!=null)S.tl.ms[+tn.dataset.m].name=tn.textContent;save();return}
    const f=e.target.closest('[data-p]');if(!f)return;if(f.textContent==='')f.innerHTML='';put(f.dataset.p,f.textContent);save();
    const s=f.closest('.bd'),b=s.dataset.board,kind=KIND(b);live(s);
    if(kind==='cover'){paintColNames();document.title=t(S.cover.title)||'Workshop'}
    if(kind==='traits')paintTraits(false);
    if(kind==='team'){const i=+f.closest('.row').dataset.i;f.closest('.row').querySelector('.avslot').innerHTML=av(S.team[i].name,S.team[i])}
    if(kind==='raci'){const c=f.closest('[data-k]');if(c)c.querySelector('.avs').innerHTML=avs(f.textContent)}
    if(kind==='questions'){const col=f.closest('.qcol');if(col)col.classList.toggle('done',answered(S[b][+col.dataset.i]))}
    if(kind==='personas'){const z=f.closest('.zone');if(z){const j=+z.dataset.z;z.classList.toggle('has',answered(S.pers[U.psel].qs[j])||U.popen===U.psel+':'+j)}livePers()}});
  root.addEventListener('focusout',e=>{const df=e.target.closest('[data-dpf]');if(df){dpCommit(df.dataset.dpf,df.textContent);return}
    const tn=e.target.closest('.tlb [contenteditable]');if(tn){render('end');return}
    const f=e.target.closest('[data-p]');if(!f)return;const s=f.closest('.bd'),b=s.dataset.board,kind=KIND(b);
    requestAnimationFrame(()=>{const a=document.activeElement;if(s.contains(a)&&a.closest('[data-p]'))return;
      if(!GROWK.includes(kind)&&b in U.lit)light(b,-1);
      if(kind==='team'){render('raci');render('steps')}
      if(kind==='cover')coverChanged();
      const before=JSON.stringify(S);clean(b);let changed=JSON.stringify(S)!==before;if(kind==='personas'&&U.popen!==null){U.popen=null;changed=true}
      if(changed){save();clampLit();render(b)}})});
  root.addEventListener('keydown',e=>{
    const dk=e.target.closest?.('.bf-dock');
    if(dk&&e.target===dk){const n=VIS().length;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();dockKey(dk,Math.max(0,Math.min(n-1,(dk._hot??0)+(e.key==='ArrowRight'?1:-1))))}
      if(e.key==='Enter'&&dk._hot!=null){e.preventDefault();const i=dk._hot;dockOff(dk);goBoard(i)}if(e.key==='Escape')dockOff(dk);return}
    if(e.target.closest?.('[data-dpf]')){if(e.key==='Enter'||e.key==='Escape'){e.preventDefault();e.target.blur()}return}
    if(e.target.closest?.('.tlb')&&tlKey(e))return;
    if(e.target.matches?.('.pers .zone')&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openZone(e.target);return}
    if(e.target.matches?.('[data-newowner]')&&e.key==='Enter'){e.preventDefault();const i=+e.target.dataset.newowner,n=t(e.target.textContent);if(!n)return;
      snap();S.steps[i].who=n;U.pick=null;save();render('steps');land(`[data-who="${i}"]`);ROOT.querySelector(`[data-who="${i}"]`)?.focus({preventScroll:true});say('steps',`${n} owns step ${n2(i)}.`);return}
    const gp=e.target.closest('.grip');
    if(gp&&/^Arrow/.test(e.key)){e.preventDefault();const l=gp.dataset.grip,i=+gp.dataset.i,arr=get(l);let to=l,ti=i;
      if(e.key==='ArrowUp')ti=Math.max(0,i-1);else if(e.key==='ArrowDown')ti=Math.min(arr.length-1,i+1);
      else{const g=group(l);if(g==='week'){const [k,dd]=l.split('.');let f=(k==='week2'?5:0)+ +dd+(e.key==='ArrowRight'?1:-1);const n=S.cadence===2?10:5;if(f<0||f>=n)return;to=(f>=5?'week2.':'week.')+(f%5);ti=get(to).length}
        else if(/\.a$/.test(g)){const [k,qi]=l.split('.');const n=+qi+(e.key==='ArrowRight'?1:-1);if(n<0||n>=S[k].length)return;to=`${k}.${n}.a`;ti=get(to).length}else return}
      if(to===l&&ti===i)return;moveItem(l,i,to,ti);ROOT.querySelector(`[data-grip="${to}"][data-i="${ti}"]`)?.focus();return}
    const f=e.target.closest('[data-p]');if(!f)return;const p=f.dataset.p,it=itemOf(p),b=f.closest('.bd').dataset.board,kind=KIND(b);
    if(e.key==='Escape'){f.blur();return}
    if(kind==='personas'){const m=p.match(/^pers\.(\d+)\.qs\.(\d+)\.a\.(\d+)$/);
      if(!m){if(e.key==='Enter'){e.preventDefault();f.blur();return}
        const pi=+p.split('.')[1];if(e.key==='Backspace'&&f.textContent===''&&S.pers.length>1&&!pdone(S.pers[pi])){e.preventDefault();snap();S.pers.splice(pi,1);U.psel=Math.max(0,pi-1);U.ptab=0;U.popen=null;save();render('pers');say('pers','Removed an audience.');focusField(`pers.${U.psel}.name`)}
        return}
      const [,i,j,k]=m.map(Number),list=S.pers[i].qs[j].a;
      if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();if(j===0){f.blur();return}snap();if(!list.length)list.push('');list.splice(k+1,0,'');save();U.popen=i+':'+j;render('pers');focusField(`pers.${i}.qs.${j}.a.${k+1}`);return}
      if(e.key==='Backspace'&&f.textContent===''&&list.length>1){e.preventDefault();list.splice(k,1);save();render('pers');focusField(`pers.${i}.qs.${j}.a.${Math.max(0,k-1)}`)}
      return}
    if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();if(!it){f.blur();return}
      snap();get(it.a).splice(it.i+1,0,listOf(it.a)());save();render(b);focusField(firstField(it.a,it.i+1));return}
    if(e.key==='Backspace'&&it&&f.textContent===''&&isPrimary(it.rest)){const item=get(it.a+'.'+it.i);if(item&&item.a&&item.a.some(t))return;
      e.preventDefault();snap();get(it.a).splice(it.i,1);save();clampLit();render(b);if(it.i>0)focusField(firstField(it.a,it.i-1))}});
  root.addEventListener('click',e=>{const ax=e.target.closest('.tl-axis');if(ax){tlAddMs(clamp(day7(tlX(e)*S.tl.n),0,S.tl.n));return}
    const btn=e.target.closest('button');if(!btn)return;const D=btn.dataset;
    if(btn.hasAttribute('data-undo')){undo();return}
    if(D.gear!==undefined){U.panel=!U.panel;renderPanel();return}
    if(D.dpclose!==undefined){U.panel=false;renderPanel();return}
    if(D.dpcol){const k=D.dpcol;U.col[k]=!U.col[k];const m=btn.closest('.dp-mod');m.classList.toggle('col',U.col[k]);btn.setAttribute('aria-expanded',String(!U.col[k]));return}
    if(D.dpsw){const [k,key]=D.dpsw.split(':'),on=btn.getAttribute('aria-checked')!=='true';
      if(k==='on'){if(on)delete S.off[key];else S.off[key]=true;save();renderAll();watch()}else{S.call[k]=on;save();refreshFeet()}renderPanel();return}
    if(D.dplen){if(D.dplen==='custom'){if(!S.call.custom){S.call.custom=true;renderPanel();ROOT.querySelector('[data-dpf="len"]')?.focus()}}else{S.call.custom=false;setLen(+D.dplen);save();refreshFeet();renderPanel()}return}
    if(D.dptheme){S.call.theme=D.dptheme;save();paintTheme();renderPanel();return}
    const rt=b=>{const f=sec(b)?.querySelector('.bf-right');if(f){f.firstElementChild.outerHTML=timeHTML(b);paintTmr()}};
    if(D.tadd){U.tmr[D.tadd]={pick:true};rt(D.tadd);sec(D.tadd).querySelector('.bf-chip')?.focus({preventScroll:true});return}
    if(D.tset){const x=+D.m*60;U.tmr[D.tset]={total:x,left:x,end:Date.now()+x*1000};rt(D.tset);sec(D.tset).querySelector(`[data-ttog]`)?.focus({preventScroll:true});return}
    if(D.ttog){const x=U.tmr[D.ttog];if(x.end){x.left=Math.max(0,(x.end-Date.now())/1000);x.end=null}else{if(!x.left)x.left=x.total;x.end=Date.now()+x.left*1000}paintTmr();return}
    if(D.treset){const x=U.tmr[D.treset];x.end=null;x.left=x.total;paintTmr();return}
    if(D.tx){delete U.tmr[D.tx];rt(D.tx);return}
    if(D.pace!==undefined){PACE.paused=!PACE.paused;paintPace();return}
    if(D.tlweeks){if(!btn.disabled)tlWeeks(+D.tlweeks);return}
    if(D.tladd){D.tladd==='phase'?tlAddPhase():tlAddMs(Math.ceil(S.tl.n/2));return}
    if(D.tlx){tlRemove(D.tlx,+D.i);return}
    if(btn.matches('.agenda .row')){const i=+D.i,k=btn.closest('.bd').dataset.board;light(k,U.lit[k]===i?-1:i);return}
    if(D.person!==undefined){if(U.dragged)return;const a=document.activeElement,c=a&&a.closest&&a.closest('.raci [data-cell]');
      if(c){const [i,k]=c.dataset.cell.split('.');addPerson(+i,k,D.person);return}
      if(U.arm===D.person){disarm();return}
      U.arm=D.person;const s=sec('raci');s.querySelectorAll('.chip.pp').forEach(x=>x.setAttribute('aria-pressed',String(x===btn)));s.querySelector('[data-spot]').classList.add('armed');s.querySelector('.tray').classList.add('on');return}
    if(D.cadence){setCadence(+D.cadence);return}
    if(D.qx){const k=D.qx,i=+D.i;snap();const q=S[k].splice(i,1)[0];save();clampLit();render(k);say(k,`Removed ${itemLabel(k,q)}.`);return}
    if(D.psel!==undefined){U.psel=+D.psel;U.ptab=0;U.popen=null;render('pers');return}
    if(D.ptab!==undefined){U.ptab=+D.ptab;U.popen=null;render('pers');return}
    if(D.padd!==undefined){snap();S.pers.push({name:'',qs:PQ().map(()=>({a:[]}))});U.psel=S.pers.length-1;U.ptab=0;U.popen=null;save();render('pers');say('pers','Added an audience.');focusField(`pers.${U.psel}.name`);return}
    if(D.add){const a=D.add,b=btn.closest('.bd').dataset.board;snap();const arr=get(a);arr.push(listOf(a)());save();render(b);focusField(firstField(a,arr.length-1));return}
    if(D.slot){placeTrait(+D.i,+D.slot);return}
    if(D.who){const i=+D.who;U.pick=U.pick===i?null:i;render('steps');ROOT.querySelector('.pk .chip')?.focus({preventScroll:true});return}
    if(D.owner!==undefined){const i=U.pick;snap();S.steps[i].who=D.owner;U.pick=null;save();render('steps');land(`[data-who="${i}"]`);ROOT.querySelector(`[data-who="${i}"]`)?.focus({preventScroll:true});say('steps',D.owner?`${D.owner} owns step ${n2(i)}.`:`Step ${n2(i)} has no owner.`);return}
  });
}
const editing=el=>el&&el.closest&&el.closest('[contenteditable],input,select,textarea');
document.addEventListener('keydown',e=>{if(!S||!ROOT)return;
  if((e.metaKey||e.ctrlKey)&&!e.shiftKey&&e.key.toLowerCase()==='z'&&!editing(e.target)){if(H.length){e.preventDefault();undo()}return}
  if(e.key==='Escape'){if(U.pick!==null){const i=U.pick;U.pick=null;render('steps');ROOT.querySelector(`[data-who="${i}"]`)?.focus({preventScroll:true});return}
    if(U.arm){disarm();return}
    for(const b in U.tmr)if(U.tmr[b].pick){delete U.tmr[b];const f=sec(b)?.querySelector('.bf-right');if(f)f.firstElementChild.outerHTML=timeHTML(b)}
    if(U.panel){U.panel=false;renderPanel()}return}
  /* presenting: the arrow keys and Page keys move a board at a time; F fills the screen */
  if(e.defaultPrevented||editing(e.target)||e.metaKey||e.ctrlKey||e.altKey||e.target.closest?.('.grip,.bf-dock,.tl-bar,.tl-dia,.tl-axis,.slot,.knob,.dp'))return;
  const step={ArrowRight:1,PageDown:1,ArrowLeft:-1,PageUp:-1}[e.key];
  if(step){const v=VIS(),i=v.indexOf(PACE.cur||v[0]);const j=clamp(i+step,0,v.length-1);if(j!==i){e.preventDefault();goBoard(j)}return}
  if(e.key==='f'||e.key==='F'){e.preventDefault();if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen?.()}});
document.addEventListener('click',e=>{if(U.pick!==null&&ROOT&&!e.target.closest('.pk,[data-who]')){U.pick=null;render('steps')}});
addEventListener('resize',()=>requestAnimationFrame(()=>{if(!S)return;clampKnobs();const s=sec('tl');if(s&&!s.hidden){const stk=tlStk();if(stk!==!!s.querySelector('.tl-wrap.stk'))render('tl');else{tlFit(s);tlPlace(s)}}}));

/* ── saving ──────────────────────────────────────────────────────────────
   Every change lands in localStorage at once, then goes to the server a moment later. The
   browser copy is marked dirty until the server confirms; on reopening, a dirty copy wins and
   is sent again, so a crash between the two loses nothing. The server keeps the deck it
   replaces in history/ whenever two copies disagree. */
const LK='workshop:'+WID;
let REV=null,DIRTY=false,dirtySince=0,GEN=0,inflight=false,failSince=0,lastOK=0,timer=null,PATH='';
function saveLocal(){try{localStorage.setItem(LK,JSON.stringify({base:REV,dirty:DIRTY,at:Date.now(),deck:S}))}catch(_){}}
function save(){S.pace=PACE.t;GEN++;if(!DIRTY)dirtySince=Date.now();DIRTY=true;saveLocal();schedule(400)}
function keep(){S.pace=PACE.t;GEN++;if(!DIRTY)dirtySince=Date.now();DIRTY=true;saveLocal();schedule(2000)}   /* position and clock: no hurry */
function schedule(ms){clearTimeout(timer);timer=setTimeout(flush,ms)}
async function flush(){if(!DIRTY)return;if(inflight){schedule(300);return}inflight=true;const g=GEN;
  try{const r=await fetch(API,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({base:REV,deck:S})});
    if(!r.ok)throw new Error(r.status);const j=await r.json();REV=j.rev;S.rev=j.rev;lastOK=Date.now();failSince=0;if(g===GEN)DIRTY=false;saveLocal()}
  catch(_){if(!failSince)failSince=Date.now();schedule(Math.min(15000,1500+(Date.now()-failSince)/4))}
  finally{inflight=false;paintSave()}}
function saveNote(){if(failSince)return `<span class="off"><b>Not reaching the server.</b> Every answer is kept in this browser and goes to disk as soon as the server is back. Run <code>python3 brain/workshop.py serve</code>.</span>`;
  const when=lastOK?new Date(lastOK).toLocaleTimeString([], {hour:'numeric',minute:'2-digit'}):'';
  return `Every answer saves as you type to <b>${esc(PATH||'brain/workshops/'+WID+'/deck.json')}</b>${when?`, last at ${when}`:''}.`}
function paintSave(){if(!ROOT)return;const off=failSince&&Date.now()-failSince>2500;
  const v=off?'Not saved to disk · kept in this browser':DIRTY&&Date.now()-dirtySince>6000?'Saving…':'';
  ROOT.querySelectorAll('[data-save]').forEach(el=>{if(el.textContent!==v)el.textContent=v;el.classList.toggle('off',!!off)});
  const n=ROOT.querySelector('[data-dpsave]');if(n){const h=saveNote();if(n.innerHTML!==h)n.innerHTML=h}}
addEventListener('online',()=>schedule(0));
addEventListener('pagehide',()=>{if(DIRTY){saveLocal();try{fetch(API,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({base:REV,deck:S}),keepalive:true}).catch(()=>{})}catch(_){}}});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&DIRTY){saveLocal();flush()}});

function fail(msg){document.querySelector('.fw').innerHTML=`<p class="boot">${msg}</p>`}
async function boot(){
  let server=null,local=null;
  try{const r=await fetch(API,{cache:'no-store'});if(r.status===404){fail('There is no workshop at this address. <a href="/">All workshops</a>');return}if(r.ok)server=await r.json()}catch(_){}
  try{local=JSON.parse(localStorage.getItem(LK))}catch(_){}
  if(server){S=server.deck;REV=server.rev;PATH=server.path;lastOK=Date.now();
    if(local&&local.dirty&&local.deck){S=local.deck;REV=local.base??REV;DIRTY=true;schedule(200)}}
  else if(local&&local.deck){S=local.deck;REV=local.base;DIRTY=!!local.dirty;failSince=Date.now()-3000;schedule(1500)}
  else{fail('The workshop server is not answering, and this browser holds no copy of this workshop yet. Start it with <code>python3 brain/workshop.py serve</code>, then refresh.');return}
  S.off=S.off||{};S.mins=S.mins||{};S.call=Object.assign({tk:false,len:60,start:600,tod:true,tz:'',theme:'light'},S.call||{});
  PACE.t=Object.assign({},S.pace||{});document.title=t(S.cover.title)||'Workshop';
  resetLit();U.col={boards:true,client:true,call:true,sched:true,look:true};
  ROOT=document.querySelector('.fw');
  ROOT.innerHTML=S.boards.map(d=>`<section class="bd ${CLS[d.kind]||d.kind}" data-board="${d.key}" data-kind="${d.kind}" aria-label="${esc(d.name)}"></section>`).join('');
  wire(ROOT);renderAll();const ag=sec('agenda');if(ag)ag.dataset.enter='wait';
  const at=S.at&&!S.off[S.at]&&sec(S.at);if(at&&KIND(S.at)!=='cover'){U.entered.agenda=KIND(S.at)!=='agenda';if(ag&&U.entered.agenda)ag.dataset.enter='';at.scrollIntoView({block:'start'})}
  watch();paintSave();
  document.fonts?.ready.then(()=>{const s=sec('tl');if(s&&!s.hidden){tlFit(s);tlPlace(s)}clampKnobs()});
}
boot();
