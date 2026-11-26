import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {examples,tabs} from './model.mjs';

const [bgPath,out]=process.argv.slice(2);
const bg=readFileSync(bgPath);
assert.equal(createHash('sha256').update(bg).digest('hex'),'3dacdb946f662574c2284b9beaa24ee9db9febe8f97da31be45dad3191a37b83');
mkdirSync(out,{recursive:true});
const ink='#f5f0e8', cyan='#a8e3ee', muted='#abc0c8', low='#8da5ae', amber='#f5cb85';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const panel=(x,y,w,h,fill='#122630',stroke='#405661',r=7)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}"/>`;
const label=(x,y,s,n=12,c=ink,o={})=>`<text x="${x}" y="${y}" fill="${c}" font-size="${n}" font-family="${o.m?'DejaVu Sans Mono':'DejaVu Sans'}" font-weight="${o.b?700:400}" letter-spacing="${o.k??0}" text-anchor="${o.a??'start'}">${esc(s)}</text>`;
const cap=(x,y,s,c=muted,o={})=>label(x,y,s,o.n??9.8,c,{m:true,k:o.k??1.0,b:o.b,a:o.a});
const path=(x,y,d,c,w=1.4)=>`<path transform="translate(${x} ${y})" d="${d}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"/>`;
const tabsIcons=[
  'M-8 -6 -3 -8 3 -5 8 -7V6L3 8 -3 5 -8 7Z M-3 -8V5 M3 -5V8',
  'M-6 8Q-5 1 0 1Q5 1 6 8Z M-3 -4A3 3 0 1 0 3 -4A3 3 0 1 0 -3 -4',
  'M0 -8 7 -1 0 8 -7 -1Z M-7 -1H7 M0 -8 -2 -1 0 8 2 -1Z',
  'M-7 -1 0 -5 7 -1V7H-7Z M-3 -4Q-3 -9 0 -9Q3 -9 3 -4 M-7 2H7',
  'M0 -9 2.4 -3 8 -2 4 2 5 8 0 5 -5 8 -4 2 -8 -2 -2.4 -3Z',
];
const line=(x,x2,y,c='#38505b')=>`<path d="M${x} ${y}H${x2}" stroke="${c}"/>`;

function chrome(){
  let s=panel(10,14,382,846,'url(#glass)','#678592',18);
  s+=panel(11,15,380,844,'none','#405967',17)+line(29,373,15,'#83bac9');
  s+=panel(25,33,64,40,'#142b37','#49626e',6)+cap(57,57,'CLOSE',ink,{a:'middle',b:true,n:9});
  s+=path(201,38,'M0 -12 10 -6 10 6 0 12 -10 6 -10 -6Z M0 -7 6 -3 0 7 -6 -3Z',cyan);
  s+=cap(201,69,'B A G',ink,{a:'middle',b:true,n:15})+cap(201,84,'SHOWCASE',muted,{a:'middle',n:8});
  s+=cap(375,49,'W9b / E13',muted,{a:'end',n:8.1})+cap(375,63,'PREVIEW',low,{a:'end',n:7.8});
  for(const [i,t] of tabs.entries()){
    const x=25+i*70.2, active=t==='Finds';
    s+=panel(x,99,69.2,50,active?'#1a3d4c':'#11212a',active?'#82b3c0':'#314750',4);
    s+=path(x+34.6,114,tabsIcons[i],active?cyan:muted)+cap(x+34.6,137,t.toUpperCase(),active?cyan:muted,{a:'middle',b:active,n:8.5,k:.45});
    if(active)s+=panel(x+4,146,61,2,cyan,'none',1);
  }
  return s;
}
function collection(data){
  let s=label(25,189,'Finds',26,ink,{b:true})+
    cap(375,188,'SHARD JOURNAL',cyan,{a:'end',n:8.8})+
    label(25,211,'Discover places, keepsakes and Gold.',11.7,muted);
  for(const [i,r] of data.collection.entries()){
    const y=228+i*81;
    s+=panel(25,y,352,73,i===2?'#242a30':'#172933',i===2?'#645744':'#344d58');
    s+=panel(36,y+12,34,34,'#14232b','#45616c',5)+path(53,y+29,r.icon,r.color);
    s+=label(80,y+26,r.label,14.3,ink,{b:true});
    s+=label(80,y+43,r.unit,10.8,muted);
    s+=label(363,y+30,r.count+' / '+r.limit,18,r.color,{a:'end',m:true,b:true});
    const width=326/r.limit;
    for(let j=0;j<r.limit;j++){
      const x=38+j*width;
      s+=panel(x,y+54,width-2.25,6,j<r.count?r.color:'#31454d','none',1.3);
      if(j<r.count && i===2 && ((j+1)%5===0))s+=line(x+2,x+width-4,y+57,'#7a5e35');
    }
  }
  const hint=data.next===null?'All four milestones reached':data.remaining+' more Gold to the next chip';
  s+=panel(25,477,352,54,'#252b2e','#706044',6)+cap(38,496,'CALIBRATION CHIPS',amber,{b:true,n:8.9});
  s+=label(38,518,hint,11.5,ink)+label(362,510,data.earned+' / 4',16,amber,{a:'end',m:true,b:true});
  return s;
}
function personal(data){
  let s=label(25,567,'Personal bests',18,ink,{b:true})+
    cap(375,566,'WEST COURSES',cyan,{a:'end',n:8.5});
  for(const [i,r] of data.records.entries()){
    const y=581+57*i;
    s+=panel(25,y,352,50,'#152934','#344e5a',5);
    s+=label(38,y+20,r.label,13.2,ink,{b:true})+label(38,y+37,r.hint,10.1,muted);
    s+=label(363,y+30,r.value??'No result yet',r.value?13:10.5,r.value?cyan:muted,{a:'end',m:true,b:Boolean(r.value)});
  }
  s+=line(25,376,763);
  s+=label(25,786,'East Scrip chests are separate from cosmetic caches.',10.6,muted);
  s+=cap(201,827,'ILLUSTRATIVE SAVE · NO LIVE RECORDS',low,{a:'middle',k:.65,n:8.5});
  return s;
}
for(const [name,data] of Object.entries(examples)){
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="402" height="874" viewBox="0 0 402 874" role="img"><title>Wildshard FINDS • ${name==='new'?'New explorer':'Mid-route example'}</title><desc>Illustrative finds counters, Gold milestones and best scores in the Bag.</desc>
<defs><linearGradient id="glass" x2="0" y2="1"><stop stop-color="#101c26"/><stop offset="1" stop-color="#111c26"/></linearGradient></defs>
<image width="402" height="874" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,${bg.toString('base64')}"/>
<rect width="402" height="874" fill="#172837" opacity=".7"/>${chrome()}${collection(data)}${personal(data)}</svg>\n`;
  writeFileSync(join(out,`finds-${name}.svg`),svg);
}
