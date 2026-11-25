import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const [fixture,out]=process.argv.slice(2)
assert(fixture&&out,'Pass an admitted local folder and output JSON path')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const root=dirname(req.resolve('@wildshard/engine/package.json'))
const formatFile=join(dirname(req.resolve('@wildshard/format/movers')),'../../package.json')
const version=p=>JSON.parse(readFileSync(p)).version
assert.equal(version(join(root,'package.json')),'0.1.44')
assert.equal(version(formatFile),'0.43.0')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {loadCookedFolder}=await at('src/server/host/headlessFolder.ts')
const {createNativeHeadlessResident}=await at('src/server/host/headlessRuntime.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {staticBoxCollider}=await at('src/shared/engine/physics/query.ts')
const {plateOverlap}=await at('src/shared/engine/world/interact/barrel.ts')
const {bindInteractionState,bindInteractionTransitions,test}=await at('src/shared/engine/world/interact/flags.ts')
const {QuestFlagGates}=await at('src/shared/game/quest/flagGates.ts')
const {overlapBox}=await at('src/shared/engine/physics/overlap.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const base=await loadCookedFolder(fixture,R)
const assetURL=new URL('../../public/assets/wildshard-art/',import.meta.url)
const assets=['haul-crate.glb','wsc-plan-006-pressure-plate.glb','w4a-plate-gate-grate.glb'].map(n=>
  [n,createHash('sha256').update(readFileSync(new URL(n,assetURL))).digest('hex')])
assert.equal(assets[0][1],'d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44')
assert.equal(assets[1][1],'cdf40fa1f1036818e460ba5a29f95cbb547c09f8e361e5fbbb1d536d895847cc')
const floor=.0345, support=.3225, crateY=.8635/2
const plates=[-82,-72,-62].map((x,i)=>({id:'w4a-plate-'+(i+1),kind:'plate',by:'any',size:4,x,y:support,z:192}))
const gate={x:-52.03425,z:192,hw:.20425,hd:9.628006,yBottom:.060,yTop:3.715}
const gateCy=(gate.yTop+gate.yBottom)/2,gateHy=(gate.yTop-gate.yBottom)/2
const cond={all:plates.map(p=>'plate:'+p.id)}
const rot={x:0,y:0,z:0,w:1}
const xyz=(x,y,z)=>({x,y,z})
function nav(){
  const b=Buffer.alloc(120);let n=0
  const u32=v=>{b.writeUInt32LE(v,n);n+=4}
  const u16=v=>{b.writeUInt16LE(v,n);n+=2}
  const f=v=>{b.writeFloatLE(v,n);n+=4}
  const bytes=a=>{for(const x of a)b[n++]=x}
  bytes([87,83,78,77]);u32(1);u32(1)
  for(const x of [.38,1.8,.3,.25,.1,-75,0,183,4])f(x)
  u32(1);u32(0);u32(0)
  for(const x of [-75,0,183,-71,1,187])f(x)
  u16(3);u16(1);u16(0);bytes([0,0,8,0,8,0]);u16(0);u16(0);u16(0)
  bytes([3,0,1,0,1,2,0,0,0,0,0])
  return b.subarray(0,n)
}
const box=(x,y,z,hx,hy,hz)=>({kind:'box',x,y,z,hx,hy,hz,rot})
const colliders=[box(-67,floor-.5,192,35,.5,20),
  ...plates.map(p=>box(p.x,support-.12,p.z,1.77,.12,1.77)),
  box(gate.x,gateCy,gate.z,gate.hw,gateHy,gate.hd)]
const navPath='server/w4a-calibration-nav',nativePath='server/native-assembly.json'
const native=new TextEncoder().encode(JSON.stringify({kind:'native-assembly',
  level:{speed:4.3,ground:{size:500,height:-2}},terrain:{kind:'flat'},navigation:{file:navPath},
  entries:{proven:{lanes:0,steps:0,portalTransfers:0}},
  features:[{host:'collision.pieces',rows:{value:colliders.map((collider,i)=>({
    id:'w4a-witness-'+i,name:'W4a isolated test '+i,file:'w4a-rehearsal-only',active:true,surface:'metal',colliders:[collider]
  }))}}]}))
const p=base.product
const input={...base,product:{...p,hasFile:n=>n===nativePath||n===navPath||p.hasFile(n),
  file:n=>n===nativePath?Promise.resolve(native):n===navPath?Promise.resolve(nav()):p.file(n)}}
const idle={kind:'player',moveX:0,moveZ:0,yaw:Math.PI}
const shift=(cmd,moveZ)=>({...cmd,moveZ})
function pose(body,x,y,z){body.position.set(x,y,z);body.motor.resetAt(body.position)}
const stable=n=>Number(n.toFixed(5))

async function run(mode){
  const resident=await createNativeHeadlessResident(input,undefined,{room:true})
  const host=resident.host, physics=host.physics, w=physics.world
  const player=host.players.get('actor.player')
  const solid=staticBoxCollider(physics,gate)
  assert(player?.hasMotor&&solid); assert.equal(host.players.size,1)
  const rows=plates.map(row=>bindInteractionState(row,host.flags))
  const transitions=bindInteractionTransitions(rows,host.flags,{
    commit:()=>{throw new Error('The plate test has no scripted actions')},item:()=>{throw new Error('No grants')},
    plate:(row,size)=>plateOverlap(physics,row.d,0,size)
  })
  const stock=mode==='stock'?new QuestFlagGates(host,{gates:[{id:'w4a-grate',opensWhen:cond,target:{kind:'box',box:gate}}]}):null
  const bodies=plates.slice(0,2).map(p=>{
    const b=w.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(p.x,support+crateY+.022,p.z).setCcdEnabled(true))
    w.createCollider(R.ColliderDesc.cuboid(.558,crateY,.5192).setCollisionGroups(groups('ITEM')).setFriction(.76),b)
    return b
  })
  const step=(n,cmd=idle)=>{
    for(let i=0;i<n;i++){
      resident.step([cmd])
      transitions.step()
      if(stock)stock.sync();
      else {
        // Proposed world-wide, reversible owner. Re-arm only when doorway is clear.
        const occupied=overlapBox(physics,xyz(gate.x,gateCy,gate.z),xyz(gate.hw+.035,gateHy,gate.hd),0,['PLAYER','ITEM'],()=>true)
        const shouldCollide=!test(host.flags,cond)&&(solid.isEnabled()||!occupied)
        if(solid.isEnabled()!==shouldCollide)solid.setEnabled(shouldCollide)
      }
    }
  }
  const sample=name=>{
    const desired=test(host.flags,cond)
    const flags=rows.map(row=>host.flags.has(row.plate))
    const enabled=solid.isEnabled()
    const ray=new R.Ray(xyz(-54,1.05,192),xyz(1,0,0))
    const contact=w.castRay(ray,4,true,undefined,undefined,undefined,undefined,c=>c.handle===solid.handle)
    return {name,tick:host.state.tick,held:flags,logicalOpen:desired,colliderEnabled:enabled,doorwayRayBlocked:contact!==null,
      playerFeet:player.position.toArray().map(stable)}
  }
  try {
    pose(player,-62,floor+.035,187.5);step(90)
    const control=bodies.map((b,i)=>{
      const pad=plates[i]
      return {crateBottomM:stable(b.translation().y-crateY),lowStripe:plateOverlap(physics,{...pad,y:floor},0,pad.size),
        raisedTread:plateOverlap(physics,pad,0,pad.size)}
    })
    assert(control.every(c=>!c.lowStripe&&c.raisedTread&&Math.abs(c.crateBottomM-support)<.01),JSON.stringify(control))
    const states=[sample('two crates')]
    // First arrival is staged; the player actually walks off and back onto the raised tread.
    pose(player,-62,support+.028,192);step(16);states.push(sample('player on'))
    step(47,shift(idle,-1));step(6);states.push(sample('player walks off'))
    step(48,shift(idle,1));step(8);states.push(sample('player walks back'))
    assert.deepEqual(states.map(x=>x.held.filter(Boolean).length),[2,3,2,3],JSON.stringify(states))
    assert.deepEqual(states.map(x=>x.logicalOpen),[false,true,false,true])
    assert.deepEqual(states.map(x=>x.colliderEnabled),mode==='stock'?[true,false,false,false]:[true,false,true,false])
    assert.deepEqual(states.map(x=>x.doorwayRayBlocked),states.map(x=>x.colliderEnabled),JSON.stringify(states))
    let rearm=null, stockReleaseCrossing=null
    if(stock){
      pose(player,gate.x-2,floor+.028,gate.z);step(20)
      step(55,{...idle,moveX:1});step(4)
      stockReleaseCrossing=sample('stock passage after release')
      assert(!stockReleaseCrossing.logicalOpen&&!stockReleaseCrossing.colliderEnabled&&
        stockReleaseCrossing.playerFeet[0]>gate.x+1,JSON.stringify(stockReleaseCrossing))
    }else{
      pose(player,gate.x,floor+.028,gate.z);step(18)
      const overlap=sample('body in doorway')
      pose(player,gate.x+3,floor+.028,gate.z);step(18)
      const clear=sample('doorway cleared')
      assert(!overlap.logicalOpen&&!overlap.colliderEnabled&&clear.colliderEnabled)
      pose(player,gate.x-2,floor+.028,gate.z);step(20)
      step(55,{...idle,moveX:1});step(4)
      const approach=sample('normal closed approach')
      assert(approach.playerFeet[0]<gate.x-gate.hw && approach.playerFeet[0]>gate.x-1 && approach.colliderEnabled,JSON.stringify(approach))
      rearm={overlap,clear,approach}
    }
    return {mode,control,states,rearm,stockReleaseCrossing}
  }finally{resident.dispose()}
}
const stock=await run('stock'), proposed=await run('reversible')
assert.deepEqual(await run('stock'),stock)
assert.deepEqual(await run('reversible'),proposed)
writeFileSync(out,JSON.stringify({scope:'Engine 0.1.44 one-player native resident rehearsal; no shard change',assets:Object.fromEntries(assets),
  gate,plates:plates.map(({id,x,y,z})=>({id,x,y,z})),stock,proposed,
  note:'Crates are placed by the fixture, player walks off and back on. No carrying, art animation or multiplayer.'},null,2)+'\n')
console.log('Verified physical 2→3→2→3; stock latches, reversible restores collision and waits for clear doorway.')
