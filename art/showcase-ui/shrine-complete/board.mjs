import {example,route} from './model.mjs'
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')
const blue='#a6e8f3', pale='#e8edf1', amber='#ffd89b', muted='#b5cbd3'
const t=(x,y,s,{n=12,f=pale,k=0,b=400,align='start',mono=true}={})=>
  `<text x="${x}" y="${y}" fill="${f}" font-family="${mono?'DejaVu Sans Mono':'DejaVu Sans'}" font-size="${n}" font-weight="${b}" letter-spacing="${k}" text-anchor="${align}">${esc(s)}</text>`
const mid=(y,s,o={})=>t(201,y,s,{...o,align:'middle'})
const line=(x,y,u,v,color='#3a5866')=>`<path d="M${x} ${y}L${u} ${v}" stroke="${color}"/>`
const box=(x,y,w,h,fill,stroke='none',r=2)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}"/>`
const shell=(x,y,w,h)=>box(x,y,w,h,'url(#panel)','#507782')+
  `<path d="M${x} ${y+16}v-16h16m${w-32} 0h16v16m0 ${h-32}v16h-16m-${w-32} 0h-16v-16" fill="none" stroke="${blue}" stroke-width="1.2"/>`
function complete(){
 let s=shell(18,219,366,476)
 s+=mid(251,'THE TRAINING VAULT · WARDEN DOWN',{n:9.1,k:2,f:blue})
 s+=mid(293,'TRAINING VAULT',{n:30,k:1.9,b:700,mono:false})
 s+=mid(323,'·  SHRINE COMPLETE  ·',{n:13,k:2.8,b:700,f:amber})
 s+=mid(368,'Solved puzzles stay solved. The chest is open.',{n:10.4})
 s+=line(38,390,364,390)
 const rows=[['TIME',example.time],['BEST',example.best],['DEATHS',example.deaths],
              ['ROOMS',example.rooms],['CHEST',example.scrip,example.core],['TROPHY',...example.trophy.split(' ')]]
 for(const [i,[label,v,sub]] of rows.entries()){
   const x=39+(i%3)*112,y=i<3?416:479
   s+=t(x,y,label,{n:8.2,k:1.6,f:blue})+t(x,y+21,v,{n:i%3===1?13.2:15,b:700,mono:false})
   if(sub)s+=t(x,y+38,sub,{n:12.5,b:700,mono:false})
 }
 s+=line(38,527,364,527)
 s+=box(39,544,324,55,'#1e4252','#9edceb',3)
 s+=`<path d="M39 557v-13h14m296 55h14v-13" fill="none" stroke="#e7f6ff" stroke-width="2"/>`
 s+=mid(577,'CONTINUE  ›',{n:15,k:3.3,b:700})
 s+=mid(626,'The exit portal is open behind the chest.',{n:10.4})+
    mid(648,'Walk through it to leave.',{n:10.7})+
    mid(666,'Walk back in to run it again.',{n:10.7})
 return s
}

function portal(state){
 const [x,y]=route[state.position]
 let s=shell(18,281,366,373)
 const status={
   vault:['EXIT PORTAL OPEN','WALK PAST THE CHEST'],
   outside:['OUTSIDE THE VAULT','WALK BACK THROUGH TO RERUN'],
   newRun:['NEW RUN','PORTAL RE-ENTERED'],
 }[state.place]
 s+=mid(311,status[0],{n:13,k:2.1,b:700,f:blue})+
    mid(332,status[1],{n:8.6,k:1.45,f:muted})
 s+=`<path d="M258 352H97V620H306V352Z" fill="#122631" stroke="#3b5460"/>
      <path d="M103 382h196" stroke="#496875" stroke-dasharray="2 5"/>
      <path d="M175 383v-10q0-23 26-23t26 23v10" fill="none" stroke="#9be4ed" stroke-width="3"/>
      <path d="M175 383h52" stroke="#a8e2e9" stroke-width="2"/>
      <path d="M${route.map(p=>p.join(' ')).join(' L')}" fill="none" stroke="#6bacb8" stroke-width="2" stroke-dasharray="4 6"/>
      <path d="M186 474l12-8h35l11 8v21h-58z" fill="#58412c" stroke="#d9a978" stroke-width="1.2"/>
      <path d="M186 474l10-10h37l11 10m-33 6h8v7h-8z" fill="none" stroke="#ffc980"/> `
 s+=t(237,374,'THRESHOLD',{n:7.5,k:.7,f:blue})+t(244,515,'CHEST',{n:8,k:.8,f:amber})
 s+=`<circle cx="${x}" cy="${y}" r="10" fill="#18363e" stroke="#b1f0df" stroke-width="2"/>
      <path d="M${x-4} ${y+3}l4-7 4 7z" fill="#b1f0df"/>`
 s+=mid(641,`STUDY RUN ${state.runs} · PATH NOT TO SCALE`,{n:8.3,k:1,f:muted})
 return s
}

export function board(state,background){
 const label=state.card?'Shrine completion card showing time, rooms, deaths and rewards':`Walk diagram: ${state.place}, sample run ${state.runs}`
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 402 874" width="402" height="874" role="img" aria-label="${esc(label)}">
 <defs><linearGradient id="shade" x1="0" x2="0" y1="0" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#08131f" stop-opacity=".44"/><stop offset=".51" stop-color="#081520" stop-opacity=".17"/><stop offset="1" stop-color="#051018" stop-opacity=".92"/></linearGradient>
 <linearGradient id="panel" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#102630" stop-opacity=".97"/><stop offset="1" stop-color="#10222d" stop-opacity=".96"/></linearGradient></defs>
 <rect width="402" height="874" fill="#111f2a"/>
 <image href="${esc(background)}" x="0" y="0" width="402" height="874" preserveAspectRatio="xMidYMid slice"/>
 <rect width="402" height="874" fill="url(#shade)"/>
 ${mid(57,'W I L D S H A R D   /   V A U L T',{n:9.1,f:blue,b:700})}
 ${box(161,83,80,1,'#79a7af')}
 ${state.card?complete():portal(state)}
 ${mid(815,'UI-30 · PORTRAIT REVIEW',{n:8.2,k:2.1,f:blue})}
 ${mid(837,'ILLUSTRATIVE · NOT THE LIVE GAME',{n:8,k:1.25,f:muted})}
 </svg>`
}
