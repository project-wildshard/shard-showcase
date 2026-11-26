// Native Station 4 deck-track rehearsal; arm is not a gameplay collider.
import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const [fixture,out,mode]=process.argv.slice(2)
assert(fixture&&out,'Pass an admitted plan folder and output JSON path')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const root=dirname(req.resolve('@wildshard/engine/package.json'))
const path=req.resolve('@wildshard/format/movers')
const motion=req.resolve('@wildshard/format/moverMotion')
const version=p=>JSON.parse(readFileSync(p)).version
assert.equal(version(join(root,'package.json')),'0.1.44')
assert.equal(version(join(dirname(path),'../../package.json')),'0.43.0')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {parseMovers}=await import(pathToFileURL(path).href)
const {lowerMoverMotion}=await import(pathToFileURL(motion).href)
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {loadCookedFolder}=await at('src/server/host/headlessFolder.ts')
const {createNativeHeadlessResident}=await at('src/server/host/headlessRuntime.ts')
const {MoverScriptDriver}=await at('src/server/game/plugin/mover.ts')
const {snapshotSimHostBytes}=await at('src/shared/engine/sim/snapshot.ts')
const {tagOf}=await at('src/shared/engine/physics/surface.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const base=await loadCookedFolder(fixture,R)
function nav() {
  // Small calibration tile; no NPCs or path queries in this isolated resident.
  const b=Buffer.alloc(120);let n=0
  const u32=v=>{b.writeUInt32LE(v,n);n+=4}
  const u16=v=>{b.writeUInt16LE(v,n);n+=2}
  const f=v=>{b.writeFloatLE(v,n);n+=4}
  const bytes=a=>{for(const x of a)b[n++]=x}
  bytes([87,83,78,77]);u32(1);u32(1)
  for(const x of [.38,1.8,.3,.25,.1,51,0,217,4])f(x)
  u32(1);u32(0);u32(0)
  for(const x of [51,0,217,55,1,221])f(x)
  u16(3);u16(1);u16(0);bytes([0,0,8,0,8,0]);u16(0);u16(0);u16(0)
  bytes([3,0,1,0,1,2,0,0,0,0,0])
  return b.subarray(0,n)
}
const design=JSON.parse(readFileSync(new URL('../../project/layouts/w6a-station4-spinner-check.json',import.meta.url)))
const mesh=readFileSync(new URL('../../public/assets/wildshard-art/wsc-kit-002-station4-spinner.glb',import.meta.url))
const sha=createHash('sha256').update(mesh).digest('hex')
assert.equal(sha,'d6eada249cb5b79d4e24de992678f063560f41fc7fa4cfc5892d8d7ee9a4a5e5')
const [x,,z]=design.gltf_world_m, y=design.deck_top_m
const atRest={x,y:y-.15,z},euler={x:0,y:0,z:0},rot={x:0,y:0,z:0,w:1}
const radius=design.disc_diameter_m/2
// Rehearsal only: the row format accepts cuboids. Use 32 tangent-safe
// strips entirely inside the 32-gon art's apothem, not a square collision pad.
const apothem=radius*Math.cos(Math.PI/32), pitch=apothem*2/32
const boxes=Array.from({length:32},(_,i)=>{
  const a=Math.max(-apothem,-apothem+i*pitch-.022),b=Math.min(apothem,-apothem+(i+1)*pitch+.022)
  const k=Math.max(Math.abs(a),Math.abs(b))
  const hx=Math.sqrt(Math.max(0,apothem**2-k**2))
  return {x:0,y:0,z:(a+b)/2,hx,hy:.15,hz:(b-a)/2,rot}
}).filter(b=>b.hx>1e-5)
const make=(speed)=>{
  const trigger={kind:'always'}, driver={kind:'track'}
  const duration=8,times=[0,2,4,6,8]
  const track={clip:'W6aRehearsalYaw',duration,loop:'repeat',speed:1,times,
    quaternion:times.map(t=>[0,Math.sin(t*speed/2),0,Math.cos(t*speed/2)])}
  return {id:'w6a-spinner-deck',entity:2372,execution:'native',kind:'platform',
    at:atRest,euler,enabled:true,boxes,track,trigger,driver,
    ...lowerMoverMotion({track,trigger,driver},{at:atRest,euler})}
}
const navPath='server/w6a-rehearsal-nav',nativePath='server/native-assembly.json'
const crossing=mode==='--handoff'
const block=([id,x,y,z,hx,hy,hz])=>({id,name:id,file:'w6a-rehearsal-only',active:true,surface:'metal',
  colliders:[{kind:'box',x,y,z,hx,hy,hz,rot}]})
const lip=['optional-lip',-152.995,5.85,-103,1.245,.15,3.0]
const solids=[
  ['arrival',-141,5.75,-103,1,.25,4],
  ['base',-147,-.15,-103,10,.15,8],
  ['axle',-147,6.45,-103,.226,.6,.226],
  ...(crossing?[['cage',-157,5.8,-103,2.75,.2,3.1]]:[]),
].map(block)
const native=addLip=>new TextEncoder().encode(JSON.stringify({kind:'native-assembly',
  level:{speed:4.3,ground:{size:500,height:0}},terrain:{kind:'flat'},navigation:{file:navPath},
  entries:{proven:{lanes:0,steps:0,portalTransfers:0}},features:[{host:'collision.pieces',rows:{value:addLip?[...solids,block(lip)]:solids}}]}))
const p=base.product
const input=addLip=>({...base,product:{...p,hasFile:n=>n===nativePath||n===navPath||p.hasFile(n),
  file:n=>n===nativePath?Promise.resolve(native(addLip)):n===navPath?Promise.resolve(nav()):p.file(n)}})
async function open(speed,snapshot,addLip=false){
  let runtime
  const row=make(speed)
  const resident=await createNativeHeadlessResident(input(addLip),snapshot,{room:true,install:host=>{
    const s=p.shardfile
    runtime=new MoverScriptDriver(parseMovers([row]),host).install(host,
      {content:{identity:s.identity,sim:{...s.sim,bindings:[]},state:s.state},
        assets:new Map(),rules:{fields:{},archetypes:[],events:[],maxEntities:32}},
      {id:'w6a.rehearsal.spinner',restoring:!!snapshot,joined:true,drive:true})
  }})
  return {resident,runtime,host:resident.host,row}
}
function describe({host,runtime,row}){
  const p=host.players.get('actor.player'), ground=p.motor.result.groundCollider
  const owner=tagOf(ground)?.owner
  const onDeck=owner===row.id||owner?.id===row.id
  const yaw=runtime.pose(row.id).euler.y
  const feet=p.position.toArray(),dx=feet[0]-x,dz=feet[2]-z
  return {tick:host.state.tick,yaw,feet,grounded:p.fall.grounded,onDeck,
    relativeXZ:[Math.cos(yaw)*dx-Math.sin(yaw)*dz,Math.sin(yaw)*dx+Math.cos(yaw)*dz]}
}
const idle={kind:'player',moveX:0,moveZ:0,yaw:0}
const step=(run,n,cmd=idle)=>{for(let i=0;i<n;i++)run.resident.step([cmd])}
function set(run,xx,yy,zz){
  const p=run.host.players.get('actor.player')
  p.position.set(xx,yy,zz)
  p.motor.resetAt(p.position)
}
const dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]))
const rate=Math.PI/4
if(crossing){
  const approach=async(addLip,dz,hold)=>{
    const run=await open(rate,undefined,addLip)
    try{
      set(run,-141.3,6.04,z+dz)
      step(run,24)
      const samples=[], mark=()=>{const q=describe(run);samples.push(q);return q}
      mark()
      const west={...idle,moveX:-1}
      let q,air=0
      for(let i=0;i<60;i++){
        step(run,1,west);q=mark();air+=!q.grounded
        if(q.onDeck)break
      }
      assert(q.onDeck&&air===0)
      for(let i=0;i<hold;i++){step(run,1);mark()}
      const carryEnd=describe(run)
      assert(carryEnd.onDeck)
      // Stage a world-space path south of the unchanged axle, then take
      // the west gap straight into the stationary bottom cage.
      const points=[[x+2.8,z+1.30],[x-2.8,z+1.30],[-156.15,z+1.30]]
      let reached=true
      for(const [tx,tz] of points){
        let reachedPoint=false
        for(let i=0;i<235;i++){
          q=describe(run)
          const dx=tx-q.feet[0],dzz=tz-q.feet[2],d=Math.hypot(dx,dzz)
          if(d<.12){reachedPoint=true;break}
          step(run,1,{...idle,moveX:dx/d,moveZ:dzz/d})
          q=mark()
          if(q.feet[1]<5.5)break
        }
        if(!reachedPoint){reached=false;break}
      }
      const final=describe(run)
      return {addLip,dz,hold,reached,airborne:samples.filter(q=>!q.grounded).length,carryEnd,final,samples}
    }finally{run.resident.dispose()}
  }
  const trials=[]
  for(const dz of [-.75,0,.75])for(const hold of [24,72])for(const enabled of [false,true])
    trials.push(await approach(enabled,dz,hold))
  for(const q of trials)
    console.log(q.addLip,q.dz,q.hold,q.reached,q.airborne,q.final.feet)
  for(const q of trials){
    assert.equal(q.reached,q.addLip)
    if(q.addLip){
      assert(q.airborne===0&&q.final.grounded&&!q.final.onDeck&&q.final.feet[0]<-155.8&&q.final.feet[1]>5.99)
    }else assert(q.airborne>0&&q.final.feet[1]<5.5)
  }
  assert.deepEqual(await approach(true,0,24),trials.find(r=>r.addLip&&r.dz===0&&r.hold===24))
  const trace={sha,origin:[x,y,z],lip,trials}
  const compact={scope:'Headless stock spinner, proposed fixed approach lip and stationary lower lift cage. No moving lift, arm collision or game install.',
    sha,origin:trace.origin,lip,repeatMatched:true,runs:trials.map(({samples,...q})=>({...q,ticks:samples.length-1}))}
  writeFileSync(out,JSON.stringify(compact,null,2)+'\n')
  if(process.argv[5])writeFileSync(process.argv[5],JSON.stringify(trace)+'\n')
  process.exit(0)
}
const spin=[]
for(const [r,angle] of [[.85,.2],[2,1],[3.3,2],[3.85,4.2]]) {
  const live=await open(rate)
  let resumed
  try {
    set(live,x+r*Math.cos(angle),6.04,z+r*Math.sin(angle))
    step(live,30)
    const initial=describe(live)
    assert(initial.grounded&&initial.onDeck,JSON.stringify(initial))
    const points=[initial]
    let losses=0,maxLocalDrift=0,maxRestoreDelta=0,maxRestoreYaw=0,travel=0
    let prev=initial
    for(let k=1;k<=600;k++){
      step(live,1)
      const s=describe(live)
      losses+=!s.grounded||!s.onDeck
      travel+=dist(s.feet,prev.feet)
      prev=s
      maxLocalDrift=Math.max(maxLocalDrift,dist(s.relativeXZ,initial.relativeXZ))
      if(k%60===0)points.push(s)
      if(r===3.3&&k===211)resumed=await open(rate,snapshotSimHostBytes(live.host))
      else if(resumed){
        step(resumed,1)
        const rs=describe(resumed)
        assert.equal(rs.onDeck,s.onDeck)
        maxRestoreDelta=Math.max(maxRestoreDelta,dist(rs.feet,s.feet))
        maxRestoreYaw=Math.max(maxRestoreYaw,Math.abs(rs.yaw-s.yaw))
      }
    }
    console.log({r,losses,maxLocalDrift,maxRestoreDelta,maxRestoreYaw,travel})
    assert.equal(losses,0)
    assert(maxLocalDrift<.05&&maxRestoreDelta<.002&&maxRestoreYaw<1e-6)
    assert(travel>r*7)
    spin.push({r,angle,shots:points,yawRateRadSec:rate,losses,maxLocalDrift,maxRestoreDelta,maxRestoreYaw,travel,
      resumeTicks:r===3.3?389:0})
  }finally{resumed?.resident.dispose();live.resident.dispose()}
}
const fixed=await open(0)
let control
try{
  set(fixed,x+3.3,6.04,z)
  step(fixed,30)
  const initial=describe(fixed)
  step(fixed,600)
  const final=describe(fixed)
  control={initial,final,worldDistance:dist(initial.feet,final.feet)}
  assert(initial.onDeck&&final.onDeck&&control.worldDistance<.001)
}finally{fixed.resident.dispose()}

