// Isolated Deck A collision and stock ladder behavior; no production change.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const [fixture, output] = process.argv.slice(2)
assert(fixture && output, 'Pass a local admitted calibration product and output JSON path')
const req = createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT), 'package.json') : import.meta.url)
const engine = dirname(req.resolve('@wildshard/engine/package.json'))
const fmt = req.resolve('@wildshard/format/modes')
const version = p => JSON.parse(readFileSync(p, 'utf8')).version
assert.equal(version(join(engine, 'package.json')), '0.1.44')
assert.equal(version(join(dirname(fmt), '../../package.json')), '0.43.0')
const at = p => import(pathToFileURL(join(engine, p)).href)
await at('scripts/sim-node-loader.mjs')
const { parse } = await import(pathToFileURL(req.resolve('valibot')).href)
const { LadderModeSchema } = await import(pathToFileURL(fmt).href)
const { loadRapier } = await at('src/shared/engine/physics/rapier.ts')
const { loadCookedFolder } = await at('src/server/host/headlessFolder.ts')
const { openWorldAdapter } = await at('src/server/host/openWorld.ts')
const { createNativeHeadlessResident } = await at('src/server/host/headlessRuntime.ts')
const { installLadders } = await at('src/shared/game/shardfile/ladder.ts')
const { snapshotSimHostBytes } = await at('src/shared/engine/sim/snapshot.ts')
const { tagOf } = await at('src/shared/engine/physics/surface.ts')
const wasm = join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')
const rapier = await loadRapier(readFileSync(wasm))
const base = await loadCookedFolder(fixture, rapier)
const product = base.product

// assemble.py: x=-166, z=28, visible rail z=31.4, floor y=.0275,
// outer deck beam ends at z=31.35, and outermost tread at z=31.23.
// Put the capsule track outside the beam, and land atop the actual planks.
const x = -166, floor = .0275, rim = 31.23
const normal = {x:0,z:1}
const route = parse(LadderModeSchema, {kind:'ladder',id:'w8a-deck-a',normal,reach:.9,speed:2,
  bottom:{x,y:floor,z:31.78},top:{x,y:6.035,z:31.78},exit:{x,y:6.035,z:30.93}})
const nativePath = 'server/native-assembly.json', navPath = 'server/w8a-bench-nav'
function nav() {
  const b = Buffer.alloc(120); let n = 0
  const u32 = v => { b.writeUInt32LE(v,n); n+=4 }
  const u16 = v => { b.writeUInt16LE(v,n); n+=2 }
  const f = v => { b.writeFloatLE(v,n); n+=4 }
  const bytes = a => { for (const x of a) b[n++]=x }
  bytes([87,83,78,77]);u32(1);u32(1)
  for(const x of [.38,1.8,.3,.25,.1,-168,0,27,4])f(x)
  u32(1);u32(0);u32(0)
  for(const x of [-168,0,27,-164,1,31])f(x)
  u16(3);u16(1);u16(0);bytes([0,0,8,0,8,0]);u16(0);u16(0);u16(0)
  bytes([3,0,1,0,1,2,0,0,0,0,0])
  return b.subarray(0,n)
}
const rot={x:0,y:0,z:0,w:1}
const box=(x,y,z,hx,hy,hz)=>({kind:'box',x,y,z,hx,hy,hz,rot})
const piece=(id,surface,colliders)=>({id,name:id,file:'w8a-bench-only',active:true,surface,colliders})
const boards = Array.from({length:12},(_,j)=>box(x,5.915,28+(j-5.5)*.54,3.3,.085,.26))
const guards = []
for (const [a,b] of [[-3.15,-.75],[.75,3.15]]) {
  for (const dx of [a,b]) guards.push(box(x+dx,6.54,31.2,.035,.54,.035))
  for (const y of [6.55,7.02]) guards.push(box(x+(a+b)/2,y,31.2,(b-a)/2,.024,.024))
}
const pieces=[
  piece('deck-a-ground','stone',[box(x,floor-.2,31.5,12,.2,12)]),
  piece('deck-a','wood',[box(x,5.68,28,3.3,.16,3.35),...boards]),
  piece('deck-a-opening','wood',guards),
]
const native=Buffer.from(JSON.stringify({kind:'native-assembly',level:{speed:4.3,ground:{size:500,height:0}},
  terrain:{kind:'flat'},navigation:{file:navPath},entries:{proven:{lanes:0,steps:0,portalTransfers:0}},
  features:[{host:'collision.pieces',rows:{value:pieces}}]}))
const input={...base,product:{...product,
  shardfile:{...product.shardfile,modes:{...product.shardfile.modes,traverse:[route]}},
  hasFile:n=>n===nativePath||n===navPath||product.hasFile(n),
  file:n=>n===nativePath?Promise.resolve(native):n===navPath?Promise.resolve(nav()):product.file(n)}}
