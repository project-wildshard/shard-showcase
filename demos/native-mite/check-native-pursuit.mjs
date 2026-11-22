import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const input=process.argv[2]
assert(input,'Pass the built native mite-calibration folder')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=dirname(req.resolve('@wildshard/engine/package.json'))
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
const sim=await HeadlessSimulation.create(shard,assets,undefined,{deadline:'advisory'})
function read(commit){
 const snap=decodeSimSnapshot(commit.snapshot)
 const actor=snap.entities.find(a=>a.id==='crate-mite:1')
 return {actor:actor?.state,player:snap.players[0],flags:snap.flags}
}
function health(p){const attrs=p.health.entries.find(([n])=>n==='attributes')[1];return attrs.entries.find(([n])=>n==='health')[1].value}
try{
 const start=read(await sim.step());assert(start.actor)
 const id='crate-mite:1'
 const evidence={ticks:0,walkMetres:0,minimumPlayerHp:health(start.player),miteWindup:false,miteBiteHit:false,overclockWindup:false,overclockHit:false}
 const observed=new Set()
 let state=start
 for(let i=0;i<920;i++){
  const p=state.player.position,m=state.actor?.position
  if(!m)break
  const dx=m[0]-p[0],dz=m[2]-p[2],range=Math.hypot(dx,dz)
  const follow=range>1.65?1/Math.max(.01,range):0
  const command={kind:'player',moveX:dx*follow,moveZ:dz*follow,yaw:Math.atan2(-dx,-dz)}
  const commit=await sim.step([{source:'mite-calibration.player',commands:[command]}])
  const snap=decodeSimSnapshot(commit.snapshot)
  const bite=snap.strikes.find(r=>r.id===id)
  if(bite&&bite.state.phase!=='idle')observed.add([bite.state.currentId,bite.state.phase,bite.state.hit].join(':'))
  state={player:snap.players[0],actor:snap.entities.find(a=>a.id===id)?.state}
  evidence.ticks=commit.tick
  evidence.walkMetres=Math.max(evidence.walkMetres,Math.hypot(state.player.position[0]-start.player.position[0],state.player.position[2]-start.player.position[2]))
  evidence.minimumPlayerHp=Math.min(evidence.minimumPlayerHp,health(state.player))
  evidence.miteWindup ||= bite?.state.currentId==='crate-mite.bite'&&bite.state.phase==='windup'
  evidence.miteBiteHit ||= bite?.state.currentId==='crate-mite.bite'&&bite.state.hit===true
  evidence.overclockWindup ||= bite?.state.currentId==='crate-mite.overclock'&&bite.state.phase==='windup'
  evidence.overclockHit ||= bite?.state.currentId==='crate-mite.overclock'&&bite.state.hit===true
  if(evidence.miteBiteHit&&evidence.overclockHit)break
 }
 console.log(JSON.stringify({...evidence,observed:[...observed]}))
 assert(evidence.walkMetres>8,'The native player did not walk to the pen')
 assert(evidence.miteWindup&&evidence.miteBiteHit&&evidence.overclockWindup&&evidence.overclockHit,'Both declared native Mite strikes must wind up and land')
 assert(evidence.minimumPlayerHp<health(start.player),'Player health did not change')
}finally{await sim.dispose()}
