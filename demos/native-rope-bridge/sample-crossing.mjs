// Test the normal room installer. Never construct a RopeChain or add a deck collider here.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const fixture=process.argv[2], out=process.argv[3]
assert(fixture && out,'Pass a built native plan folder and an output JSON path')
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const root=dirname(req.resolve('@wildshard/engine/package.json'))
const formatPath=req.resolve('@wildshard/format/worldAssembly')
const version=n=>JSON.parse(readFileSync(n,'utf8')).version
assert.equal(version(join(root,'package.json')),'0.1.44')
assert.equal(version(join(dirname(formatPath),'../../package.json')),'0.43.0')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {WorldAssemblySchema}=await import(pathToFileURL(formatPath).href)
const {parse}=await import(pathToFileURL(req.resolve('valibot')).href)
const {Vector3,Quaternion,Matrix4}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {loadCookedFolder}=await at('src/server/host/headlessFolder.ts')
const {openWorldAdapter}=await at('src/server/host/openWorld.ts')
const {installedKeys}=await at('src/server/game/shardfile/installedSides.ts')
const {tagOf}=await at('src/shared/engine/physics/surface.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const base=await loadCookedFolder(fixture,R)
const a=new Vector3(-168,18,-103),b=new Vector3(-190,18,-104)
const len=a.distanceTo(b), direction=b.clone().sub(a).normalize(), side=new Vector3(direction.z,0,-direction.x)
const width=1.6,sag=.65,halfY=.075,N=Number(process.env.WSC_BRIDGE_LINKS??18), mass=12
assert(Number.isInteger(N)&&N>=12&&N<=54)
const owner={id:'w6c-station6',name:'Station 6 rope bridge'}
const position=(p)=>a.clone().addScaledVector(direction,p*len).add(new Vector3(0,-4*sag*p*(1-p),0))
const point=({x,y,z})=>({x,y,z})
const angles=({x,y,z,w})=>({x,y,z,w})
// Native assembly requires navigation even though this test has no NPCs.
function calibrationNav() {
  const buf=Buffer.alloc(120);let n=0
  const u32=v=>{buf.writeUInt32LE(v,n);n+=4}
  const u16=v=>{buf.writeUInt16LE(v,n);n+=2}
  const f=v=>{buf.writeFloatLE(v,n);n+=4}
  const bytes=a=>{for(const x of a)buf[n++]=x}
  bytes([87,83,78,77]);u32(1);u32(1)
  for(const x of [.38,1.8,.3,.25,.1,-169,18,-104,4])f(x)
  u32(1);u32(0);u32(0)
  for(const x of [-169,18,-104,-165,19,-100])f(x)
  u16(3);u16(1);u16(0)
  bytes([0,0,8,0,8,0]);u16(0);u16(0);u16(0)
  bytes([3,0,1,0,1,2,0,0,0,0,0])
  return buf.subarray(0,n)
}
const nativePath='server/native-assembly.json'
const navPath='server/w6c-calibration-nav'
const yaw=new Quaternion().setFromRotationMatrix(new Matrix4().makeBasis(side,new Vector3(0,1,0),direction))
const lands=[[a,-1,'top-deck'],[b,1,'tank-roof']].map(([end,sign,id])=>{
  const {x,z}=end.clone().addScaledVector(direction,sign*2.5)
  return {id,name:id,file:'w6c-bench-only',active:true,surface:'wood',
    colliders:[{kind:'box',x,y:17.75,z,hx:2.5,hy:.25,hz:2.5,rot:angles(yaw)}]}
})
const native=new TextEncoder().encode(JSON.stringify({kind:'native-assembly',
  level:{speed:4.3,ground:{size:500,height:0}},terrain:{kind:'flat'},
  navigation:{file:navPath},entries:{proven:{lanes:0,steps:0,portalTransfers:0}},
  features:[{host:'collision.pieces',rows:{value:lands}}]}))
const source={...base,product:{...base.product,
  hasFile:n=>n===nativePath||n===navPath||base.product.hasFile(n),
  file:n=>n===nativePath?Promise.resolve(native):n===navPath?Promise.resolve(calibrationNav()):base.product.file(n)}}
const product=source.product
const segments=Array.from({length:N},(_,i)=>{
  const start=position(i/N),end=position((i+1)/N),along=end.clone().sub(start).normalize()
  const up=new Vector3().crossVectors(along,side).normalize()
  return {...point(start.clone().lerp(end,.5).addScaledVector(up,-halfY)),
      hz:start.distanceTo(end)/2,rot:angles(new Quaternion().setFromRotationMatrix(new Matrix4().makeBasis(side,up,along)))}
})
const span={a:[a.x,a.z],b:[b.x,b.z]}
const rows=parse(WorldAssemblySchema,{stages:[
  {kind:'rope-deck',id:'w6c-deck',label:'Station 6 test deck',span,
    site:{model:{id:'w6c-deck',name:owner.name,file:'wsc-prop-048-rope-walkway.glb',category:'props',pipeline:'blender',surface:'wood'},
      specimen:0,loading:[width,.15,len],draws:{specimen:'w6c-bench-only',world:'w6c-bench-only'},
      deck:{width,sag,halfY,mass,maxSegments:N,maxColliders:N,margin:0,owner,piece:'w6c-deck'},
      spans:[{key:JSON.stringify([span.a,span.b,width,sag]),ground:[],origin:point(a),width,len,direction:{x:direction.x,z:direction.z},segments,ownDescs:[]}]}},
  {kind:'rope-chain',id:'w6c-chain',label:'Station 6 test chain',deck:'w6c-deck',capture:'w6c-capture'}
]})
const basePlan=product.has('client/plan')?product.section('client/plan'):{features:[]}
assert(!basePlan.features.some(f=>f.kind==='world.assembly' && f.rows.stages.some(s=>s.kind==='rope-chain')))
const plan={...basePlan,features:[...basePlan.features,{kind:'world.assembly',rows}]}
const input={...source,product:{...product,
  has:n=>n==='client/plan'||product.has(n),
  section:n=>n==='client/plan'?plan:product.section(n)}}
const setup=room=>{
  const p=room.host.players.get('actor.player')
  p.position.copy(a.clone().addScaledVector(direction,-1.3).add(new Vector3(0,.045,0)))
  p.motor.resetAt(p.position)
}
const owned=(host)=>{
  const planks=[]
  host.physics.world.forEachCollider(c=>{
    if(tagOf(c)?.owner?.id===owner.id)planks.push({col:c,body:c.parent()})
  })
  return planks.sort((aa,bb)=>aa.body.handle-bb.body.handle)
}
const joints=host=>{
  let n=0;const bodies=new Set(owned(host).map(({body})=>body.handle))
  host.physics.world.impulseJoints.forEach(j=>{if(bodies.has(j.body1().handle)||bodies.has(j.body2().handle))n++})
  return n
}
const describe=room=>{
  const p=room.host.players.get('actor.player'), feet=p.position.toArray(), ground=tagOf(p.motor.result.groundCollider)?.owner?.id===owner.id
  const travel=p.position.clone().sub(a).dot(direction), lateral=p.position.clone().sub(a).dot(side)
  const bodies=owned(room.host)
  return {tick:room.host.state.tick,feet,travel,lateral,ground,onFloor:p.fall.grounded,
      awake:bodies.filter(q=>!q.body.isSleeping()).length,
      poses:bodies.map(q=>({p:point(q.body.translation()),q:angles(q.body.rotation())}))}
}
const walk={kind:'player',moveX:direction.x,moveZ:direction.z,yaw:Math.atan2(-direction.x,-direction.z)}
const idle={...walk,moveX:0,moveZ:0}
const live=await openWorldAdapter(input)
let restored,legacy,upgraded
try{
  assert(installedKeys(live.host).has('ropeDecks'))
  assert.equal(owned(live.host).length,N)
  assert.equal(joints(live.host),N+1)
  setup(live)
  for(let i=0;i<360;i++)live.step([idle])
  const rest=describe(live)
  const frames=[]
  let checkpoint,minimumY=Infinity,minYSpan=Infinity,firstDeck,firstEnd,maxAwake=0,lastCentre,restoredFrames=0,maxRestoreDelta=0,maxLateral=0,spanGroundTicks=0,spanAirTicks=0
  for(let i=0;i<1000;i++){
    live.step([walk])
    const f=describe(live);if(i%5===0)frames.push(f)
    minimumY=Math.min(minimumY,f.feet[1]);maxAwake=Math.max(maxAwake,f.awake)
    if(f.travel>1&&f.travel<len-1){
      minYSpan=Math.min(minYSpan,f.feet[1]);maxLateral=Math.max(maxLateral,Math.abs(f.lateral));lastCentre=f
      if(f.ground)spanGroundTicks++;else spanAirTicks++
    }
    if(f.ground&&!firstDeck)firstDeck=f
    if(!checkpoint&&f.travel>=len/2&&f.ground){
      checkpoint=live.commit().snapshot
      restored=await openWorldAdapter(input,checkpoint)
      assert(installedKeys(restored.host).has('ropeDecks'))
      assert.equal(owned(restored.host).length,N)
      assert.equal(joints(restored.host),N+1)
      assert.deepEqual(describe(restored).feet,f.feet)
      assert.deepEqual(describe(restored).poses,f.poses)
    }else if(restored){
      restored.step([walk])
      const r=describe(restored)
      const error=Math.hypot(...r.feet.map((v,k)=>v-f.feet[k]))
      assert.deepEqual(r.poses,f.poses,'Restored chain pose differs from uninterrupted room')
      maxRestoreDelta=Math.max(maxRestoreDelta,error);restoredFrames++
      assert(error<.003,'Restored room crossed differently')
    }
    if(f.travel>len+.8){firstEnd=f;break}
    if(f.feet[1]<15)break
  }
  const awakeByIdleSecond=[]
  for(let i=1;i<=1200;i++){
    live.step([idle]);if(i%60===0)awakeByIdleSecond.push(describe(live).awake)
  }
  const summary={N,len,width,sag,a:point(a),b:point(b),minimumY,minYSpan,maxAwake,maxLateral,spanGroundTicks,spanAirTicks,
     restoredFrames,maxRestoreDelta,awakeByIdleSecond,
     restAwake:rest.awake,firstDeck:firstDeck?.tick??null,firstEnd:firstEnd?.tick??null,
     endFeet:(firstEnd??describe(live)).feet,endTravel:(firstEnd??describe(live)).travel,
     centreGround:lastCentre?.ground??false,restored:Boolean(restored),joints:joints(live.host),
     clockHz:60,engine:'0.1.44',format:'0.43.0',scopedRoomBench:true}
  console.log(JSON.stringify(summary))
  writeFileSync(out,JSON.stringify({summary,frames,rows})+'\n')
  assert(firstDeck&&firstEnd&&checkpoint,'Bridge did not carry the native player to the far end')
  assert(minYSpan>16.8&&spanGroundTicks>0&&spanAirTicks===0&&maxLateral<width/2-.38,
    'Bridge reached the far end but failed the measured crossing envelope')
  legacy=await openWorldAdapter(source)
  assert.equal(owned(legacy.host).length,0)
  // Real old save with no chain adapter or bodies, not a stripped snapshot.
  setup(legacy)
  for(let i=0;i<180;i++)legacy.step([idle])
  const old=legacy.commit().snapshot
  let emptyFall=null
  for(let i=0;i<360;i++){
    legacy.step([walk]);const f=describe(legacy)
    assert(!f.ground)
    if(f.feet[1]<15){emptyFall={tick:f.tick,feet:f.feet};break}
  }
  assert(emptyFall,'Control room without rope stages did not fall')
  upgraded=await openWorldAdapter(input,old)
  assert.equal(owned(upgraded.host).length,N)
  assert.equal(joints(upgraded.host),N+1)
  for(let i=0;i<800;i++){
    upgraded.step([walk])
    const f=describe(upgraded)
    assert(f.feet[1]>16.8)
    if(f.travel>len+.8){
      writeFileSync(out,JSON.stringify({summary:{...summary,emptyFall,legacyRebuiltBodies:N,legacyExitTick:f.tick},frames,rows})+'\n')
      break
    }
    assert(i<799,'Old save upgraded but player did not cross')
  }
}finally{upgraded?.dispose();legacy?.dispose();restored?.dispose();live.dispose()}
