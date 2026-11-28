// Original, engine-independent game logic for the local Forge Yard demo.
import {configuration} from './variants.mjs';
import {SURGE,surgeAt,surgeTouches} from './breakwater-surge.mjs';
export const ARENA=10.5;
export const RAM_OPEN_SECONDS=.88;
const SHIELD_OPEN_STATES=['windup','recover','hit','feint'];
export const wardenOpen=b=>b.attack==='guard'&&b.life>0&&SHIELD_OPEN_STATES.includes(b.state);
export const SNARE_RADIUS=.93;
export const sweepRadius=b=>b.reach+.32;
export const ramOpen=b=>b.id==='WSC-ENM-004'&&!b.variant&&b.state==='recover'&&b.life>0&&!b.chargeConnected&&b.t<RAM_OPEN_SECONDS;
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
export function create(enemyTypes,{breakwater=false}={}){
 return {surge:breakwater?{section:null,lastHit:-1,hits:0}:null,time:0,weapon:0,wave:0,events:[],player:{x:0,z:5.7,r:.36,hp:120,maxHp:120,face:[0,-1],inv:0,slash:null,dodge:0},bots:[],enemyTypes};
}
export function select(s,n){if(Number.isInteger(n)&&WEAPONS[n]&&!s.player.slash)s.weapon=n;}
export function spawn(s,index,where={x:0,z:-4.2},variant=null){
 const base=s.enemyTypes[index];
 if(!base)return null;
 const spec=configuration(base,variant);
 const b={...spec,x:where.x,z:where.z,r:spec.radius,life:spec.hp,
  maxHp:spec.hp,mark:null,burstLeft:0,rushReady:true,feinted:false,echoed:false,pulse:0,pulseCooldown:0,windReady:spec.windup,state:'idle',t:0,face:[0,1],lock:[0,1],hit:false,lockLength:0,dashHit:false,shots:0,activeDuration:.29};
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
const DAM={windmill:18,pounce:14,beam:13,charge:26,hook:12,guard:15,burrow:16,burst:18,salvo:9,lunge:21,mortar:22,crosscut:17,vacuum:18,stilt:13,relay:18,recoil:20,shutter:20,seed:12,harrow:15,flank:18};
function strikePlayer(s,b,damage=DAM[b.attack],style=b.attack){
 const p=s.player;
 if(p.inv>0||p.hp<=0)return false;
 p.hp=Math.max(0,p.hp-damage);p.inv=.26;
 s.events.push({type:'player-hit',enemy:b.id,style,hp:p.hp});return true;
}
const ACTIVE={charge:.56,pounce:.39,salvo:.62,lunge:.32,mortar:.61,crosscut:.38,vacuum:.57,stilt:.62,relay:.66,recoil:.39,shutter:.36,seed:.69,harrow:.59,flank:.48};
export const MORTAR_RADIUS=1.48,CROSS_HALF_WIDTH=.56,RELAY_RADIUS=.98,STILT_RADIUS=1.01,SEED_RADIUS=.70,FLANK_RADIUS=1.04,HARROW_WIND=.87;
export function seedMarks(b){
 const {x,z}=b.mark,[u,v]=b.lock;
 return [-1.20,0,1.20].map(d=>({x:x+u*d,z:z+v*d}));
}
export function harrowLine(b){
 const [x,z]=b.lock,a=b.state==='active'?HARROW_WIND*(1-2*clamp(b.t/.55,0,1)):HARROW_WIND;
 const co=Math.cos(a),si=Math.sin(a);return [x*co-z*si,x*si+z*co];
}
export function splitMarks(b,offset){
 const {x,z}=b.mark;
 return [{x:x-b.lock[1]*offset,z:z+b.lock[0]*offset},{x:x+b.lock[1]*offset,z:z-b.lock[0]*offset}];
}
function fireSalvo(s,b,p){
 const ax=p.x-b.x,az=p.z-b.z,along=ax*b.lock[0]+az*b.lock[1];
 const off=Math.abs(ax*b.lock[1]-az*b.lock[0]);
 s.events.push({type:'salvo-shot',enemy:b.id});
 if(along>0&&along<b.reach+.35&&off<.61&&!reachBlocked(b,p))strikePlayer(s,b);
}
function state(s,b,next){
 b.state=next;b.t=0;
 if(next==='active')b.activeDuration=ACTIVE[b.attack]??.29;
 s.events.push({type:'enemy-state',enemy:b.id,state:next,style:b.attack});
}
function beginWind(s,b,p,wind=b.windup){
 b.lock=norm(p.x-b.x,p.z-b.z);b.lockLength=Math.max(1.5,gap(b,p));
 b.dashHit=false;b.chargeConnected=false;b.shots=0;b.mark={x:p.x,z:p.z};b.windReady=wind;
 state(s,b,'windup');
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
 // Stage contact is checked after movement. It shares the dodge/damage grace
 // period, applies at most once per tide, and never hurts the rival.
 if(s.surge){
  const tide=s.surge,section=tide.section=surgeAt(s.time);
  if(p.hp>0&&!p.inv&&surgeTouches(p,section)&&tide.lastHit!==section.cycle){
   tide.lastHit=section.cycle;tide.hits++;p.hp=Math.max(0,p.hp-SURGE.damage);p.inv=.26;
   s.events.push({type:'player-hit',enemy:null,style:'surge',damage:SURGE.damage,hp:p.hp});
  }
 }
 if(p.slash){
  const a=p.slash;a.time+=dt;
  if(!a.done&&a.time>=a.weapon.wind){
   a.done=true;a.releaseAt=a.time;
   const cone=a.weapon.style==='thrust'?.67:a.weapon.style==='chop'?.23:-.05;
   for(const b of s.bots)if(b.life>0&&gap(p,b)<=a.weapon.reach+b.r&&dot(p.face,norm(b.x-p.x,b.z-p.z))>=cone&&!reachBlocked(p,b)){
    const front=dot(b.face,norm(p.x-b.x,p.z-b.z))>.35;
    const shutted=b.attack==='shutter'&&['idle','move'].includes(b.state);
    const blocks=shutted||((b.attack==='guard'||b.variant==='bulwark')&&front&&!SHIELD_OPEN_STATES.includes(b.state));
    const counter=ramOpen(b);
    const dealt=counter?Math.ceil(a.weapon.power*1.35):blocks?Math.ceil(a.weapon.power*(b.variant==='bulwark'?.22:shutted?.45:.35)):a.weapon.power;
    b.life=Math.max(0,b.life-dealt);
    if(blocks)s.events.push({type:'shield',enemy:b.id});
    s.events.push({type:'enemy-hit',enemy:b.id,hp:b.life,counter,damage:dealt});
    if(!b.life){state(s,b,'defeat');s.events.push({type:'defeat',enemy:b.id});}
    else if(b.state!=='active'&&!blocks)state(s,b,'hit');
   }
  }
  if(a.time>=a.weapon.cycle)p.slash=null;
 }
 for(const b of s.bots){
  b.t+=dt;
  if(b.life<=0||p.hp<=0)continue;
  const d=gap(b,p),aim=norm(p.x-b.x,p.z-b.z);
  if(b.variant==='overload'){
   b.pulseCooldown=Math.max(0,b.pulseCooldown-dt);
   if(b.pulse>0){
    b.pulse-=dt;
    if(b.pulse<=0){
     b.pulse=0;b.pulseCooldown=2.9;
     s.events.push({type:'discharge',enemy:b.id});
     if(d<2.25&&!reachBlocked(b,p))strikePlayer(s,b,9,'overload');
    }
   }else if(!b.pulseCooldown&&d<3.55){
    b.pulse=.77;
    s.events.push({type:'pulse',enemy:b.id});
   }
  }
  if(b.state==='idle'||b.state==='move'){
   b.face=aim;
   if(d<=b.reach&&!reachBlocked(b,p)){
     beginWind(s,b,p);continue;
   }
   if(d>1.15){
    if(b.state!=='move'){
     state(s,b,'move');
     if(b.variant==='rusher'&&b.rushReady){
      b.rushReady=false;b.burstLeft=.47;s.events.push({type:'rush',enemy:b.id});
     }
    }
    // A small tangent bypass around convex cover.
    let [x,z]=aim;
    if(reachBlocked(b,p)){x=aim[0]*.31-aim[1]*.95;z=aim[1]*.31+aim[0]*.95;}
    const pace=b.pace*(b.burstLeft>0?2.12:1);
    b.burstLeft=Math.max(0,b.burstLeft-dt);
    place(b,b.x+x*pace*dt,b.z+z*pace*dt);
   }
  }else if(b.state==='windup'&&b.variant==='feinter'&&!b.feinted&&b.t>=b.windReady*.58){
   b.feinted=true;
   const side=b.id.length%2?1:-1;
   place(b,b.x-b.lock[1]*.75*side,b.z+b.lock[0]*.75*side);
   state(s,b,'feint');
   s.events.push({type:'feint',enemy:b.id});
  }else if(b.state==='feint'&&b.t>=.24){
   if(d<=b.reach+.95&&!reachBlocked(b,p))beginWind(s,b,p,b.windup*.76);
   else state(s,b,'idle');
  }else if(b.state==='windup'&&b.t>=b.windReady){
   state(s,b,'active');
   if(b.attack==='windmill'&&d<=sweepRadius(b)&&!reachBlocked(b,p))strikePlayer(s,b);
   if(b.attack==='hook'||b.attack==='beam'){
    const ax=p.x-b.x,az=p.z-b.z,along=ax*b.lock[0]+az*b.lock[1];
    const off=Math.abs(ax*b.lock[1]-az*b.lock[0]);
    if(along>0&&along<b.reach+.6&&off<(b.attack==='hook'?.78:.63)&&!reachBlocked(b,p)){
     const hit=strikePlayer(s,b);
     if(hit&&b.attack==='hook'){
      const q=Math.min(1.30,Math.max(0,d-1.15));place(p,p.x-aim[0]*q,p.z-aim[1]*q);
     }
    }
   }
   if(b.attack==='guard'&&d<=b.reach+.30&&dot(b.lock,aim)>.55&&!reachBlocked(b,p)&&strikePlayer(s,b)){
    place(p,p.x+b.lock[0]*.88,p.z+b.lock[1]*.88);
   }
   if(b.attack==='burrow'){
    const old={x:b.x,z:b.z};
    if(!reachBlocked(old,b.mark)){place(b,b.mark.x-b.lock[0]*.45,b.mark.z-b.lock[1]*.45);}
    if(gap(p,b.mark)<SNARE_RADIUS&&!reachBlocked(b,p))strikePlayer(s,b);
   }
   if(b.attack==='salvo'){b.shots=1;fireSalvo(s,b,p);}
   if(b.attack==='mortar')s.events.push({type:'mortar-launch',enemy:b.id});
   if(b.attack==='crosscut'){
    // The paddles sweep the transverse strip through the lock point.
    const z=b.mark.z-p.z,x=b.mark.x-p.x;
    if(Math.abs(x*b.lock[0]+z*b.lock[1])<CROSS_HALF_WIDTH&&
       Math.abs(x*b.lock[1]-z*b.lock[0])<1.72&&!reachBlocked(b,p))strikePlayer(s,b);
   }
   if(b.attack==='recoil'&&d<=b.reach+.10&&dot(b.lock,aim)>.84&&!reachBlocked(b,p))strikePlayer(s,b);
   if(b.attack==='shutter'&&d<=b.reach+.21&&dot(b.lock,aim)>.67&&!reachBlocked(b,p))strikePlayer(s,b);
   if(b.attack==='burst'&&d<b.reach+.16&&!reachBlocked(b,p))strikePlayer(s,b);
  }else if(b.state==='active'){
   if(b.attack==='seed'&&b.shots<3&&b.t+1e-6>=[.16,.34,.52][b.shots]){
    const index=b.shots++,mark=seedMarks(b)[index];
    if(gap(p,mark)<SEED_RADIUS&&!reachBlocked(mark,p))strikePlayer(s,b);
    s.events.push({type:'seed-burst',enemy:b.id,index});
   }
   if(b.attack==='harrow'&&!b.dashHit&&d<=b.reach+.12&&dot(harrowLine(b),aim)>.992&&!reachBlocked(b,p)){
    if(strikePlayer(s,b))b.dashHit=true;
   }
   if(b.attack==='flank'){
    const side=b.lock[1]>=0?-1:1;
    if(b.t<=.26)place(b,b.x-b.lock[1]*side*dt*4.2,b.z+b.lock[0]*side*dt*4.2);
    if(!b.dashHit&&b.t>=.29){
     b.dashHit=true;s.events.push({type:'flank-strike',enemy:b.id});
     if(gap(p,b.mark)<FLANK_RADIUS&&!reachBlocked(b,p))strikePlayer(s,b);
    }
   }
   if(b.attack==='vacuum'){
    const inSlot=d<=b.reach+.14&&dot(b.lock,aim)>.89&&!reachBlocked(b,p);
    if(b.t<.42&&inSlot&&p.inv<=0&&d>1.14){
     const q=Math.min(3.5*dt,d-1.14);place(p,p.x-aim[0]*q,p.z-aim[1]*q);
    }
    if(!b.dashHit&&b.t>=.42){
     b.dashHit=true;s.events.push({type:'vacuum-release',enemy:b.id});
     if(inSlot&&d<=1.67&&strikePlayer(s,b))place(p,p.x+aim[0]*.72,p.z+aim[1]*.72);
    }
   }
   if(b.attack==='stilt'||b.attack==='relay'){
    const stilt=b.attack==='stilt',at=b.shots===0?(stilt?.08:.22):(stilt?.38:.52);
    if(b.shots<2&&b.t+1e-6>=at){
     const index=b.shots++,mark=splitMarks(b,stilt?.54:1.23)[index],radius=stilt?STILT_RADIUS:RELAY_RADIUS;
     if(gap(p,mark)<radius&&!reachBlocked(mark,p))strikePlayer(s,b);
     s.events.push({type:'split-strike',enemy:b.id,index});
    }
   }
   if(b.attack==='recoil'&&b.t<=.32)place(b,b.x-b.lock[0]*3.35*dt,b.z-b.lock[1]*3.35*dt);
   if(b.attack==='salvo'&&b.shots<3&&b.t+1e-6>=b.shots*.28){b.shots++;fireSalvo(s,b,p);}
   if(b.attack==='mortar'&&!b.dashHit&&b.t>=.50){
    b.dashHit=true;s.events.push({type:'mortar-impact',enemy:b.id});
    if(gap(p,b.mark)<MORTAR_RADIUS&&!reachBlocked(b.mark,p))strikePlayer(s,b);
   }
   if(['pounce','charge','lunge'].includes(b.attack)){
    const speed=b.attack==='pounce'?7.2:b.attack==='lunge'?8.35:10.8;
    const moved=place(b,b.x+b.lock[0]*speed*dt,b.z+b.lock[1]*speed*dt);
    if(!b.dashHit&&gap(p,b)<b.r+p.r+.24&&!reachBlocked(b,p)){b.chargeConnected=strikePlayer(s,b);b.dashHit=true;}
    if(moved<speed*dt*.68){state(s,b,'recover');continue;}
   }
   if(b.t>b.activeDuration)state(s,b,'recover');
  }else if(b.state==='recover'){
   if(b.variant==='echo'&&!b.echoed&&b.t>=b.recover*.53&&d<=b.reach+.45&&!reachBlocked(b,p)){
    b.echoed=true;
    s.events.push({type:'echo',enemy:b.id});
    beginWind(s,b,p,b.windup*.63);
   }else if(b.t>=b.recover){
    b.feinted=false;b.echoed=false;b.rushReady=true;
    state(s,b,'idle');
   }
  }else if(b.state==='hit'&&b.t>=.24)state(s,b,'idle');
 }
}
