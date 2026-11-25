// Exercise the calibrated C2 lift using the real MoverScriptDriver/SimHost.
// The shared stage flag is a rehearsal input, not a wave director.
import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const [fixture,out]=process.argv.slice(2)
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
const design=JSON.parse(readFileSync(new URL('../../project/layouts/wsc-scene-007-c2-pit.json',import.meta.url)))
const [x,z]=design.lift_x_z, rise=design.lift_rise
const atRest={x,y:0,z},euler={x:0,y:0,z:0}, rot={x:0,y:0,z:0,w:1}
const trigger={kind:'shared',field:1,equals:true}
const driver={kind:'track'}
// Lead-in and soft stop sampled with bounded track keys. Endpoints are exact.
const times=[0,.25,.6,1.25,1.9,2.25,2.5]
const ys=[0,.085,.436,2,3.564,3.915,rise]
const track={clip:'C2RevealLift',duration:2.5,loop:'once',speed:1,times,position:ys.map(y=>[x,y,z])}
const row={id:'c2-reveal-rehearsal',entity:2371,execution:'native',kind:'platform',at:atRest,euler,enabled:true,
  boxes:[{x:0,y:-.115,z:0,hx:3,hy:.115,hz:3,rot}],track,trigger,driver,
  ...lowerMoverMotion({track,trigger,driver},{at:atRest,euler})}
const movers=parseMovers([row])
const flag='c2RehearsalStage'
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
const navPath='server/c2-rehearsal-nav',nativePath='server/native-assembly.json'
const solids=[[55,0,218,8,8],[55,0,233,8,1],[48,0,229,4,3],[62,0,229,4,3],[55,-5.6,229,3.6,3.6]].map(([x,y,z,hx,hz],i)=>({
  id:'c2-tile-'+i,name:'C2 rehearsal floor '+i,file:'c2-rehearsal-only',active:true,surface:'metal',
  colliders:[{kind:'box',x,y:y-.3,z,hx,hy:.3,hz,rot}]
}))
const native=new TextEncoder().encode(JSON.stringify({kind:'native-assembly',
  level:{speed:4.3,ground:{size:500,height:-5.6}},terrain:{kind:'flat'},navigation:{file:navPath},
  entries:{proven:{lanes:0,steps:0,portalTransfers:0}},
  features:[{host:'collision.pieces',rows:{value:solids}}]}))
const p=base.product
const input={...base,product:{...p,hasFile:n=>n===nativePath||n===navPath||p.hasFile(n),
  file:n=>n===nativePath?Promise.resolve(native):n===navPath?Promise.resolve(nav()):p.file(n)}}
async function open(snapshot,installMover=true){
  let runtime
  const resident=await createNativeHeadlessResident(input,snapshot,{room:true,install:host=>{
    if(!installMover)return
    const s=p.shardfile
    runtime=new MoverScriptDriver(movers,host).install(host,
      {content:{identity:s.identity,sim:{...s.sim,bindings:[]},state:s.state},
        assets:new Map(),rules:{fields:{},archetypes:[],events:[],maxEntities:32}},
      {id:'c2.rehearsal.lift',restoring:!!snapshot,joined:true,drive:true,
        activation:{shared:n=>n===1?host.flags.has(flag):undefined}})
  }})
  return {resident,runtime,host:resident.host}
}
const describe=({host,runtime})=>{
  const p=host.players.get('actor.player'), g=tagOf(p.motor.result.groundCollider)
  const deck=runtime.pose(row.id)
  const owner=g?.owner
  return {tick:host.state.tick,y:deck.position.y,feet:p.position.toArray(),ground:p.fall.grounded,deckGround:owner===row.id||owner?.id===row.id}
}
const idle={kind:'player',moveX:0,moveZ:0,yaw:Math.PI}
const walk={...idle,moveZ:1}
const step=(run,n,cmd=idle)=>{for(let i=0;i<n;i++)run.resident.step([cmd])}
const setPlayer=(run,xx,yy,zz)=>{
  const p=run.host.players.get('actor.player')
  p.position.set(xx,yy,zz);p.motor.resetAt(p.position)
}
const live=await open()
let resumed,without
try{
  setPlayer(live,x,.035,z-4.3)
  step(live,25)
  step(live,57,walk)
  step(live,24)
  const rest=describe(live)
  console.log('rest',rest)
  assert(rest.y===0&&rest.deckGround&&rest.ground,'Player did not walk onto the flush lift')
  const cases=[rest]
  live.host.flags.set(flag)
  let ascentLosses=0, ascentFootError=0, previousY=0, firstTopTick=null
  const inspectAscent=now=>{
    assert(now.y>=previousY && now.y<=rise)
    previousY=now.y
    if(now.y===rise && firstTopTick===null)firstTopTick=now.tick-rest.tick
    if(!now.ground||!now.deckGround)ascentLosses++
    ascentFootError=Math.max(ascentFootError,Math.abs(now.feet[1]-now.y))
  }
  for(let i=0;i<75;i++) {
    step(live,1)
    const now=describe(live)
    inspectAscent(now)
    if((i+1)%15===0)cases.push(now)
  }
  const mid=describe(live)
  assert(Math.abs(mid.y-2)<.0002)
  const saved=snapshotSimHostBytes(live.host)
  resumed=await open(saved)
  assert(resumed.host.flags.has(flag))
  assert.deepEqual(describe(resumed).feet,mid.feet)
  assert.equal(describe(resumed).y,mid.y)
  let maxDelta=0,losses=0,maxSkin=0
  for(let i=0;i<115;i++){
    // Deassert only after the lift has reached its upper stop; it must hold.
    if(i===80){live.host.flags.clear(flag);resumed.host.flags.clear(flag)}
    step(live,1); step(resumed,1)
    const a=describe(live),b=describe(resumed)
    assert.equal(a.y,b.y)
    inspectAscent(a)
    if(!a.ground||!a.deckGround)losses++
    maxSkin=Math.max(maxSkin,Math.abs(a.feet[1]-a.y))
    maxDelta=Math.max(maxDelta,Math.hypot(...a.feet.map((v,j)=>v-b.feet[j])))
    if((i+1)%15===0)cases.push(a)
  }
  const end=describe(live)
  console.log('end',end,{mid,losses,maxSkin,maxDelta})
  assert(end.y===4 && end.deckGround && end.ground)
  assert(losses===0 && maxSkin<.075 && maxDelta<.003)
  assert(ascentLosses===0 && ascentFootError<.075 && firstTopTick>=149 && firstTopTick<=151)
  without=await open(undefined,false)
  setPlayer(without,x,.035,z-4.3)
  step(without,25); step(without,57,walk); step(without,85)
  const baselineFeet=without.host.players.get('actor.player').position.toArray()
  assert(Math.abs(baselineFeet[1]+5.58)<.03,'Without the mover the same walk must settle at the shaft floor')
  writeFileSync(out,JSON.stringify({scope:'Real engine mover/physics and save restore with a synthetic shared stage flag; no wave director, actor, native client or live deployment.',
    engine:'0.1.44',format:'0.43.0',worldOrigin:[x,0,z],row,rest,mid,end,losses,maxSkin,maxDelta,cases,
    ascentLosses,ascentFootError,firstTopTick,baselineFeet,checkedResumeTicks:115,clockHz:60,layout:design.donors_sha256},null,2)+'\n')
}finally{without?.resident.dispose();resumed?.resident.dispose();live.resident.dispose()}
