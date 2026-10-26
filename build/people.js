// ---------- people & citations ----------
const SRC=D.src||{};
const KIND={birth:'Born',study:'Studied',teach:'Taught',office:'Office',travel:'Travel',exile:'Exile',research:'Research',death:'Died'};
const kc=k=>`var(--k-${k})`;
const PP={}; (D.people||[]).forEach(p=>{PP[p.id]=p;p.st_=[];});
(D.people||[]).forEach(p=>p.te.forEach(t=>{if(PP[t.id])PP[t.id].st_.push({id:p.id,i:t.i,pl:t.pl,f:t.f,to:t.to,k:t.k,src:t.src})}));
const lifeTxt=p=>{const b=p.b!=null?yfmt(p.b,p.ba):'',dd=p.d!=null?yfmt(p.d,p.da):'';return (b||dd)?`${b||'?'}–${dd||'?'}`:(p.stops.length?`active ${p.stops[0].f}`:'')};
// residency -> person
D.th.forEach(t=>{if(t.p&&PP[t.p])t.person=t.p});
S.person=null; S.linT=true; S.linS=true;

// citation numbering for one panel
function Cites(){const order=[],idx={};
  return {ref(list){const ns=(list||[]).filter(s=>SRC[s]).map(s=>{if(!(s in idx)){idx[s]=order.length+1;order.push(s)}return idx[s]});
      return ns.length?`<sup class="c">${ns.map(n=>`<a href="#src-${n}" data-cite="${n}">[${n}]</a>`).join('')}</sup>`:''},
    list(){return order.length?`<ol class="srcs">${order.map((s,n)=>{const o=SRC[s];return `<li id="src-${n+1}">${esc(o.t)}${o.p?`, <i>${esc(o.p)}</i>`:''}. <a href="${esc(o.u)}" target="_blank" rel="noopener">${esc(o.u.replace(/^https?:\/\/(www\.)?/,'').slice(0,70))}</a></li>`}).join('')}</ol>`:'<p class="note">No sources attached yet.</p>'}}}
const stTag=s=>s&&s!=='confirmed'?`<span class="st ${s}">${s==='doubtful'?'disputed':s}</span>`:'';
document.addEventListener('click',ev=>{const a=ev.target.closest('a[data-cite]');if(!a)return;ev.preventDefault();
  const pane=a.closest('.detail');const li=pane&&pane.querySelector('#src-'+a.dataset.cite);if(li){li.scrollIntoView({block:'center',behavior:'smooth'});li.style.background='var(--accent-soft)';setTimeout(()=>li.style.background='',1600)}});

