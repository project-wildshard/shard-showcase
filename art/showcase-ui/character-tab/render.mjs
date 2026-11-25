import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {stats,tabs,subTabs,player,derived,choose,openBag} from './model.mjs';

const [background,out]=process.argv.slice(2), bg=readFileSync(background);
assert.equal(createHash('sha256').update(bg).digest('hex'),'3dacdb946f662574c2284b9beaa24ee9db9febe8f97da31be45dad3191a37b83');
mkdirSync(out,{recursive:true});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const rec=(x,y,w,h,f='#101e27',stroke='#2b3b43',r=5)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${f}" stroke="${stroke}"/>`;
const txt=(x,y,s,o={})=>`<text x="${x}" y="${y}" fill="${o.f??'#f2eee5'}" font-family="${o.m?'DejaVu Sans Mono':'DejaVu Sans'}" font-size="${o.n??12}" font-weight="${o.b??400}" letter-spacing="${o.k??0}" text-anchor="${o.a??'start'}">${esc(s)}</text>`;
const mono=(x,y,s,o={})=>txt(x,y,s,{m:true,...o});
const pale='#aac0c8',blue='#a8e3ee',teal='#78dbb6',amber='#f2c688',mute='#8eafb7';
const line=(x,y,x2,y2,c='#304650')=>`<path d="M${x} ${y} L${x2} ${y2}" stroke="${c}" stroke-width="1"/>`;
const icons=[
 'M-8 -6 L-3 -8 3 -5 8 -7 8 6 3 8 -3 5 -8 7 Z M-3 -8V5 M3 -5V8',
 'M-6 8 Q-5 1 0 1 Q5 1 6 8Z M-3 -4 A3 3 0 1 0 3 -4A3 3 0 1 0 -3 -4',
 'M0 -8 L7 -1 0 8 -7 -1 Z M-7 -1H7 M0 -8L-2 -1 0 8 2 -1Z',
 'M-7 -1 L0 -5 7 -1 7 7 -7 7 Z M-3 -4 Q-3 -9 0 -9 Q3 -9 3 -4 M-7 2H7',
 'M0 -9 L2.4 -3 8 -2 4 2 5 8 0 5 -5 8 -4 2 -8 -2 -2.4 -3Z',
];
const icon=(x,y,i,c)=>`<path transform="translate(${x} ${y})" d="${icons[i]}" fill="none" stroke="${c}" stroke-width="1.1" stroke-linejoin="round"/>`;
const seal=(x,y)=>`<g transform="translate(${x} ${y})"><path d="M0 -13 12 -6 12 6 0 13 -12 6 -12 -6 Z" fill="#122936" stroke="#5596a8"/><path d="M0 -8 7 -4 7 0 0 7 -7 0 -7 -4Z" fill="none" stroke="#a8e3ee"/><path d="M-4 -2 0 2 4 -2 0 5Z" fill="#a8e3ee"/></g>`;
const title=(y,label,right)=>mono(25,y,label,{n:9.5,b:700,k:1.45,f:blue})+mono(375,y,right,{n:8.25,k:.48,f:mute,a:'end'});
function chrome(state){
 const gear=state.subTab==='Gear';
 let s=rec(10,14,382,846,'url(#glass)','#557681',18);
 s+=rec(11,15,380,845,'none','#486171',17);
 s+=`<path d="M27 15h345" stroke="#9cd6e6" opacity=".62"/>`;
 s+=rec(25,33,58,31,'#122530','#395460');
 s+=mono(54,53,'CLOSE',{n:8.8,a:'middle',k:1.1,b:700});
 s+=seal(199,40)+mono(199,69,'B A G',{n:15,b:700,a:'middle'})+mono(199,84,player.shard.toUpperCase(),{n:7.75,k:1.25,f:pale,a:'middle'});
 s+=mono(376,49,'UI-10',{n:9,a:'end',f:pale})+mono(376,63,'PREVIEW',{n:6.8,a:'end',f:mute,k:.75});
 const w=70.2;
 for(let i=0;i<tabs.length;i++){
  const x=25+i*w, active=tabs[i]===state.tab;
  s+=rec(x,99,w-1,50,active?'#173544':'#101a23',active?'#547d8c':'#25353d',4)+icon(x+w/2,113,i,active?blue:'#91a2ac');
  s+=mono(x+w/2,137,tabs[i].toUpperCase(),{n:8,a:'middle',f:active?blue:'#aab8bd',b:active?700:400,k:.55});
  if(active)s+=rec(x+4,146,w-9,2,'#9adbec','none',1);
 }
 for(let i=0;i<subTabs.length;i++){
  const selected=subTabs[i]===state.subTab,x=25+i*178.5;
  s+=rec(x,160,172,33,selected?'#1e3d49':'#121e27',selected?'#77aab6':'#334b56')+
     mono(x+86,181,subTabs[i].toUpperCase(),{a:'middle',n:10,b:selected?700:400,k:1.6,f:selected?blue:pale});
 }
 s+=line(25,815,375,815)+mono(200,840,gear?'REFERENCE LOADOUT · NO EQUIP ACTION':'STATS GROW AUTOMATICALLY · NO POINTS TO SPEND',{a:'middle',n:8.35,k:.78,f:pale});
 return s;
}
function character(){
 let s=title(216,'SHARD PROGRESSION','SAMPLE VALUES');
 s+=rec(25,225,350,77,'#10232d','#38515b');
 s+=mono(38,250,`LEVEL ${player.level}`,{n:15,b:700,k:1.25})+mono(362,250,player.xp.toLocaleString('en-US')+' / '+player.goal.toLocaleString('en-US')+' XP',{n:11,f:blue,a:'end'});
 s+=rec(38,261,324,5,'#2b4350','none',2)+rec(38,261,324*player.xp/player.goal,5,blue,'none',2);
 s+=txt(38,287,'Levels, XP and aptitudes belong to this shard.',{n:10,f:pale});
 s+=title(321,'ATTRIBUTES','WHITE TICK = LEVEL PAR');
 for(const [i,[id,value,par,apt,description]] of stats.entries()){
  const y=331+i*40;
  s+=rec(25,y,350,37,i%2?'#11232c':'#142632','#30454f',3.5);
  const color=apt>1?teal:apt<1?amber:pale;
  s+=mono(37,y+15,id,{n:10,b:700,k:.9,f:blue})+txt(37,y+29,description,{n:8.65,f:pale});
  const filled=Math.min(104,104*value/(1.65*par)), tick=104/1.65;
  s+=rec(162,y+12,104,4,'#314852','none',2)+rec(162,y+12,filled,4,color,'none',2);
  s+=line(162+tick,y+8,162+tick,y+20,'#f2eee5');
  s+=mono(304,y+17,value,{n:13,b:700,a:'end'});
  s+=mono(362,y+16,(apt>1?'▲ ':apt<1?'▼ ':'  ')+`PAR ${par}`,{n:8.8,a:'end',f:color});
 }
 s+=title(626,'WHAT THEY MAKE','VS. EQUAL-LEVEL REFERENCE');
 for(const [i,[label,value]] of derived.entries()){
  const x=25+(i%2)*177.5,y=637+Math.floor(i/2)*42;
  s+=rec(x,y,172.5,38,'#142632','#30454f');
  s+=txt(x+9,y+14,label,{n:8.7,f:pale})+mono(x+9,y+30,value,{n:11,b:700,f:i===0?'#f8f1dc':blue});
 }
 return s;
}
const weapon=(x,y,type)=>`<g transform="translate(${x} ${y})">${type==='Sword'?
 '<path d="M-23 17 15 -22 25 -25 22 -15 -14 23Z" fill="#b4c7cd" stroke="#b0d0d7"/><path d="M-21 7 -8 20 -11 25 -25 12Z" fill="#bc7848"/><path d="M-18 16 -27 26" stroke="#ba8d58" stroke-width="5"/>':
 '<path d="M-16 21 17 -21 22 -17 -11 26Z" fill="#92704e"/><path d="M-23 -6Q-3 -25 27 3M-23 -6 7 -8 27 3" stroke="#b4c7cd" stroke-width="3" fill="none"/><path d="M-11 9 25 -23" stroke="#ddc18d" stroke-width="2"/>'}</g>`;