const entries=[]
for(const dz of [0,.75,-.75]){
  for(const [jump,spinEnabled] of [[false,true],[true,true],[true,false]]){
    const live=await open(spinEnabled?rate:0)
    try {
      set(live,-141.3,6.04,z+dz)
      step(live,24)
      assert(describe(live).grounded && !describe(live).onDeck)
      const start=describe(live)
      const enter={...idle,moveX:-1}
      let firstDeck=null,maxY=0,air=0
      const segments=[start.feet]
      for(let k=0;k<85;k++){
        step(live,1,{...enter,jump:jump&&k===10})
        const s=describe(live)
        maxY=Math.max(maxY,s.feet[1])
        if(k%4===0) segments.push(s.feet)
        air+=!s.grounded
        if(s.onDeck){firstDeck={k,...s};segments.push(s.feet);break}
      }
      if(firstDeck) step(live,48)
      const final=describe(live)
      entries.push({dz,jump,spinEnabled,start,firstDeck,final,maxY,air,segments})
      console.log('entry',dz,jump,spinEnabled,firstDeck?.k,final.feet,final.onDeck)
    } finally {live.resident.dispose()}
  }
}
assert(entries.filter(a=>!a.jump).every(a=>a.firstDeck&&a.final.onDeck))
assert(entries.filter(a=>a.jump).every(a=>a.firstDeck&&!a.final.grounded&&!a.final.onDeck))
writeFileSync(out,JSON.stringify({scope:'Stock MoverScriptDriver and character carry in a headless rehearsal. Collider is an inscribed cuboid strip approximation of the 9 m disc; original mesh unchanged. No sweep arm shove, live install, phone or timer.',
  engine:'0.1.44',format:'0.43.0',sha,clockHz:60,origin:[x,y,z],row:make(rate),spin,control,entries},null,2)+'\n')
