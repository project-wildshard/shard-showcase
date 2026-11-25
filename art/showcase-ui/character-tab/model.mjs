// Illustrative UI fixture only. These are not reads or writes of a game profile.
export const stats=[
 ['VIT',184,176,1.2,'Maximum health'],
 ['STR',33,35,1,'Melee attack · stagger dealt'],
 ['DEX',37,35,1.2,'Ranged attack · hit chance · melee crit'],
 ['AGI',41,45,.8,'Dodge share · ranged crit'],
 ['DEF',40,39,1,'Physical armour · deflect share'],
 ['MDEF',17,18,1,'Energy armour · burn, shock, blast'],
 ['LUK',12,13,.8,'Crit size · lucky saves'],
];
export const tabs=['Map','Character','Finds','Pack','Feats'];
export const subTabs=['Character','Gear'];
export const player=Object.freeze({level:7,xp:64,goal:2890,shard:'Showcase Shard'});
const [v,s,d,a,p,m,l]=stats.map(([key,value,par])=>({key,value,par}));
const mitigation=f=>100*f.value/(2.5*f.par+f.value);
const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
const crit=f=>clamp(10+50*(f.value/f.par-1),0,40);
const pct=n=>n.toFixed(1)+'%';
export const derived=[
 ['Maximum HP',String(v.value)],['Physical armour',pct(mitigation(p))],
 ['Energy armour',pct(mitigation(m))],['Dodge share',pct(100*a.value/(a.value+p.value))],
 ['Melee / ranged crit',pct(crit(d))+' / '+pct(crit(a))],
 ['Critical damage',(1.5+l.value/100).toFixed(2)+'×'],
 ['Outgoing fail roll',pct(clamp(12+clamp(50*(1-d.value/d.par),-8,8),2,90))],
 ['Lucky save',pct(Math.min(6,l.value*.2))],
];
export function openBag(){return {tab:'Character',subTab:'Character'};}
export function choose(state,name){return subTabs.includes(name)?{...state,subTab:name}:state;}
