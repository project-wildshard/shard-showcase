const el=id=>document.getElementById(id);
function node(tag,str,parent){const n=document.createElement(tag);if(str)n.textContent=str;if(parent)parent.append(n);return n}
function options(id,vals){new Set(vals).forEach(v=>{const o=node('option',v,el(id));o.value=v})}
for(const a of DATA.assets.filter(a=>a.concept)){
 const c=node('article','',el('boards'));c.className='concept';
 if(ConceptAngles.available(a)){
  ConceptAngles.render(c,a);
 }else{
  const l=node('a','',c);l.href=a.concept;const i=node('img','',l);i.src=a.concept;i.alt=a.name+' concept board';i.loading='lazy';
 }
 const t=node('div','',c);t.className='angle-meta';node('h3',a.name,t);node('p',a.id,t);if(a.concept_caption)node('p',a.concept_caption,t);
 if(ConceptAngles.available(a))ConceptAngles.boardLink(t,a);
}
ConceptAngles.mountRails();
options('types',DATA.assets.map(x=>x.class));
function rows(reveal){const q=el('query').value.trim().toLowerCase(), t=el('types').value; const list=DATA.assets.filter(a=>a.id===reveal||((!t||a.class===t)&&[a.id,a.name,a.evidence,a.reuse_or_open_edge].join(' ').toLowerCase().includes(q)));el('hits').textContent=list.length+' matching entries';const f=document.createDocumentFragment();for(const a of list){const d=node('details','',f);d.className='row';d.id='asset-'+a.id;const s=node('summary','',d);node('span',a.id,s);node('strong',a.name,s);node('p',[a.class,a.priority,a.status.replaceAll('-',' ')].join(' · '),d);node('p','Evidence: '+a.evidence,d);node('p',a.reuse_or_open_edge,d);if(ConceptAngles.available(a))ConceptAngles.rowButton(d,a);if(a.concept){const l=node('a','View concept board',d);l.href=a.concept}if(a.plan_studies){const line=node('p','',d);const l=node('a','View the three illustrated plan studies',line);l.href=a.plan_studies}if(a.reference_preview){const line=node('p','',d);const l=node('a','View original reference and observations',line);l.href=a.reference_preview}if(a.model_preview){const line=node('p','',d);const l=node('a','View Blender art candidate',line);l.href=a.model_preview}}el('rows').replaceChildren(f)}
el('query').addEventListener('input',rows);el('types').addEventListener('change',rows);rows();
options('groups',DATA.refs.map(r=>r.cat));let shown=0;
function refs(reset){if(reset){shown=0;el('thumbs').replaceChildren()}const pick=el('groups').value;const list=DATA.refs.filter(r=>!pick||r.cat===pick);for(const r of list.slice(shown,shown+30)){const a=node('button','',el('thumbs'));a.type='button';a.addEventListener('click',()=>detail(r));const i=node('img','',a);i.src=r.img;i.loading='lazy';i.alt=r.name;node('small',r.name+' · '+r.cat,a)}shown+=30;el('more').hidden=shown>=list.length}
el('groups').addEventListener('change',()=>refs(true));el('more').addEventListener('click',()=>refs(false));refs(true);

function detail(r){
 const w=el('detail-body');w.replaceChildren();const h=node('h3',r.scene||r.name,w);h.id='detail-title';
 const i=node('img','',w);i.src=r.img;i.alt=r.name;node('p',r.name+' · '+r.cat+' · '+r.visibility.replaceAll('-',' '),w);
 if(r.notes)node('p',r.notes,w);
 const list=node('ul','',w);
 if(!r.observations.length)node('li','No asset observations recorded for this image.',list);
 for(const o of r.observations){const li=node('li','',list);node('strong',o.label+' · ',li);
  function assetLink(id,prefix){const l=node('a',prefix+id,li);l.href='#asset-'+id;l.onclick=e=>{e.preventDefault();el('detail').close();go('asset-'+id,true);};}
  if(o.review_label)node('span',o.review_label,li).className='review-label';
  if(o.asset_id)assetLink(o.asset_id,o.mapping_status.startsWith('grey-proxy')?'Gray proxy for ':'');
  if(o.candidate_asset_ids?.length){const label=o.mapping_status.startsWith('grey-proxy')?'Tentative gray proxy links:':'Tentative matches:';node('div',label,li);for(const id of o.candidate_asset_ids){assetLink(id,'');li.append(document.createTextNode('  '));}}
  else if(!o.asset_id&&!o.review_label)node('span','No asset ID assigned',li);
  if(o.review_label)node('div',[o.evidence_region,o.review_note].filter(Boolean).join(' · '),li).className='review-note';
  else node('div',[o.evidence_region,o.certainty,o.mapping_status,o.link_confidence,o.reuse_hint,o.unmapped_reason].filter(Boolean).join(' · '),li);
  if(o.catalog_crosswalk)node('div',o.catalog_crosswalk,li);
 }
 const link=node('a','Open original on GitHub',w);link.href=r.url;if(!el('detail').open)el('detail').showModal();
}

const tabs=['assets','blender','originals'];
const aliases={'stall-revision':'awning'};
const refKeys=new Map(DATA.refs.map(r=>['reference-'+r.img.split('/').at(-1).replace(/\.webp$/,''),r]));
el('detail').addEventListener('close',()=>{if(refKeys.has(location.hash.slice(1)))history.replaceState(null,'','#originals');});
function route(key,focus=false){
 ConceptAngles.close();
 key=aliases[key]||key;
 if(key.startsWith('asset-'))rows(key.slice(6));
 const ref=refKeys.get(key),target=el(key),panel=ref?'originals':target?.closest('[role=tabpanel]')?.id||'assets';
 if(!ref&&el('detail').open)el('detail').close();
 for(const name of tabs){const active=name===panel, tab=el('tab-'+name);tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;el(name).hidden=!active;}
 if(ref)detail(ref);
 if(target&&!tabs.includes(key)){if(target.matches('details'))target.open=true;target.scrollIntoView({block:'start'});if(focus)target.querySelector('summary')?.focus({preventScroll:true});}
}
function go(key,focus){if(location.hash!=='#'+key)history.pushState(null,'','#'+key);route(key,focus);}
function fromHash(){route(location.hash.slice(1)||'assets');}
tabs.forEach((name,i)=>{const t=el('tab-'+name);t.onclick=()=>go(name);t.onkeydown=e=>{const n={ArrowRight:(i+1)%3,ArrowLeft:(i+2)%3,Home:0,End:2}[e.key];if(n===undefined)return;e.preventDefault();go(tabs[n]);el('tab-'+tabs[n]).focus();};});
addEventListener('hashchange',fromHash);addEventListener('popstate',fromHash);fromHash();
