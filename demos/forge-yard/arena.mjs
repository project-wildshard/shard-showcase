// Original, engine-independent game logic for the local Forge Yard demo.
export const ARENA=10.5;
export const COVER=[[-3.1,-.6,.78],[2.7,-2.8,.88],[-2.2,3.2,.93],[4.2,2.9,.66]];
const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));
const norm=(x,z)=>{const d=Math.hypot(x,z);return d>1e-6?[x/d,z/d]:[0,0];};
const gap=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
// Proposed weapon tuning, not claims about physics outside this demo.
export const WEAPONS=[
 ['014','Signal Shear','sweep',2.40,19,.21,.55],
 ['015','Dock Cleaver','chop',1.95,22,.31,.62],
 ['016','Line Pike','thrust',3.25,15,.26,.57],
 ['017','Rivet Maul','chop',2.15,30,.43,.82],
 ['018','Harbor Hook','sweep',2.70,17,.30,.62],
 ['019','Cinder Axe','chop',2.28,26,.36,.73],
 ['020','Relay Baton','sweep',1.66,13,.13,.35],
 ['021','Beacon Lance','thrust',3.10,20,.34,.69],
 ['022','Slipfin','sweep',2.04,15,.15,.44],
 ['023','Counterweight Flail','chop',2.48,24,.47,.85],
 ['024','Glassbreaker Fan','sweep',2.12,17,.22,.58],
 ['025','Rail Needle','thrust',2.80,13,.15,.42]
].map(([id,name,style,reach,power,wind,cycle])=>({id,name,style,reach,power,wind,cycle}));
function place(o,x,z){
 const before=[o.x,o.z];
 x=clamp(x,-ARENA+o.r,ARENA-o.r);z=clamp(z,-ARENA+o.r,ARENA-o.r);
 for(const [a,b,r] of COVER){
  const d=Math.hypot(x-a,z-b),q=o.r+r;
  if(d<q){const [u,v]=norm(x-a,z-b);x=a+(u||(!v?1:0))*q;z=b+v*q;}
 }
 o.x=x;o.z=z;
 return Math.hypot(x-before[0],z-before[1]);
}
function reachBlocked(a,b){
 const ux=b.x-a.x,uz=b.z-a.z,ll=ux*ux+uz*uz;
 return COVER.some(([x,z,r])=>{
  const t=clamp(((x-a.x)*ux+(z-a.z)*uz)/Math.max(.000001,ll),0,1);
  return Math.hypot(x-a.x-t*ux,z-a.z-t*uz)<r-.045;
 });
}
export function create(enemyTypes){
 return {time:0,weapon:0,wave:0,events:[],player:{x:0,z:5.7,r:.36,hp:120,maxHp:120,face:[0,-1],inv:0,slash:null,dodge:0},bots:[],enemyTypes};
}
export function select(s,n){if(Number.isInteger(n)&&WEAPONS[n]&&!s.player.slash)s.weapon=n;}
export function spawn(s,index,where={x:0,z:-4.2}){
 const spec=s.enemyTypes[index];
 if(!spec)return null;
 const b={...spec,x:where.x,z:where.z,r:spec.radius,life:spec.hp,
  maxHp:spec.hp,state:'idle',t:0,face:[0,1],lock:[0,1],hit:false,lockLength:0,dashHit:false};
 s.bots.push(b);
 return b;
}
export function press(s,kind){
 const p=s.player;
 if(p.hp<=0)return false;
 if(kind==='dodge'&&p.dodge<=0&&!p.slash){p.dodge=.245;p.inv=.29;s.events.push({type:'dodge'});return true;}
 if(kind==='attack'&&!p.dodge&&!p.slash){
  const weapon=WEAPONS[s.weapon];
  const near=s.bots.filter(b=>b.life>0&&gap(p,b)<weapon.reach+1.1&&!reachBlocked(p,b)).sort((a,b)=>gap(a,p)-gap(b,p))[0];
  if(near)p.face=norm(near.x-p.x,near.z-p.z);
  p.slash={time:0,done:false,weapon};
  s.events.push({type:'swing',id:weapon.id});
  return true;
 }
 return false;
}
const DAM={windmill:18,pounce:14,beam:13,charge:26};
function strikePlayer(s,b){
 const p=s.player;
 if(p.inv>0||p.hp<=0)return false;
 p.hp=Math.max(0,p.hp-DAM[b.attack]);p.inv=.26;
 s.events.push({type:'player-hit',enemy:b.id,style:b.attack,hp:p.hp});return true;
}
function state(s,b,next){
 b.state=next;b.t=0;
 s.events.push({type:'enemy-state',enemy:b.id,state:next,style:b.attack});
}
export function tick(s,seconds,input=[0,0]){
 const dt=clamp(seconds,0,.05),p=s.player;
 if(dt<=0)return;
 s.time+=dt;
 p.inv=Math.max(0,p.inv-dt);
 const dir=norm(...input),moving=!!(dir[0]||dir[1]);
 if(p.hp>0){
  if(p.dodge){place(p,p.x+p.face[0]*9.6*dt,p.z+p.face[1]*9.6*dt);p.dodge=Math.max(0,p.dodge-dt);}
  else if(moving){if(!p.slash)p.face=dir;const v=p.slash?1.4:4.6;place(p,p.x+dir[0]*v*dt,p.z+dir[1]*v*dt);}
 }
 if(p.slash){
  const a=p.slash;a.time+=dt;
  if(!a.done&&a.time>=a.weapon.wind){
   a.done=true;
   const cone=a.weapon.style==='thrust'?.67:a.weapon.style==='chop'?.23:-.05;
   for(const b of s.bots)if(b.life>0&&gap(p,b)<=a.weapon.reach+b.r&&dot(p.face,norm(b.x-p.x,b.z-p.z))>=cone&&!reachBlocked(p,b)){
    b.life=Math.max(0,b.life-a.weapon.power);
    s.events.push({type:'enemy-hit',enemy:b.id,hp:b.life});
    if(!b.life){state(s,b,'defeat');s.events.push({type:'defeat',enemy:b.id});}
    else if(b.state!=='active')state(s,b,'hit');
   }
  }
  if(a.time>=a.weapon.cycle)p.slash=null;
 }
 for(const b of s.bots){
  b.t+=dt;
  if(b.life<=0||p.hp<=0)continue;
  const d=gap(b,p),aim=norm(p.x-b.x,p.z-b.z);
  if(b.state==='idle'||b.state==='move'){
   b.face=aim;
   if(d<=b.reach&&!reachBlocked(b,p)){
     b.lock=aim;b.lockLength=Math.max(1.5,d);b.dashHit=false;
     state(s,b,'windup');continue;
   }
   if(d>1.15){
    if(b.state!=='move')state(s,b,'move');
    // A small tangent bypass around convex cover.
    let [x,z]=aim;
    if(reachBlocked(b,p)){x=aim[0]*.31-aim[1]*.95;z=aim[1]*.31+aim[0]*.95;}
    place(b,b.x+x*b.pace*dt,b.z+z*b.pace*dt);
   }
  }else if(b.state==='windup'&&b.t>=b.windup){
   state(s,b,'active');
   if(b.attack==='windmill'&&d<=b.reach+.32&&!reachBlocked(b,p))strikePlayer(s,b);
   if(b.attack==='beam'){
    const ax=p.x-b.x,az=p.z-b.z,along=ax*b.lock[0]+az*b.lock[1];
    const off=Math.abs(ax*b.lock[1]-az*b.lock[0]);
    if(along>0&&along<b.reach+.6&&off<.63&&!reachBlocked(b,p))strikePlayer(s,b);
   }
  }else if(b.state==='active'){
   if(b.attack==='pounce'||b.attack==='charge'){
    const speed=b.attack==='pounce'?7.2:10.8;
    const moved=place(b,b.x+b.lock[0]*speed*dt,b.z+b.lock[1]*speed*dt);
    if(!b.dashHit&&gap(p,b)<b.r+p.r+.24&&!reachBlocked(b,p)){strikePlayer(s,b);b.dashHit=true;}
    if(moved<speed*dt*.68){state(s,b,'recover');continue;}
   }
   if(b.t>(b.attack==='charge'?.56:b.attack==='pounce'?.39:.29))state(s,b,'recover');
  }else if((b.state==='recover'&&b.t>=b.recover)||(b.state==='hit'&&b.t>=.24))state(s,b,'idle');
 }
}
