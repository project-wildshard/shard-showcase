import { createHash } from 'node:crypto'
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const req = createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT), 'package.json') : import.meta.url)
const root = dirname(req.resolve('@wildshard/engine/package.json'))
assert.equal(JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version, '0.1.44')
const formatVersion = JSON.parse(readFileSync(join(dirname(req.resolve('@wildshard/format/scriptAbiV1')),'../../package.json'),'utf8')).version
assert.equal(formatVersion,'0.43.0')
assert.equal(formatVersion,'0.43.0')
const at = relative => import(pathToFileURL(join(root,relative)).href)
await at('scripts/sim-node-loader.mjs')
const {Physics}=await at('src/shared/engine/physics/Physics.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const [proofFile,traceFile]=process.argv.slice(2)
assert(proofFile&&traceFile,'Need proof and replay paths')
const rad=d=>d*Math.PI/180
const p=(x,y,z)=>({x,y,z})
const qz=a=>({x:0,y:0,z:Math.sin(a/2),w:Math.cos(a/2)})
const angle=q=>2*Math.atan2(q.z,q.w)
const asset=(name,hash)=>{
  const b=readFileSync(new URL('../../public/assets/wildshard-art/'+name+'.glb',import.meta.url))
  assert.equal(createHash('sha256').update(b).digest('hex'),hash)
  assert.equal(b.readUInt32LE(16),0x4e4f534a)
  const j=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)))
  const bytes=28+b.readUInt32LE(12)
  function mesh(name){
    const n=j.nodes.find(n=>n.name===name)
    assert(n&&!n.rotation&&!n.scale&&!n.matrix)
    const xyz=[]
    for(const {attributes:{POSITION:key}} of j.meshes[n.mesh].primitives){
      const a=j.accessors[key],v=j.bufferViews[a.bufferView]
      assert.equal(a.type,'VEC3');assert.equal(a.componentType,5126)
      for(let i=0;i<a.count;i++)for(let k=0;k<3;k++)
        xyz.push(b.readFloatLE(bytes+(v.byteOffset??0)+(a.byteOffset??0)+i*(v.byteStride??12)+k*4))
    }
    return {pivot:n.translation??[0,0,0],xyz}
  }
  return {hash,mesh}
}
const plank=asset('wsc-plan-003-hinged-seesaw','4810b216338fb4da46115884945a2a52c89776ce9d87c585508d6b95bd27df07')
const deck=plank.mesh('Hinged_Deck')
const crate=asset('haul-crate','d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44').mesh('haul-crate')
const pivotY=deck.pivot[1],top=Math.max(...deck.xyz.filter((_,i)=>i%3===1))
const crateH=Math.max(...crate.xyz.filter((_,i)=>i%3===1))
const limit=rad(9.55), rest=rad(7.5), release=90, drop=120
const rotate=(q,v)=>{
  const {x,y,z,w}=q
  const k=p(2*(y*v.z-z*v.y),2*(z*v.x-x*v.z),2*(x*v.y-y*v.x))
  return p(v.x+w*k.x+y*k.z-z*k.y,v.y+w*k.y+z*k.x-x*k.z,v.z+w*k.z+x*k.y-y*k.x)
}
const state=b=>({p:{...b.translation()},q:{...b.rotation()}})
const BASES=[[-80,224],[-62,224]], floor=.02
function run(base,offset,mode){
  const [X,Z]=base, anchorY=floor+pivotY
  const phy=new Physics(R), W=phy.world
  try {
    W.createCollider(R.ColliderDesc.cuboid(12,1,6).setTranslation(X,floor-1,Z).setFriction(.85))
    const stand=W.createRigidBody(R.RigidBodyDesc.fixed().setTranslation(X,floor,Z))
    const d=W.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(X,anchorY,Z).setAngularDamping(.06).setAdditionalSolverIterations(12).setCanSleep(false))
    const hull=R.ColliderDesc.convexHull(new Float32Array(deck.xyz))
    assert(hull)
    const deckCollider=W.createCollider(hull.setMass(165).setFriction(.7).setRestitution(0),d)
    const joint=W.createImpulseJoint(R.JointData.revolute(p(0,pivotY,0),p(0,0,0),p(0,0,1)),stand,d,true)
    joint.setContactsEnabled(false)
    joint.setLimits(-limit,limit)
    d.setRotation(qz(rest),true);d.setBodyType(R.RigidBodyType.Fixed,true)
    function makeCrate(position,scale,mass){
      const b=W.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(...position).setCanSleep(false).setCcdEnabled(true))
      const shape=R.ColliderDesc.convexHull(new Float32Array(crate.xyz.map(c=>c*scale)))
      assert(shape)
      const collider=W.createCollider(shape.setMass(mass).setFriction(.82).setRestitution(0),b)
      return {body:b,collider}
    }
    const topAt=x=>(top+x*Math.sin(rest))/Math.cos(rest)
    const {body:rider,collider:riderCollider}=makeCrate([X-5.46,anchorY+topAt(-5.46)+.088,Z+offset],1,24)
    let weight
    const frames=[]
    let clearFrames=0,bestClear=0,apexY=-Infinity,settledY,lowest=Infinity,minAngle=Infinity,maxAngle=-Infinity,
        maxPivotDrift=0,firstLift=null,landed=null,peakTick=0,apexTick=0,runClear=0,longestClear=0
    function deckGap(){
      const ds=state(d),rs=state(rider)
      const inv={x:-ds.q.x,y:-ds.q.y,z:-ds.q.z,w:ds.q.w}
      let gap=Infinity
      for(let i=0;i<crate.xyz.length;i+=3){
        const v=rotate(rs.q,p(...crate.xyz.slice(i,i+3)))
        const local=rotate(inv,p(rs.p.x+v.x-ds.p.x,rs.p.y+v.y-ds.p.y,rs.p.z+v.z-ds.p.z))
        gap=Math.min(gap,local.y-top)
      }
      return gap
    }
    for(let tick=0;tick<=330;tick++){
      if(tick===release&&mode!=='locked')d.setBodyType(R.RigidBodyType.Dynamic,true)
      if(tick===drop&&mode!=='no-weight')weight=makeCrate([X+5.34,anchorY+topAt(5.34)+2.8,Z-offset],1.35,205).body
      phy.step()
      if(tick===release-1)settledY=rider.translation().y
      const a=angle(d.rotation()),r=state(rider),s=state(d)
      const gap=deckGap()
      const over=Math.abs(r.p.x-X)<6.2&&Math.abs(r.p.z-Z)<.74
      if(tick>=drop){
        if(gap>bestClear&&over){bestClear=gap;peakTick=tick}
        let touching=false
        W.contactPair(deckCollider,riderCollider,m=>{
          for(let i=0;i<m.numContacts();i++) if(m.contactDist(i)<=.004) touching=true
        })
        if(over&&gap>.04&&!touching){clearFrames++;firstLift??=tick;runClear++} else runClear=0
        longestClear=Math.max(longestClear,runClear)
        if(firstLift!==null&&landed===null&&over&&touching)landed=tick
        if(r.p.y>apexY){apexY=r.p.y;apexTick=tick}
      }
      maxPivotDrift=Math.max(maxPivotDrift,Math.hypot(s.p.x-X,s.p.y-anchorY,s.p.z-Z))
      minAngle=Math.min(a,minAngle);maxAngle=Math.max(a,maxAngle)
      for(let i=0;i<deck.xyz.length;i+=3)
        lowest=Math.min(lowest,s.p.y-floor+rotate(s.q,p(...deck.xyz.slice(i,i+3))).y)
      frames.push({tick,deck:s,rider:r,weight:weight?state(weight):null,gap})
    }
    return {base,offset,mode,clearFrames,longestClear,bestClear,settledY,apexY,apexTick,lowest,angleDeg:[minAngle/rad(1),maxAngle/rad(1)],maxPivotDrift,firstLift,landed,peakTick,frames}
  } finally {phy.dispose()}
}
const runs=BASES.flatMap(b=>[-.18,0,.18].flatMap(o=>['live','locked','no-weight'].map(m=>run(b,o,m))))
const brief=({frames,...r})=>r
for(let i=0;i<runs.length;i+=3){
  const [open,locked,unloaded]=runs.slice(i,i+3)
  assert.equal(open.settledY,locked.settledY)
  assert.equal(open.settledY,unloaded.settledY)
  assert(open.firstLift>drop&&open.landed>open.firstLift+60,'Payload must return to the deck')
  assert(open.longestClear>=70&&open.bestClear>1.95&&open.apexY-open.settledY>3.8)
  assert(locked.firstLift===null&&unloaded.firstLift===null)
}
assert(runs.every(r=>r.lowest>.25&&r.maxPivotDrift<.002&&r.angleDeg.every(a=>Math.abs(a)<9.60)))
assert.deepEqual(run(BASES[0],0,'live'),runs[3])
console.table(runs.map(({base,offset,mode,longestClear,bestClear,firstLift,landed})=>({base,offset,mode,longestClear,bestClear,firstLift,landed})))
writeFileSync(proofFile,JSON.stringify({engine:'0.1.44',format:formatVersion,hz:60,pivotY,top,crateH,
  floor,release,drop,limitDeg:limit/rad(1),runs:runs.map(brief)},null,2)+'\n')
writeFileSync(traceFile,JSON.stringify({floor,release,drop,run:runs[3],second:runs[12],locked:runs[4]})+'\n')
