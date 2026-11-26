import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [file,traceFile]=process.argv.slice(2)
assert(file&&traceFile)
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(engine)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(engine),p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const threeRoot=dirname(req.resolve('three'))
const {AnimationMixer,LoopOnce,Vector3}=await import(pathToFileURL(join(threeRoot,'../build/three.module.js')))
const {GLTFLoader}=await import(pathToFileURL(join(threeRoot,'../examples/jsm/loaders/GLTFLoader.js')))
const root=new URL('../../',import.meta.url)
const assets=new URL('public/assets/wildshard-art/',root)
const model='e5b-alarm-gate-pair-motion.glb'
const donor=readFileSync(new URL(model,assets))
const hash=createHash('sha256').update(donor).digest('hex')
assert.equal(hash,'f79ae9baf004cc550db96aa6568a1a5194f04c32e8cac9a1557d07235a184d06')
const fit=JSON.parse(readFileSync(new URL('project/layouts/e5b-alarm-gate-fit.json',root)))
const glb=await new GLTFLoader().parseAsync(donor.buffer.slice(donor.byteOffset,donor.byteOffset+donor.byteLength),'')
const {scene,animations}=glb
const leaves=['AlarmLeafLeft','AlarmLeafRight'].map(n=>scene.getObjectByName(n))
assert(leaves.every(Boolean)&&leaves.every(o=>o.children.length===20))
scene.updateMatrixWorld(true)
const geometry=leaves.map(leaf=>{
 const verts=[],ids=[],v=new Vector3()
 leaf.traverse(o=>{
  if(!o.isMesh)return
  const off=verts.length/3,p=o.geometry.getAttribute('position')
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld).sub(leaf.position);verts.push(v.x,v.y,v.z)}
  const n=o.geometry.index?.count??p.count
  for(let i=0;i<n;i++)ids.push(off+(o.geometry.index?o.geometry.index.getX(i):i))
 })
 assert.equal(ids.length/3,736)
 return {verts,ids}
})
const timeline={}, mixer=new AnimationMixer(scene)
for(const [mode,ticks] of Object.entries({close:144,open:168})){
 const clip=animations.find(a=>a.name==='Alarm_gate_'+mode)
 assert(Math.abs(clip.duration-ticks/60)<1e-6)
 const act=mixer.clipAction(clip);act.setLoop(LoopOnce,1);act.clampWhenFinished=true;act.play()
 timeline[mode]=Array.from({length:ticks+1},(_,i)=>{
   mixer.setTime(Math.min(i/60,clip.duration));return leaves.map(o=>o.position.toArray())
 })
 act.stop()
}
const maxDiff=(a,b)=>Math.max(...a.flat().map((x,i)=>Math.abs(x-b.flat()[i])))
assert(maxDiff(timeline.close[0],timeline.open.at(-1))<1e-5)
assert(maxDiff(timeline.close.at(-1),timeline.open[0])<1e-5)
const xyz=(x,y,z)=>({x,y,z}), round=x=>+x.toFixed(6)
function trial(name,mode,offset){
 const origin=fit.origins_world_xyz[name], yaw=fit[name+'_yaw_degrees']*Math.PI/180, c=Math.cos(yaw),s=Math.sin(yaw)
 const world=([x,y,z])=>xyz(x*c+z*s+origin[0],y+origin[1],z*c-x*s+origin[2])
 const local=(p)=>{const x=p.x-origin[0],z=p.z-origin[2];return [x*c-z*s,p.y-origin[1],z*c+x*s]}
 const isSlab=mode.startsWith('slab')
 const sim=new SimHost({version:SIM_API_VERSION,id:'e5b-alarm-gate-witness',seed:84,ground:{size:500,height:0},
  player:{at:world([offset,.03,-3.9]),yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
 try{
  const w=sim.physics.world
  const stamp=xyz(origin[0],-.5,origin[2]);const groupsWorld=groups('WORLD')
  w.createCollider(R.ColliderDesc.cuboid(24,.5,20).setTranslation(stamp.x,stamp.y,stamp.z).setCollisionGroups(groupsWorld))
  const bodies=geometry.map(({verts,ids},i)=>{
   const p=world(timeline.close[0][i])
   const rot={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)}
   const b=w.createRigidBody(R.RigidBodyDesc.kinematicPositionBased().setTranslation(p.x,p.y,p.z).setRotation(rot))
   if(!isSlab)w.createCollider(R.ColliderDesc.trimesh(new Float32Array(verts),new Uint32Array(ids)).setCollisionGroups(groupsWorld),b)
   return b
  })
  // Alternative receiver contract: leave the exact mesh visual-only and use
  // one non-travelling blocker during the fully shut phase. No moving carrier.
  let blocker=null
  const player=sim.players.get('actor.player')
  assert.equal(player.motor.opts.radius,.38)
  const dir=new Map([[player.id,{moveX:s,moveZ:c,yaw:0}]])
  let airborne=0, peakY=0, minY=Infinity
  const walk=(n,useDir)=>{for(let j=0;j<n;j++){sim.step(useDir?dir:undefined);airborne+=!player.fall.grounded;peakY=Math.max(peakY,player.position.y);minY=Math.min(minY,player.position.y)}}
  const feet=()=>local(player.position).map(round)
  const sample=(phase)=>({phase,airborne,peakY:round(peakY),minY:Number.isFinite(minY)?round(minY):null,tick:sim.state.tick,feet:feet(),leafX:bodies.map(b=>round(local(b.translation())[0]))})
  const set=(pose)=>bodies.forEach((b,i)=>b.setNextKinematicTranslation(world(pose[i])))
  walk(25,false);assert(player.fall.grounded);airborne=0;peakY=0;minY=Infinity
  if(mode==='clear'){
   walk(115,true)
   assert(feet()[2]>3.7 && airborne===0,feet())
   return {name,mode,offset,airborne,openOnly:sample('open pass')}
  }
  if(mode==='occupied'){
   // Start from the open side and request closure as the real motor enters the plane.
   walk(53,true);assert(Math.abs(feet()[2])<.5,feet())
  }
  const request=sample('alarm request')
  let deferred=0
  // Fixture interlock, intentionally conservative. It waits until the
  // player is outside the full swept doorway slab, not just the centre gap.
  while(Math.abs(feet()[2])<1.05&&Math.abs(feet()[0])<8.5){
   walk(1,true);deferred++
   assert(deferred<40,'Doorway did not clear')
  }
  const clear=sample('closure starts')
  assert(mode==='occupied'?deferred>0:deferred===0)
  for(let i=1;i<=144;i++){
   set(timeline.close[i]);walk(1,false)
  }
  if(isSlab){
   const mid=world([0,1.9,0])
   blocker=w.createCollider(R.ColliderDesc.cuboid(8.12,1.9,.135)
    .setTranslation(mid.x,mid.y,mid.z).setRotation({x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)})
    .setCollisionGroups(groupsWorld))
  }
  const closed=sample('fully closed')
  assert.equal(closed.tick-clear.tick,144)
  assert(closed.leafX.every((x,i)=>Math.abs(x-timeline.close.at(-1)[i][0])<1e-5))
  if(mode==='occupied'){
   assert(feet()[2]>1 && airborne===0)
   return {name,mode,offset,airborne,deferred,request,clear,closed}
  }
  walk(120,true);const denied=sample('blocked walk')
  assert(denied.feet[2]>-.9&&denied.feet[2]<-.38,denied.feet)
  const retreat=new Map([[player.id,{moveX:-s,moveZ:-c,yaw:0}]])
  if(mode==='cycle'){
   for(let j=0;j<25;j++){sim.step(retreat);airborne+=!player.fall.grounded}
   assert(feet()[2]<-1.8)
  }
  walk(mode==='cycle'?1055:1080,false);const endHold=sample('hold ends')
  assert.equal(endHold.tick-closed.tick,1200)
  assert.deepEqual(endHold.leafX,closed.leafX)
  assert(endHold.feet[2]<-.38)
  let passDuringOpen=null, releaseTick=null
  for(let i=1;i<=168;i++){
   set(timeline.open[i])
   const gap=timeline.open[i][1][0]-timeline.open[i][0][0]-7.98
   if(blocker?.isEnabled()&&gap>=2.05){blocker.setEnabled(false);releaseTick=i}
   walk(1,mode==='slab-held')
   if(mode==='slab-held'&&passDuringOpen===null&&feet()[2]>0){
    assert(gap>2.05)
    passDuringOpen={tick:i,gap:round(gap),feet:feet()}
   }
  }
  const opened=sample('fully open')
  assert.equal(opened.tick-endHold.tick,168)
  walk(130,true);const crossed=sample('post-open walk')
  const drift=round(opened.feet[0]-endHold.feet[0])
  if(mode==='cycle')assert(crossed.feet[2]>6&&crossed.airborne===opened.airborne&&peakY<.3&&Math.abs(drift)<.003,JSON.stringify({crossed,airborne,drift}))
  if(isSlab)assert(crossed.feet[2]>6&&airborne===0&&Math.abs(drift)<.003,crossed.feet)
  if(mode==='slab-held')assert(passDuringOpen&&passDuringOpen.tick>releaseTick)
  return {name,mode,offset,airborne,deferred,request,clear,closed,denied,endHold,opened,crossed,drift,releaseTick,passDuringOpen,
    crossedWithOriginalInput:crossed.feet[2]>6}
 }finally{sim.dispose()}
}
const runs=Object.keys(fit.origins_world_xyz).flatMap(name=>[
 ...[-.53,0,.53].flatMap(x=>[trial(name,'cycle',x),trial(name,'clear',x)]),
 trial(name,'occupied',0),...[-.53,0,.53].map(x=>[trial(name,'cycle-near',x),trial(name,'slab',x),trial(name,'slab-held',x)]).flat()
])
const sample=runs.find(r=>r.name==='north'&&r.mode==='cycle'&&r.offset===0)
const atNorth=(mode)=>(runs.find(r=>r.name==='north'&&r.mode===mode&&r.offset===0))
assert(runs.filter(r=>r.mode==='cycle-near'&&!r.crossedWithOriginalInput).length===4)
assert(Math.max(...runs.filter(r=>r.mode==='cycle-near').map(r=>Math.abs(r.drift)))>8)
assert.deepEqual(sample,trial('north','cycle',0))
const summary={scope:'Stock player test on flat floor comparing exact kinematic gate triangle pairs with a fixed blocker; fixture alarm and interlock only.',
 engine:'0.1.44',model,sha256:hash,anchors:fit.origins_world_xyz,releaseGapM:2.05,closeTicks:144,holdTicks:1200,openTicks:168,hz:60,runs}
writeFileSync(file,JSON.stringify(summary,null,2)+'\n')
writeFileSync(traceFile,JSON.stringify({cycle:sample,near:atNorth('cycle-near'),slab:atNorth('slab-held'),blockedWindow:atNorth('occupied')},null,2)+'\n')
console.table(runs.map(({name,mode,offset,deferred,airborne,denied,crossed})=>({name,mode,offset,deferred,airborne,denied:denied?.feet[2],crossed:crossed?.feet[2]})))