// ---------- map drawing for the selected person ----------
const pplG=$('#ppl');
function personRoute(p){return p.stops.filter(s=>s.x!=null)}
function renderPerson(){
  pplG.innerHTML=''; svg.classList.toggle('pmode',!!S.person);
  if(!S.person)return;
  const p=PP[S.person], y=S.year, r=5.2*U;
  const curve=(a,b,bend=0.18)=>{const mx=(a.x+b.x)/2,my=(a.y+b.y)/2,dx=b.x-a.x,dy=b.y-a.y;return `M${a.x},${a.y}Q${mx-dy*bend},${my+dx*bend} ${b.x},${b.y}`};
  // lineage routes
  const lin=(ids,cls)=>ids.forEach(id=>{const q=PP[id];if(!q)return;const st=personRoute(q);if(!st.length)return;
    for(let n=1;n<st.length;n++){if(st[n].x===st[n-1].x&&st[n].y===st[n-1].y)continue;el('path',{class:'lpath '+cls,d:curve(st[n-1],st[n],0.12)},pplG)}
    const seen=new Set();st.forEach(s=>{const k=s.x+','+s.y;if(seen.has(k))return;seen.add(k);el('circle',{class:'ldot '+cls,cx:s.x,cy:s.y,r:r*0.45},pplG)});
    const last=st[st.length-1];el('text',{class:'llbl '+cls,x:last.x+r*0.8,y:last.y-r*0.6,'font-size':10.5*U},pplG).textContent=q.n;});
  if(S.linT)lin([...new Set(p.te.map(t=>t.id))],'t');
  if(S.linS)lin([...new Set(p.st_.map(t=>t.id))],'s');
  const st=personRoute(p); if(!st.length)return;
  for(let n=1;n<st.length;n++){const a=st[n-1],b=st[n];if(a.x===b.x&&a.y===b.y)continue;
    el('path',{class:'ppath'+(b.f>y?' later':''),d:curve(a,b),'marker-end':b.f>y?'':'url(#parrow)'},pplG)}
  // group stops at the same place
  const groups=[];st.forEach((s,n)=>{let g=groups.find(g=>Math.hypot(g.x-s.x,g.y-s.y)<0.5*r);if(!g){g={x:s.x,y:s.y,items:[]};groups.push(g)}g.items.push({s,n:n+1})});
  groups.forEach(g=>{const first=g.items[0].s, later=first.f>y;
    const c=el('circle',{class:'pstop'+(later?' later':''),cx:g.x,cy:g.y,r:r*(g.items.length>1?1.25:1),fill:kc(first.k)},pplG);
    c.addEventListener('click',ev=>{ev.stopPropagation();setPlaying(false);setYear(first.f)});
    const nums=g.items.map(i=>i.n).join(',');
    el('text',{class:'pnum',x:g.x,y:g.y+r*0.36,'font-size':(nums.length>3?6.5:8.5)*U},pplG).textContent=nums.length>5?g.items[0].n+'…':nums;
    const lbl=[...new Set(g.items.map(i=>i.s.i?I[i.s.i].L[0].c:i.s.pl))][0]||first.pl;
    el('text',{class:'plbl'+(later?' later':''),x:g.x+r*1.5,y:g.y+r*0.4,'font-size':11*U},pplG).textContent=`${lbl} ${g.items[0].s.f}`;});
}

// ---------- people list ----------
const plist=$('#plist');
function buildPeopleList(){
  const s=norm($('#pq').value.trim()), linked=$('#plinked').checked;
  const rows=(D.people||[]).filter(p=>(!s||norm(p.n).includes(s)||(p.fl||[]).some(f=>norm(f).includes(s)))&&(!linked||p.te.length||p.st_.length));
  plist.innerHTML=rows.length?rows.slice(0,400).map(p=>{const where=[...new Set(p.stops.filter(x=>x.i).map(x=>I[x.i].L[0].c))].slice(0,4).join(' · ');
    const lin=(p.te.length||p.st_.length)?`<span class="lin"> · ${p.te.length} teacher${p.te.length===1?'':'s'}, ${p.st_.length} student${p.st_.length===1?'':'s'}</span>`:'';
    return `<button class="prow" data-p="${p.id}"><span class="nm">${esc(p.n)}</span><span class="ys">${lifeTxt(p)}</span><span class="sub">${esc(where)}${lin}</span></button>`}).join('')+(rows.length>400?`<div class="empty">${rows.length-400} more; refine the search.</div>`:'')
  :'<div class="empty">No people match.</div>';
}
$('#pq').addEventListener('input',buildPeopleList);
$('#plinked').addEventListener('change',buildPeopleList);
plist.addEventListener('click',ev=>{const b=ev.target.closest('[data-p]');if(b)selectPerson(b.dataset.p)});

