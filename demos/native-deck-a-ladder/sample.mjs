// Isolated Climb Yard deck colliders and stock ladder behavior; no production change.
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

// The deck centers and repeated 6.6 m wide plank kit match assemble.py.
const letter=process.env.WSC_CLIMB_DECK || 'A'
const layout={A:[-166,28,6],B:[-146,44,10],C:[-170,60,14]}
assert(Object.hasOwn(layout,letter),'Choose deck A, B or C')
const [x,z,h]=layout[letter], floor=.0275
const id='deck-'+letter.toLowerCase()
const rim=z+3.23, approach=z+5.35, lane=z+3.78, exitZ=z+2.93
const walkY=h+.035, maxTicks=160+Math.ceil(h*60/2)
const normal={x:0,z:1}
const route=parse(LadderModeSchema,{kind:'ladder',id:'w8a-'+id,normal,reach:.9,speed:2,
  bottom:{x,y:floor,z:lane},top:{x,y:walkY,z:lane},exit:{x,y:walkY,z:exitZ}})
const nativePath = 'server/native-assembly.json', navPath = 'server/w8a-bench-nav'
function nav() {
  const b = Buffer.alloc(120); let n = 0
  const u32 = v => { b.writeUInt32LE(v,n); n+=4 }
  const u16 = v => { b.writeUInt16LE(v,n); n+=2 }
  const f = v => { b.writeFloatLE(v,n); n+=4 }
  const bytes = a => { for (const x of a) b[n++]=x }
  bytes([87,83,78,77]);u32(1);u32(1)
  for(const v of [.38,1.8,.3,.25,.1,x-2,0,z-1,4])f(v)
  u32(1);u32(0);u32(0)
  for(const v of [x-2,0,z-1,x+2,1,z+3])f(v)
  u16(3);u16(1);u16(0);bytes([0,0,8,0,8,0]);u16(0);u16(0);u16(0)
  bytes([3,0,1,0,1,2,0,0,0,0,0])
  return b.subarray(0,n)
}
const rot={x:0,y:0,z:0,w:1}
const box=(x,y,z,hx,hy,hz)=>({kind:'box',x,y,z,hx,hy,hz,rot})
const piece=(id,surface,colliders)=>({id,name:id,file:'w8a-bench-only',active:true,surface,colliders})
const boards = Array.from({length:12},(_,j)=>box(x,h-.085,z+(j-5.5)*.54,3.3,.085,.26))
const guards = []
for (const [a,b] of [[-3.15,-.75],[.75,3.15]]) {
  for (const dx of [a,b]) guards.push(box(x+dx,h+.54,z+3.2,.035,.54,.035))
  for (const y of [h+.55,h+1.02]) guards.push(box(x+(a+b)/2,y,z+3.2,(b-a)/2,.024,.024))
}
const pieces=[
  piece(id+'-ground','stone',[box(x,floor-.2,z+3.5,12,.2,12)]),
  piece(id,'wood',[box(x,h-.32,z,3.3,.16,3.35),...boards]),
  piece(id+'-opening','wood',guards),
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
const start=run=>{setFeet(run,x,.065,approach);return step(run,idle,25)}
const normalHost=await openWorldAdapter(input)
let proof, resumed, release, gated
try {
  start(normalHost)
  const nativeTrace=Array.from({length:280},()=>step(normalHost,up))
  const nativeMax=Math.max(...nativeTrace.map(x=>x.feet[1]))
  setFeet(normalHost,x,walkY,exitZ+.013)
  step(normalHost,idle,6)
  const nativeDown=Array.from({length:Math.max(130,Math.ceil(65+h*6))},()=>step(normalHost,down))
  const unsupportedFall=Math.max(...nativeDown.slice(1).map((f,i)=>nativeDown[i].feet[1]-f.feet[1]))
  assert(unsupportedFall>.08 && nativeDown.some(f=>f.feet[1]<.09 && f.ground))
  // Keep the native room result separate from the stock mode behind a test installer.
  if(nativeMax>1) throw new Error('Normal room now installs the route; rebase this bench onto it')
  const open=(save)=>createNativeHeadlessResident(input,save,{room:true,install:host=>installLadders(host,[route])})
  proof=await open()
  const bottom=start(proof), samples=[bottom]
  let attach, mid, top, landed, restoredTicks=0, error=0
  for(let i=0;i<maxTicks;i++){
    const f=step(proof,up)
    if(i%10===0)samples.push(f)
    if(!attach && f.feet[1]>.15)attach=f
    if(!mid && f.feet[1]>=h/2){
      mid=f
      resumed=await open(snapshotSimHostBytes(proof.host))
      assert.deepEqual(describe(resumed).feet,mid.feet)
    } else if(resumed) {
      const a=step(resumed,up)
      error=Math.max(error,Math.hypot(...f.feet.map((v,j)=>v-a.feet[j])))
      restoredTicks++
    }
    if(!top && f.feet[1]>=h+.02)top=f
    if(f.feet[1]>h-.02 && f.feet[2]<rim-.05 && f.ground && f.contact===id){landed=f;break}
  }
  console.log('ascent',{nativeMax,bottom,attach,mid,top,landed,error,restoredTicks,last:describe(proof)})
  assert(attach&&mid&&top&&landed&&error<.00001&&restoredTicks>65,'Capsule did not climb/land or restore diverged')
  step(proof,idle,5)
  const landingSave=snapshotSimHostBytes(proof.host)
  function descend(run,approachInput) {
    let low, descending, descentPeak=0, steadyDescentPeak=0, alignDescent, prev=describe(run), descendingTicks=0
    for(let i=0;i<maxTicks;i++){
      const f=step(run,alignDescent ? down : {...down,moveZ:approachInput})
      const drop=prev.feet[1]-f.feet[1]
      prev=f
      descentPeak=Math.max(descentPeak,drop)
      if(drop>.02)descendingTicks++
      if(alignDescent&&f.feet[1]>.20)steadyDescentPeak=Math.max(steadyDescentPeak,drop)
      if(!alignDescent && Math.abs(f.feet[2]-route.top.z)<.001)alignDescent=f
      if(!descending && f.feet[1]<h-.2)descending=f
      if(f.feet[1]<.09&&f.ground){low=f;break}
    }
    assert(descending && alignDescent && low?.contact===id+'-ground' && descendingTicks>=Math.floor((h-.34)*30))
    assert(steadyDescentPeak<.04,'Fully aligned descent exceeded the speed envelope')
    return {descending,low,descendingTicks,descentPeakMetersPerTick:descentPeak,alignedPeakMetersPerTick:steadyDescentPeak,alignedAt:alignDescent}
  }
  const selected=letter==='A' ? 1 : .70
  const descent=descend(proof,selected)
  assert(descent.descentPeakMetersPerTick<.09,'Selected edge handoff exceeded 90 mm')
  const approachTrials=[]
  if(letter!=='A') for(const input of [.40,.55,.70,.85,1]) {
    const match=await open(landingSave)
    try {
      const trial=descend(match,input)
      approachTrials.push({input,peakDropMetersPerTick:trial.descentPeakMetersPerTick,ticks:trial.low.tick-landed.tick-5})
      if(input===selected) assert.deepEqual(trial,descent,'Matched restore did not reproduce main descent')
    } finally {match.dispose()}
  }
  release=await open()
  start(release)
  for(let i=0;i<200&&describe(release).feet[1]<2;i++)step(release,up)
  const held=describe(release), still=step(release,idle,30)
  assert(held.feet[1]>=2 && Math.abs(held.feet[1]-still.feet[1])<.001,'Neutral drift')
  step(release,{...idle,jump:true})
  const released=step(release,idle,100)
  assert(released.ground&&released.feet[1]<.1)
  gated=await open()
  setFeet(gated,x+1.5,.065,approach);step(gated,idle,25)
  const off=Array.from({length:240},()=>step(gated,up))
  assert(Math.max(...off.map(f=>f.feet[1]))<.15,'Off-center approach attached')
  const result={versions:{engine:'0.1.44',format:'0.43.0'},route,deckRim:rim,
    normalRoom:{maxFeetY:nativeMax,installedLadder:false,peakDropPerTick:unsupportedFall},
    explicitStockInstaller:{bottom,attach,mid,top,landed,descending:descent.descending,low:descent.low,still,released,restoredTicks,maxRestoreErrorMeters:error,descendingTicks:descent.descendingTicks,descentPeakMetersPerTick:descent.descentPeakMetersPerTick,alignedPeakMetersPerTick:descent.alignedPeakMetersPerTick,alignedAt:descent.alignedAt}, ...(approachTrials.length?{selectedApproachInput:selected,approachTrials}:{}), samples}
  writeFileSync(output,JSON.stringify(result,null,2)+'\n')
}finally{
  for(const room of [normalHost,proof,resumed,release,gated])room?.dispose()
}