function gear(){
 let s=title(218,'GEAR','SAMPLE LOADOUT')+txt(25,239,'Gear lives inside Character, not in the top row.',{n:11.5,f:pale});
 const list=[['PRIMARY','Sword','Common · Forge I','Melee'],['SECONDARY','Crossbow','Common · Forge I','Ranged']];
 for(const [i,[slot,item,grade,kind]] of list.entries()){
  const y=254+i*126;
  s+=rec(25,y,350,111,'#142733','#43616b',6)+rec(35,y+12,87,87,'url(#tile)','#4e6872',6);
  s+=weapon(79,y+55,item);
  s+=mono(137,y+26,slot,{n:8.5,k:1.1,f:blue})+txt(137,y+53,item,{n:21,b:700});
  s+=txt(137,y+76,grade,{n:10.8,f:pale})+mono(359,y+26,kind.toUpperCase(),{n:8.3,k:.85,f:amber,a:'end'});
 }
 s+=title(538,'PROTECTION','REFERENCE SLOTS');
 for(const [i,[label,value]] of [['Armour','Standard issue'],['Finish','Default enamel'],['Trinket','Not equipped']].entries()){
  const y=551+i*49;
  s+=rec(25,y,350,41,'#132530','#304550')+mono(39,y+18,label.toUpperCase(),{n:8.8,k:.9,f:blue})+
    txt(362,y+24,value,{n:11.2,f:pale,a:'end'});
 }
 s+=rec(25,716,350,68,'#112831','#4e6b70')+mono(39,738,'CHARACTER IS THE DEFAULT',{n:9.5,k:1.0,b:700,f:blue})+
    txt(39,761,'Open the Bag again to return to the stat sheet.',{n:10.3,f:pale});
 return s;
}
function card(state){
 const isGear=state.subTab==='Gear';
 return `<svg xmlns="http://www.w3.org/2000/svg" width="402" height="874" viewBox="0 0 402 874" data-subtab="${state.subTab}"><title>UI-10 ${state.subTab} reference, not live game</title><defs>
 <linearGradient id="glass" x2="0" y2="1"><stop stop-color="#101b25"/><stop offset="1" stop-color="#121d25"/></linearGradient>
 <linearGradient id="tile" x2="1" y2="1"><stop stop-color="#172730"/><stop offset="1" stop-color="#33424b"/></linearGradient></defs>
 <image width="402" height="874" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,${bg.toString('base64')}"/>
 <rect width="402" height="874" fill="#172837" opacity=".7"/>${chrome(state)}${isGear?gear():character()}</svg>\n`;
}
for(const [name,state] of [['character',openBag()],['gear',choose(openBag(),'Gear')]])writeFileSync(join(out,`ui10-${name}.svg`),card(state));
