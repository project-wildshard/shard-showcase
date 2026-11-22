export const ARENA={width:18,depth:22,blocks:[[-6,-5,2.2,2.1],[6,-5,2.4,2],[-6,3,2.5,2],[5.8,2.5,2.2,2.2]]}
export const SWORD_SWING=Object.freeze({impact:.148,end:.48})
const TAU=Math.PI*2
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x))
const angle=(a,b)=>((b-a+Math.PI+TAU)%TAU)-Math.PI
const approach=(a,b,m)=>a+clamp(angle(a,b),-m,m)
const length=(x,z)=>Math.hypot(x,z)
function blocked(x,z,r=.28){
 return Math.abs(x)>ARENA.width/2-r||Math.abs(z)>ARENA.depth/2-r||
 ARENA.blocks.some(([u,v,w,d])=>Math.abs(x-u)<w*.5+r&&Math.abs(z-v)<d*.5+r)
}
function move(a,x,z,r){
 if(!blocked(a.x+x,a.z,r))a.x+=x
 if(!blocked(a.x,a.z+z,r))a.z+=z
}
function clear(a,b){
 const n=Math.ceil(length(b.x-a.x,b.z-a.z)/.13)
 for(let i=1;i<n;i++)if(blocked(a.x+(b.x-a.x)*i/n,a.z+(b.z-a.z)*i/n,0))return false
 return true
}
const phase=(e,n)=>{e.phase=n;e.t=0;e.serial++}
export function createGame(){
 return {player:{x:0,z:6.7,yaw:0,pitch:-.30,hp:100,swing:0,swingTime:0,spent:false},
 mite:{x:.23,z:-1.8,yaw:0,hp:70,phase:'sleep',t:0,serial:0,strikes:0},
 time:0,notice:'Approach the crate. It wakes within six meters.',over:false,kills:0,servos:0,drop:null}
}
export function step(g,input={},dt=1/60){
 if(g.over)return
 dt=clamp(dt,0,.05);g.time+=dt
 const p=g.player,e=g.mite
 if(input.yaw!==undefined)p.yaw=input.yaw;if(input.pitch!==undefined)p.pitch=clamp(input.pitch,-1.12,1.12)
 let f=clamp(input.forward||0,-1,1),r=clamp(input.strafe||0,-1,1)
 const len=Math.max(1,length(f,r));f/=len;r/=len
 const pace=(input.sprint?5.0:3.85)*dt
 const px=(Math.sin(p.yaw)*f+Math.cos(p.yaw)*r)*pace,pz=(-Math.cos(p.yaw)*f+Math.sin(p.yaw)*r)*pace
 const current=length(p.x-e.x,p.z-e.z),proposed=length(p.x+px-e.x,p.z+pz-e.z)
 if(e.phase==='die'||proposed>1||proposed>current)move(p,px,pz,.32)
 if(p.swing>0){p.swing=Math.max(0,p.swing-dt);p.swingTime+=dt}
 if(input.attack&&p.swing===0){p.swing=SWORD_SWING.end;p.swingTime=0;p.spent=false}
 let dx=p.x-e.x,dz=p.z-e.z,dist=length(dx,dz)
 if(!p.spent&&p.swing>0&&p.swingTime>=SWORD_SWING.impact){
  p.spent=true
  const face=(-dx*Math.sin(p.yaw)+dz*Math.cos(p.yaw))/Math.max(.001,dist)
  if(dist<2.24&&face>.72&&p.pitch<.6&&p.pitch>-.95&&clear(p,e)&&e.phase!=='die'){
   e.hp=Math.max(0,e.hp-24)
   if(e.hp===0){
    phase(e,'die');g.kills++
    // Land near the chassis as its breakup settles. Preserve the corpse
    // origin so the pickup never follows the player or moving debris.
    g.drop={x:e.x,z:e.z,readyAt:g.time+1.0,expiresAt:g.time+61.0}
    g.notice='Mite down. Wait for the Servo to land.'
   }
   else {phase(e,'hit');g.notice='Hit landed. Step back from the eye flash.'}
  }else if(e.phase!=='die')g.notice='Out of reach. Get closer and face the Mite.'
 }
 e.t+=dt
 const target=Math.atan2(dx,dz)
 if(e.phase==='die'){
  const d=g.drop
  if(d&&g.time>=d.expiresAt){g.drop=null;g.notice='Servo expired. Press R to reset.'}
  else if(d&&g.time>=d.readyAt){
   if(length(p.x-d.x,p.z-d.z)<=1.1&&clear(p,d)){
    g.drop=null;g.servos++;g.notice='Servo salvaged. Press R to reset.'
   }else g.notice='Walk over the Servo to salvage it.'
  }
  return
 }
 if(e.phase==='sleep'){if(dist<6&&clear(e,p)){phase(e,'wake');g.notice='Awake. Watch the cyan eye.'}return}
 if(e.phase==='wake'){if(e.t>=.54)phase(e,'chase');return}
 if(e.phase==='hit'){if(e.t>=.4)phase(e,'chase');return}
 if(e.phase==='chase'||e.phase==='turn'){
  const delta=Math.abs(angle(e.yaw,target))
  if(delta>.58){
   if(e.phase!=='turn')phase(e,'turn')
   e.yaw=approach(e.yaw,target,dt*4.7)
   return
  }
  if(e.phase!=='chase')phase(e,'chase')
  e.yaw=approach(e.yaw,target,dt*5.3)
  if(dist<2.73&&dist>.18&&clear(e,p)){
   e.strikes++;e.special=e.strikes%3===0
   e.goalX=Math.sin(e.yaw);e.goalZ=Math.cos(e.yaw);e.didDamage=false
   phase(e,'windup')
   g.notice=e.special?'Overclock. Dodge the longer charge!':'Cyan flash. Sidestep the bite!'
  }else if(dist>.62){
   const pace=(dist>3.5?2.5:1.6)*dt
   const prox=Math.max(.001,dist)
   move(e,dx/prox*pace,dz/prox*pace,.38)
  }
  return
 }
 if(e.phase==='windup'){
  if(e.t>=(e.special?23/30:.6))phase(e,'lunge')
  return
 }
 if(e.phase==='lunge'){
  if(e.t<.31&&!e.didDamage){
   move(e,e.goalX*dt*(e.special?11.7:9.65),e.goalZ*dt*(e.special?11.7:9.65),.35)
   dx=p.x-e.x;dz=p.z-e.z;dist=length(dx,dz)
   if(!e.didDamage&&dist<1.34&&clear(e,p)){
    e.didDamage=true;p.hp=Math.max(0,p.hp-(e.special?37:23))
    g.notice=p.hp?'You were hit. Move sideways during the windup.':'You went down. Press R to reset.'
    if(p.hp===0)g.over=true
   }
  }
  if(e.t>=(e.special?.70:.60))phase(e,'chase')
 }
}
