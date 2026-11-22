import test from 'node:test'
import assert from 'node:assert/strict'
import {createGame,MITE_TIMING,step} from './combat.mjs'
const advance=(g,secs,i)=>{for(let n=0;n<secs*60;n++)step(g,i,1/60)}
test('walking enters wake radius, turns and pursues',()=>{
 const g=createGame()
 advance(g,.25);assert.equal(g.mite.phase,'sleep')
 advance(g,.95,{forward:1});assert.notEqual(g.mite.phase,'sleep')
 g.player.x=-3.5;g.player.z=2.0;const initial=g.mite.yaw
 advance(g,.94)
 assert.notEqual(g.mite.yaw,initial)
})
test('windup timing, impact and defeat; third attack is special',()=>{
 const g=createGame();Object.assign(g.mite,{phase:'chase',x:0,z:0,yaw:0,strikes:2})
 Object.assign(g.player,{x:0,z:1.8,hp:35})
 step(g);assert(g.mite.special);assert.equal(g.mite.phase,'windup')
 advance(g,.68);assert.equal(g.player.hp,35)
 advance(g,.55);assert.equal(g.player.hp,0);assert(g.over)
})
test('three correctly aimed sword hits kill a Mite',()=>{
 const g=createGame();Object.assign(g.mite,{x:0,z:0,phase:'wake'})
 Object.assign(g.player,{x:0,z:1.35,yaw:0})
 advance(g,1.75,{attack:true});assert.equal(g.kills,1)
 assert.equal(g.mite.phase,'die')
 assert.equal(g.mite.hp,0)
})
test('crates block movement and a direct sword hit',()=>{
 const g=createGame();Object.assign(g.player,{x:6,z:-3.5,yaw:0})
 advance(g,2,{forward:1});assert(g.player.z>-4.1)
 Object.assign(g.mite,{x:6,z:-5.4,phase:'sleep'})
 advance(g,.21,{attack:true});assert.equal(g.mite.hp,70)
})
test('one Servo lands at the corpse, then is picked up by walking over it',()=>{
 const g=createGame();Object.assign(g.mite,{x:0,z:0,phase:'wake',hp:24})
 Object.assign(g.player,{x:0,z:1.8,yaw:0})
 advance(g,.25,{attack:true})
 assert.equal(g.kills,1);assert.equal(g.servos,0)
 assert.deepEqual([g.drop.x,g.drop.z],[0,0])
 advance(g,.2,{forward:1});assert.equal(g.servos,0,'Not before the drop lands')
 advance(g,.95);assert.equal(g.servos,1);assert.equal(g.drop,null)
 advance(g,.6,{attack:true});assert.equal(g.servos,1,'No duplicate pickup')
})
test('uncollected Servo expires and does not persist into a reset',()=>{
 const g=createGame();Object.assign(g.mite,{x:0,z:0,phase:'wake',hp:24})
 Object.assign(g.player,{x:0,z:1.8,yaw:0})
 advance(g,.25,{attack:true});assert(g.drop)
 advance(g,62)
 assert.equal(g.drop,null);assert.equal(g.servos,0);assert.match(g.notice,/expired/)
 assert.equal(createGame().drop,null)
})

test('dock is solid, but central approach to the Mite stays open',()=>{
 const side=createGame();Object.assign(side.player,{x:3.25,z:-3.7,yaw:0})
 advance(side,.7,{forward:1});assert(side.player.z>-4.17)
 const lane=createGame()
 advance(lane,1.48,{forward:1});assert(lane.player.z<1.1)
 assert.notEqual(lane.mite.phase,'sleep')
})

for(const kind of ['bite','overclock'])test(kind+' can be dodged on reaction and punished',()=>{
 for(const dt of [1/60,1/30]){
  const g=createGame(),{mite:e,player:p}=g
  Object.assign(e,{phase:'chase',x:0,z:0,yaw:0,strikes:kind==='overclock'?2:0})
  Object.assign(p,{x:0,z:2.54,pitch:0})
  step(g,{},dt)
  assert.equal(e.phase,'windup')
  assert.equal(e.special,kind==='overclock')
  const start=g.time
  while(e.phase==='windup'||e.phase==='lunge'){
   assert(g.time-start<1.5)
   const elapsed=g.time-start
   step(g,{strafe:Number(elapsed+.0001>=.25&&p.x<1.55)},dt)
   if(e.phase==='windup')assert(elapsed<MITE_TIMING[kind].tell)
  }
  assert.equal(e.phase,'recover')
  assert.equal(p.hp,100)
  assert(Math.abs(e.x)<1e-8,'attack did not track the dodge')
  assert.match(g.notice,/face the Mite and strike/i)
  const aim=Math.atan2(e.x-p.x,p.z-e.z)
  step(g,{yaw:aim,attack:true},dt)
  while(e.hp===70){assert(p.swingTime<.22);step(g,{},dt)}
  assert.equal(e.hp,46);assert.equal(e.phase,'hit');assert.equal(p.hp,100)
 }
})

test('gantry feet stop movement without blocking the center approach',()=>{
 const blocked=createGame();Object.assign(blocked.player,{x:2.92,z:-8.1,yaw:0})
 advance(blocked,.9,{forward:1})
 assert(blocked.player.z> -9.215&&blocked.player.z< -9)
 const clear=createGame();Object.assign(clear.player,{x:0,z:-8.1,yaw:0})
 advance(clear,.9,{forward:1})
 assert(clear.player.z< -10.6&&clear.player.z>=-10.68)
})

test('dodge clears the bite without invulnerability and respects solid cover',()=>{
 const g=createGame();Object.assign(g.mite,{phase:'chase',x:0,z:0,yaw:0})
 Object.assign(g.player,{x:0,z:2.54})
 step(g);advance(g,.25)
 step(g,{dodge:true});advance(g,.65)
 assert.equal(g.player.hp,100)
 assert(g.player.x>1.7&&g.player.x<1.81)
 const blocked=createGame();Object.assign(blocked.player,{x:2.5,z:-5.45})
 step(blocked,{dodge:true});advance(blocked,.3)
 assert.equal(blocked.player.x,2.5,'Dodge never phases through the dock')
 const exposed=createGame();Object.assign(exposed.mite,{phase:'chase',x:0,z:0,yaw:0})
 Object.assign(exposed.player,{x:0,z:2.54})
 step(exposed);advance(exposed,.55)
 step(exposed,{dodge:true,forward:1});advance(exposed,.38)
 assert(exposed.player.hp<100,'Dodging along the bite line gives no invulnerability')
})

test('portrait sword can catch visible edge armor but not an offscreen Mite',()=>{
 const strike=(degrees,aspect,pitch)=>{
  const g=createGame(),heading=degrees*Math.PI/180
  Object.assign(g.player,{x:0,z:2})
  Object.assign(g.mite,{x:1.8*Math.sin(heading),z:2-1.8*Math.cos(heading),phase:'wake'})
  step(g,{attack:true,aspect,pitch})
  for(let i=0;i<8;i++)step(g,{aspect})
  assert.equal(g.mite.hp,70,'No damage before contact')
  step(g,{aspect});return g.mite.hp
 }
 for(const angle of [0,19,-19])assert.equal(strike(angle,402/874),46)
 for(const angle of [36,-36]){
  assert.equal(strike(angle,402/874),70)
  assert.equal(strike(angle,16/9),46,'Desktop still shows the target')
 }
 assert.equal(strike(0,402/874,.48),70,'Do not hit while looking above the armor')
 assert.equal(strike(180,16/9),70)
})
