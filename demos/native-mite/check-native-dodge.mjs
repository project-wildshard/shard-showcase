import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const input=process.argv[2]
assert(input,'Pass the built native mite-calibration folder')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=dirname(req.resolve('@wildshard/engine/package.json'))
assert.equal(JSON.parse(await readFile(join(engine,'package.json'),'utf8')).version,'0.1.44')
await import(pathToFileURL(join(engine,'scripts/sim-node-loader.mjs')).href)
const load=name=>import(pathToFileURL(req.resolve('@wildshard/engine/'+name)).href)
const {HeadlessSimulation}=await load('host/headless')
const {loadHeadlessFolder}=await load('host/headlessFolder')
const {folderClosureFile}=await load('game/shardfile/shardFolder')
const {decodeSimSnapshot}=await load('sim/snapshot')
const product=await loadHeadlessFolder(input)
const shard=product.shardfile
const refs=[...shard.files.map(f=>f.hash),...shard.requires.commons.map(h=>'commons:'+h)]
const assets=new Map(await Promise.all(refs.map(async h=>[h,await folderClosureFile(product,h)])))
assert.equal(shard.items.loadout.primary,'weapon.sword-iron')
assert.equal(shard.creatures.spawns.filter(s=>s.species==='crate-mite').length,1)
function health(p){const attrs=p.health.entries.find(([n])=>n==='attributes')[1];return attrs.entries.find(([n])=>n==='health')[1].value}
const mob='crate-mite:1'
const strikeOf=snap=>snap.strikes.find(s=>s.id===mob)?.state
const hp=snap=>health(snap.players[0])
const pos=snap=>snap.players[0].position
const commitSnap=commit=>decodeSimSnapshot(commit.snapshot)
const reactionTicks=15 // 250 ms at the calibration sim's 60 ticks per second.
async function trial(kind,sign){
 const sim=await HeadlessSimulation.create(shard,assets,undefined,{deadline:'advisory'})
 const id='crate-mite.'+kind
 const command=(moveX,moveZ,yaw)=>[{source:'mite-calibration.player',commands:[{kind:'player',moveX,moveZ,yaw}]}]
 try{
  let commit=await sim.step(),snap=commitSnap(commit)
  for(let i=0;i<920;i++){
   const s=strikeOf(snap)
   if(s?.currentId===id&&s.phase==='windup')break
   const p=pos(snap),m=snap.entities.find(a=>a.id===mob)?.state.position
   assert(m,'Mite is missing')
   const dx=m[0]-p[0],dz=m[2]-p[2],range=Math.hypot(dx,dz)
   const walk=range>1.65?1/Math.max(.01,range):0
   commit=await sim.step(command(dx*walk,dz*walk,Math.atan2(-dx,-dz)))
   snap=commitSnap(commit)
  }
  const s=strikeOf(snap)
  assert(s?.currentId===id&&s.phase==='windup','Never saw '+id)
  const start=commit.tick,initial=hp(snap)
  const lane=[s.x0,s.z0,s.x1,s.z1]
  const vx=lane[2]-lane[0],vz=lane[3]-lane[1],length=Math.hypot(vx,vz)
  assert(length>0)
  const nx=-vz/length,nz=vx/length
  const offset=p=>(p[0]-lane[0])*nx+(p[2]-lane[1])*nz
  let activeAt,recoverAt,firstActiveOffset,changedLane=false,hit=false
  // Script only the player's movement; the native runner owns the hit and phase edges.
  for(let i=0;i<180;i++){
   const side=sign&&i>=reactionTicks&&sign*offset(pos(snap))<1.25?sign:0
   commit=await sim.step(command(nx*side,nz*side,Math.atan2(-vx,-vz)))
   snap=commitSnap(commit)
   const current=strikeOf(snap)
   assert.equal(current?.currentId,id,'Strike changed before recovery')
   if(current.phase==='windup')changedLane ||= [current.x0,current.z0,current.x1,current.z1].some((p,j)=>p!==lane[j])
   hit ||= current.hit
   if(current.phase==='active'&&activeAt===undefined){
    activeAt=commit.tick;firstActiveOffset=offset(pos(snap))
   }
   if(current.phase==='recover'){recoverAt=commit.tick;break}
  }
  assert(activeAt&&recoverAt,'Strike must reach active then recover')
  return {kind,start,control:!sign,lane,changedLane,hit,initial,final:hp(snap),
    windupTicks:activeAt-start,activeTicks:recoverAt-activeAt,firstActiveOffset,
    finalOffset:offset(pos(snap))}
 }finally{await sim.dispose()}
}
for(const kind of ['bite','overclock']){
 const control=await trial(kind,0),dodge=await trial(kind,1)
 console.log(JSON.stringify({reactionTicks,control,dodge}))
 assert.equal(control.start,dodge.start)
 assert.equal(control.initial,dodge.initial)
 assert.deepEqual(control.lane,dodge.lane)
 assert.equal(control.changedLane||dodge.changedLane,false)
 assert(control.hit&&control.final<control.initial,'Stationary control must lose health')
 assert(Math.abs(dodge.firstActiveOffset)>=1.2,'Sidestep did not clear the lane before active')
 assert(!dodge.hit&&dodge.final===dodge.initial,'Sidestep must avoid damage into recovery')
}