const idle={kind:'player',moveX:0,moveZ:0,yaw:0}, up={...idle,moveZ:-1}, down={...idle,moveZ:1,yaw:Math.PI}
const describe=run=>{
  const p=run.host.players.get('actor.player')
  const g=tagOf(p.motor.result.groundCollider)
  return {tick:run.host.state.tick,feet:p.position.toArray(),ground:p.fall.grounded,contact:typeof g?.owner==='string'?g.owner:g?.owner?.id??null}
}
const setFeet=(run, xx, yy, zz)=>{
  const p=run.host.players.get('actor.player')
  p.position.set(xx,yy,zz);p.motor.resetAt(p.position)
}
const step=(run,cmd,n=1)=>{for(let i=0;i<n;i++)run.step([cmd]);return describe(run)}
const start=run=>{setFeet(run,x,.065,33.35);return step(run,idle,25)}
const normalHost=await openWorldAdapter(input)
let proof, resumed, release, gated
try {
  start(normalHost)
  const nativeTrace=Array.from({length:280},()=>step(normalHost,up))
  const nativeMax=Math.max(...nativeTrace.map(x=>x.feet[1]))
  setFeet(normalHost,x,6.035,30.943)
  step(normalHost,idle,6)
  const nativeDown=Array.from({length:130},()=>step(normalHost,down))
  const unsupportedFall=Math.max(...nativeDown.slice(1).map((f,i)=>nativeDown[i].feet[1]-f.feet[1]))
  assert(unsupportedFall>.08 && nativeDown.some(f=>f.feet[1]<.09 && f.ground))
  // Keep the native room result separate from the stock mode behind a test installer.
  if(nativeMax>1) throw new Error('Normal room now installs the route; rebase this bench onto it')
  const open=(save)=>createNativeHeadlessResident(input,save,{room:true,install:host=>installLadders(host,[route])})
  proof=await open()
  const bottom=start(proof), samples=[bottom]
  let attach, mid, top, landed, restoredTicks=0, error=0
  for(let i=0;i<360;i++){
    const f=step(proof,up)
    if(i%10===0)samples.push(f)
    if(!attach && f.feet[1]>.15)attach=f
    if(!mid && f.feet[1]>=3){
      mid=f
      resumed=await open(snapshotSimHostBytes(proof.host))
      assert.deepEqual(describe(resumed).feet,mid.feet)
    } else if(resumed) {
      const a=step(resumed,up)
      error=Math.max(error,Math.hypot(...f.feet.map((v,j)=>v-a.feet[j])))
      restoredTicks++
    }
    if(!top && f.feet[1]>=6.02)top=f
    if(f.feet[1]>5.98 && f.feet[2]<rim-.05 && f.ground && f.contact==='deck-a'){landed=f;break}
  }
  console.log('ascent',{nativeMax,bottom,attach,mid,top,landed,error,restoredTicks,last:describe(proof)})
  assert(attach&&mid&&top&&landed&&error<.00001&&restoredTicks>65,'Capsule did not climb/land or restore diverged')
  step(proof,idle,5)
  let low, descending, descentPeak=0, steadyDescentPeak=0, alignDescent, prev=describe(proof), descendingTicks=0
  for(let i=0;i<360;i++){
    const f=step(proof,down)
    const drop=prev.feet[1]-f.feet[1]
    prev=f
    descentPeak=Math.max(descentPeak,drop)
    if(drop>.02)descendingTicks++
    if(alignDescent&&f.feet[1]>.20)steadyDescentPeak=Math.max(steadyDescentPeak,drop)
    if(!alignDescent && Math.abs(f.feet[2]-route.top.z)<.001)alignDescent=f
    if(!descending && f.feet[1]<5.8)descending=f
    if(f.feet[1]<.09&&f.ground){low=f;break}
  }
  console.log('descent',{descending,low,descentPeak,descendingTicks,unsupportedFall,last:describe(proof)})
  assert(descending && alignDescent && low?.contact==='deck-a-ground' && descendingTicks>=170)
  assert(descentPeak<.09 && steadyDescentPeak<.04,
    'Deck edge handoff or aligned descent exceeded the measured envelope')
  release=await open()
  start(release)
  for(let i=0;i<200&&describe(release).feet[1]<2;i++)step(release,up)
  const held=describe(release), still=step(release,idle,30)
  assert(held.feet[1]>=2 && Math.abs(held.feet[1]-still.feet[1])<.001,'Neutral drift')
  step(release,{...idle,jump:true})
  const released=step(release,idle,100)
  assert(released.ground&&released.feet[1]<.1)
  gated=await open()
  setFeet(gated,x+1.5,.065,33.35);step(gated,idle,25)
  const off=Array.from({length:240},()=>step(gated,up))
  assert(Math.max(...off.map(f=>f.feet[1]))<.15,'Off-center approach attached')
  const result={versions:{engine:'0.1.44',format:'0.43.0'},route,deckRim:rim,
    normalRoom:{maxFeetY:nativeMax,installedLadder:false,peakDropPerTick:unsupportedFall},
    explicitStockInstaller:{bottom,attach,mid,top,landed,descending,low,still,released,restoredTicks,maxRestoreErrorMeters:error,descendingTicks,descentPeakMetersPerTick:descentPeak,alignedPeakMetersPerTick:steadyDescentPeak,alignedAt:alignDescent}, samples}
  writeFileSync(output,JSON.stringify(result,null,2)+'\n')
}finally{
  for(const room of [normalHost,proof,resumed,release,gated])room?.dispose()
}