// ---------- person detail ----------
function selectPerson(id,opt={}){
  setPlaying(false);
  S.person=id||null;
  if(!id){$('#pdetail').hidden=true;$('#plistwrap').hidden=false;renderPerson();render();drawTimeline();return}
  if(S.sel){S.sel=null;S.selEv=null;markLog()}
  try{history.replaceState(null,'','#p-'+id)}catch(e){}
  const p=PP[id]; tab('ppl'); $('#plistwrap').hidden=true; const box=$('#pdetail'); box.hidden=false;
  personDetail(p);
  const st=personRoute(p);
  if(st.length&&opt.year!==false){const last=st[st.length-1].f; if(S.year<st[0].f||S.year>last+5)S.year=Math.min(T1,Math.max(T0,(p.d??last)))}
  if(st.length){let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;st.forEach(s=>{x0=Math.min(x0,s.x);y0=Math.min(y0,s.y);x1=Math.max(x1,s.x);y1=Math.max(y1,s.y)});
    const pad=60,r=wrap.getBoundingClientRect(),ar=r.width/Math.max(1,r.height);let w=Math.max(260,x1-x0+pad*2),h=Math.max(200,y1-y0+pad*2);if(w/h<ar)w=h*ar;else h=w/ar;
    S.view={x:(x0+x1)/2-w/2,y:(y0+y1)/2-h/2,w,h};}
  applyView(); drawTimeline();
}
function lineageSvg(p){
  const up1=[...new Set(p.te.map(t=>t.id))].filter(x=>PP[x]).slice(0,6);
  const up2=[...new Set(up1.flatMap(x=>PP[x].te.map(t=>t.id)))].filter(x=>PP[x]&&x!==p.id&&!up1.includes(x)).slice(0,6);
  const dn1=[...new Set(p.st_.map(t=>t.id))].filter(x=>PP[x]).slice(0,6);
  const dn2=[...new Set(dn1.flatMap(x=>PP[x].st_.map(t=>t.id)))].filter(x=>PP[x]&&x!==p.id&&!dn1.includes(x)).slice(0,6);
  if(!up1.length&&!dn1.length)return '<p class="note">No teacher or student links recorded yet.</p>';
  const rows=[up2,up1,[p.id],dn1,dn2].filter((r,n)=>r.length||n===2);
  const labels=[];if(up2.length)labels.push('Their teachers');if(up1.length)labels.push('Teachers');labels.push('');if(dn1.length)labels.push('Students');if(dn2.length)labels.push('Their students');
  const W2=360,RH=46,H2=rows.length*RH+8,pos={};
  rows.forEach((r,ri)=>{const n=r.length,cw=Math.min(118,(W2-20)/n);r.forEach((id,k)=>{pos[id]={x:W2/2+(k-(n-1)/2)*cw,y:ri*RH+26,w:cw-8}})});
  let s=`<svg class="lineage" viewBox="0 0 ${W2} ${H2}" role="img" aria-label="Teachers and students">`;
  const edge=(a,b)=>{if(!pos[a]||!pos[b])return '';const A=pos[a],B=pos[b];return `<path class="edge" d="M${A.x},${A.y+11}C${A.x},${(A.y+B.y)/2} ${B.x},${(A.y+B.y)/2} ${B.x},${B.y-11}"/>`};
  (D.people||[]).forEach(q=>q.te.forEach(t=>{if(pos[q.id]&&pos[t.id]&&pos[t.id].y<pos[q.id].y)s+=edge(t.id,q.id)}));
  rows.forEach((r,ri)=>{if(labels[ri])s+=`<text class="rowlbl" x="2" y="${ri*RH+6}">${labels[ri].toUpperCase()}</text>`});
  Object.entries(pos).forEach(([id,o])=>{const q=PP[id],nm=q.n.length*5.6>o.w?q.n.split(' ').slice(-1)[0]:q.n;
    s+=`<g class="node${id===p.id?' me':''}" data-p="${id}"><title>${esc(q.n)} ${lifeTxt(q)}</title><rect x="${o.x-o.w/2}" y="${o.y-11}" width="${o.w}" height="22" rx="11"/><text x="${o.x}" y="${o.y}">${esc(nm)}</text></g>`});
  return s+'</svg>';
}
function personDetail(p){
  const C=Cites(), y=S.year;
  const relRow=(r,who)=>{const q=PP[r.id];const where=r.i?`<button class="lnk" data-sel="${r.i}">${esc(I[r.i].n)}</button>`:esc(r.pl||'');
    const yrs=r.f?(r.to&&r.to!==r.f?`${r.f}–${r.to}`:r.f):'';
    return `<div class="rel"><button class="lnk" data-p="${r.id}">${esc(q.n)}</button> <span class="where">${lifeTxt(q)}</span>${C.ref(r.src)}<br><span class="where">${esc(r.k||who)}${where?' · '+where:''}${yrs?' · '+yrs:''}</span></div>`};
  const stops=personRoute(p).map((s,n)=>`<div class="stop${s.f>y?' later':''}" data-y="${s.f}"><span class="kdot" style="background:${kc(s.k)}">${n+1}</span><span class="yr ${s.a?'ap':''}">${yfmt(s.f,s.a)}${s.to&&s.to!==s.f?'–'+s.to:''}</span><span><span class="kd" style="color:${kc(s.k)}">${KIND[s.k]||s.k}</span> · <span class="pl">${s.i?`<button class="lnk" data-sel="${s.i}">${esc(I[s.i].n)}</button>`:esc(s.pl)}</span>${C.ref(s.src)}</span>${s.no?`<span class="no">${esc(s.no)}</span>`:''}</div>`).join('');
  const kinds=[...new Set(personRoute(p).map(s=>s.k))];
  $('#pdetail').innerHTML=`
    <div class="dhead"><button class="xbtn" id="pback">← All people</button><button class="xbtn" id="pclose">Close</button></div>
    <h2>${esc(p.n)}</h2>
    <div class="alt">${lifeTxt(p)}${(p.fl||[]).length?' · '+p.fl.map(esc).join(', '):''}</div>
    ${p.bio?`<p style="margin-top:10px">${esc(p.bio)}${C.ref(p.src)}</p>`:''}
    ${p.fallback?'<p class="note">This route is built from residencies alone. A sourced life path has not been added yet.</p>':''}
    <h3 class="eyebrow">Teachers and students</h3>
    ${lineageSvg(p)}
    <div class="lintog"><label><input type="checkbox" id="linT" ${S.linT?'checked':''}><span class="sw" style="border-color:var(--lin-teacher)"></span>Teachers’ routes</label><label><input type="checkbox" id="linS" ${S.linS?'checked':''}><span class="sw" style="border-color:var(--lin-student)"></span>Students’ routes</label></div>
    <h3 class="eyebrow">Route · ${personRoute(p).length} stops</h3>
    <div class="legend-k">${kinds.map(k=>`<span><i style="background:${kc(k)}"></i>${KIND[k]}</span>`).join('')}</div>
    ${stops||'<p class="note">No stops recorded.</p>'}
    ${p.te.length?`<h3 class="eyebrow">Studied under</h3>${p.te.map(r=>relRow(r,'teacher')).join('')}`:''}
    ${p.st_.length?`<h3 class="eyebrow">Students</h3>${p.st_.map(r=>relRow(r,'student')).join('')}`:''}
    <h3 class="eyebrow">Sources</h3>${C.list()}`;
  $('#pdetail').scrollTop=0;
  $('#pback').onclick=()=>{selectPerson(null);tab('ppl')};
  $('#pclose').onclick=()=>{selectPerson(null);fit()};
  $('#linT').onchange=e=>{S.linT=e.target.checked;renderPerson()};
  $('#linS').onchange=e=>{S.linS=e.target.checked;renderPerson()};
}
$('#pdetail').addEventListener('click',ev=>{
  const pn=ev.target.closest('[data-p]'); if(pn){ev.stopPropagation();selectPerson(pn.dataset.p);return}
  const s=ev.target.closest('[data-sel]'); if(s){ev.stopPropagation();selectPerson(null);goTo(s.dataset.sel);return}
  const st=ev.target.closest('.stop'); if(st){setPlaying(false);setYear(+st.dataset.y)}
});
function verificationSummary(){
  const c={confirmed:0,corrected:0,unverified:0,doubtful:0,unchecked:0};D.ev.forEach(e=>{c[e.st||'unchecked']=(c[e.st||'unchecked']||0)+1});
  const n=D.ev.length,seg=(k,v)=>c[k]?`<span style="width:${c[k]/n*100}%;background:${v}" title="${k} ${c[k]}"></span>`:'';
  $('#vstats').innerHTML=`<div class="vbar">${seg('confirmed','var(--ev-founding)')}${seg('corrected','var(--ev-reform)')}${seg('doubtful','var(--ev-suppression)')}${seg('unverified','var(--faint)')}</div>
  <p class="vnote">Events: ${c.confirmed} confirmed, ${c.corrected} corrected, ${c.doubtful} disputed, ${c.unverified} unverified${c.unchecked?`, ${c.unchecked} not yet checked`:''}. ${Object.keys(SRC).length} sources.</p>`;
}
