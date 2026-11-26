import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';

const [rp,out]=process.argv.slice(2);
const {gantry,rings,clean,bypass}=JSON.parse(readFileSync(rp));
const green='#8fe0bb', gold='#f1b86d', soft='#8cabb2', ink='#eef5ee', blue='#a9dceb';
const text=(x,y,s,n=20,c=ink,opt='')=>`<text x="${x}" y="${y}" fill="${c}" font-size="${n}" font-family="DejaVu Sans" ${opt}>${s}</text>`;
const panel=(x,y,w,h,c='#13262e',stroke='#2e4850',r=16)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${c}" stroke="${stroke}"/>`;
const path=(d,c='#395761',w=1,dash='')=>`<path d="${d}" stroke="${c}" fill="none" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;
const fmt=(n,d=3)=>Number(n).toFixed(d);
const circle=(x,y,r,c,stroke='#12222b')=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${c}" stroke="${stroke}" stroke-width="2"/>`;
const bold='font-weight="700"';
const middle='text-anchor="middle"';
function trace(run,xy,opt={}){
  const {stride=3,filter=()=>true}=opt;
  return run.trace.filter((p,i)=>i%stride===0&&filter(p)).map((p,i)=>`${i===0?'M':'L'}${xy(p.x,p.z).map(v=>fmt(v,2)).join(',')}`).join(' ');
}
function heading(title,sub){
  return text(49,56,'W10b  /  WEST RIDING OVAL',16,blue,bold)+text(48,104,title,39,ink,bold)+text(49,136,sub,18,soft);
}
const wrap=(label,contents)=>`<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760"><title>${label}</title><rect width="1280" height="760" fill="#0c1a21"/>${contents}</svg>\n`;
const view=(x,z)=>[640+(x+122)*5.05,392+(z+186)*5.05];
const xy=(x,z)=>view(x,z).join(',');
const [xa,ya]=view(-182,-148), [xb,yb]=view(-62,-224);
const oval=`M${xa},${ya}H${xb}A191.9,191.9 0 0 0 ${xb},${yb}H${xa}A191.9,191.9 0 0 0 ${xa},${ya}Z`;
let map=heading('One complete lap, eight crossings','Stock mounted movement, measured against the unchanged oval and ring centres.');
map+=path(oval,'#263d42',61)+path(oval,'#617d80',1.6,'7 10');
map+=path(trace(clean,view),green,4);
for(const ring of rings){
  const [x,y]=view(...ring.at);
  const [dx,dz]=ring.tangent;
  map+=path(`M${x+dz*10},${y-dx*10}L${x-dz*10},${y+dx*10}`,blue,2.5);
  map+=circle(x,y,17,'#224b4f',green)+text(x,y+6,String(ring.id),16,ink,middle+' '+bold);
}
const [sx,sy]=view(...gantry.at);
map+=path(`M${sx},${sy-30}V${sy+30}`,gold,4)+text(sx,sy+52,'START / FINISH',13,gold,middle+' '+bold);
map+=path('M691 571l-12 12 12 12 M561 189l12 12-12 12',green,4);
map+=text(640,364,'478.8 m',49,ink,middle+' '+bold)+text(640,397,'AUTHORED CENTRELINE',15,soft,middle);
map+=text(640,457,fmt(clean.result.total)+' s',34,green,middle+' '+bold)+text(640,486,'MEASURED CLEAN LAP',15,soft,middle);
map+=panel(48,657,1184,63)+text(71,695,'All eight ring planes hit in the westbound order: 2 → 1 → 8 → 7 → 6 → 5 → 4 → 3',19,ink);
map+=text(49,745,'Plan view of recorded position samples. No jumps, ring collision, UI timer or live shard changes.',15,soft);
writeFileSync(join(out,'nov26-w10b-lap-map.svg'),wrap('Measured westbound lap trace',map));

const ring=rings.find(r=>r.id===1);
assert(ring.tangent[0]<-.999);
const evA=clean.result.events.find(e=>e.id===1),evB=bypass.result.events.find(e=>e.id===1);
assert(evA.hit&&!evB.hit);
const zoom=(x,z)=>[640+(x-ring.at[0])*34,340+(z-ring.at[1])*35];
const [gx,gy]=zoom(...ring.at);
let detail=heading('One missed ring, five seconds added','Ring 1. A matched replay steers around the checkpoint instead of through it.');
detail+=panel(48,178,1184,338,'#152a31');
detail+=path(`M82 ${gy}H1198`,'#59747a',1.5,'8 7');
detail+=path(`M${gx} ${gy-70}V${gy+70}`,blue,8);
detail+=path(trace(clean,zoom,{filter:p=>p.x>=-160&&p.x<=-130&&Math.abs(p.z-ring.at[1])<7}),green,5);
detail+=path(trace(bypass,zoom,{filter:p=>p.x>=-160&&p.x<=-130&&Math.abs(p.z-ring.at[1])<7}),gold,5);
detail+=circle(...zoom(evA.x,evA.z),9,green)+circle(...zoom(evB.x,evB.z),9,gold);
detail+=text(70,211,'WESTBOUND  ←',15,soft,bold)+text(gx+15,gy-78,'4 m scoring band',16,blue,bold);
detail+=text(gx+20,gy+145,`Miss: ${fmt(Math.abs(evB.lateral),2)} m from ring centre`,17,gold,bold);
for(const [i,r] of [clean,bypass].entries()){
  const x=48+i*601,c=i?gold:green;
  detail+=panel(x,541,583,151)+text(x+25,572,i?'ONE BYPASS':'ALL EIGHT HIT',16,c,bold);
  detail+=text(x+25,622,`${fmt(r.result.elapsed)} s  +  ${r.result.penalty}.000 s`,25,ink);
  detail+=text(x+558,668,fmt(r.result.total)+' s',31,c,'text-anchor="end" '+bold);
}
detail+=text(49,743,'Recorded reins positions, replay scoring only. Height clearance, jump rails and phone controls are not tested.',15,soft);
writeFileSync(join(out,'nov26-w10b-lap-penalty.svg'),wrap('Ring 1 bypass and five-second penalty',detail));
