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
const at = relative => import(pathToFileURL(join(root,relative)).href)
await at('scripts/sim-node-loader.mjs')
const {Physics}=await at('src/shared/engine/physics/Physics.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {Scope}=await at('src/shared/engine/app/scope.ts')
const {DeclaredBodyOps}=await at('src/server/game/quest/bodyOps.ts')
const {SCRIPT_V1_COMMANDS: C,SCRIPT_V1_READS: Reads}=await import('@wildshard/format/scriptAbiV1')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const [geometryFile,proofFile,traceFile]=process.argv.slice(2)
assert(geometryFile&&proofFile&&traceFile,'Need ramp triangles, proof, replay paths')
const input=readFileSync(geometryFile)
const geometrySHA256=createHash('sha256').update(input).digest('hex')
assert.equal(geometrySHA256,'7cab1ab062d1e498457d701eeccfc06704ff88f1c3d7e15c4fcb835e9657f57b')
const geometry=JSON.parse(input)
const laneZ=196, floor=.04, slope=.25, toe=-42
const gate={x:-26.14,baseY:4.72,z:laneZ,half:[.088,.49,1.83],lift:1.78,ticks:36}
const dt=1/60
const p=(x,y,z)=>({x,y,z})
const tilt=q=>Math.acos(Math.max(-1,Math.min(1,1-2*(q.x*q.x+q.z*q.z))))*180/Math.PI

function trial(offset,release){
  const rows=[]
  for(let i=0;i<4;i++){
    const x=-19.5-1.8*i
    rows.push({id:'ball-'+(i+1),kind:'prop',shape:{ball:.8},
      at:p(x,(x-toe)*slope+.8/Math.cos(Math.atan(slope))+.014,laneZ+offset), yaw:0,
      owner:{kind:'w4b-gate-fixture',id:'ball-'+(i+1)},material:'metal',density:130,
      friction:.70,restitution:.04,angularDamping:.08,rolling:.025,ccd:true})
  }
  for(let r=0;r<4;r++)for(let i=0;i<=r;i++){
    const id='pin-'+(rows.length-3)
    rows.push({id,kind:'prop',shape:{cylinder:{radius:.25,halfHeight:.645}},at:p(-50-r*1.2,floor+.648,laneZ+(i-r/2)*1.1),
      yaw:0,owner:{kind:'w4b-gate-fixture',id},material:'wood',density:170,
      friction:.58,restitution:.04,angularDamping:.22,linearDamping:.32,rolling:.045,ccd:true})
  }
  const scope=new Scope('w4b gate')
  const phy=new Physics(R)
  try{
    const W=phy.world
    W.createCollider(R.ColliderDesc.cuboid(39,1,27).setTranslation(-53,floor-1,laneZ).setCollisionGroups(groups('WORLD')).setFriction(.8))
    W.createCollider(R.ColliderDesc.trimesh(new Float32Array(geometry.vertices),new Uint32Array(geometry.triangles))
      .setCollisionGroups(groups('WORLD')).setFriction(.8))
    const bar=W.createRigidBody(R.RigidBodyDesc.kinematicPositionBased().setTranslation(gate.x,gate.baseY,gate.z))
    W.createCollider(R.ColliderDesc.cuboid(...gate.half).setCollisionGroups(groups('WORLD')).setFriction(.42),bar)
    const data={bodies:rows,floors:[],colliders:[]}
    const ops=DeclaredBodyOps.native({physics:phy,scope,playerFocus:p(-46,0,laneZ)},data)
    const id=row=>ops.registries.bodies.get(row.id)
    for(let i=0;i<rows.length;i+=4)
      ops.prepare(rows.slice(i,i+4).map(row=>[C['body.spawn'],0,id(row),0,0])).commit()
    assert(rows.every(row=>ops.read(Reads.bodyAlive,id(row),0)===1))
    const bodies=rows.map(row=>ops.body(row.id)), balls=bodies.slice(0,4)
    function step(){ops.pre(dt);phy.step();ops.post(dt)}
    for(let i=0;i<240;i++)step()
    const held=balls.map(b=>({...b.curr}))
    assert(held.every(v=>v.x>gate.x+.49&&v.x<-19&&Math.abs(v.z-laneZ)<1.05),JSON.stringify(held))
    const frames=[]
    const toes=Array(4).fill(null), gatePasses=Array(4).fill(null)
    let firstTip=null
    function save(tick){frames.push({tick,bar:{...bar.translation()},bodies:bodies.map((b,i)=>({id:rows[i].id,p:{...b.curr},q:{...b.currRot}}))})}
    save(0)
    for(let i=1;i<=1200;i++){
      if(release && i<=gate.ticks){
        const q=i/gate.ticks
        bar.setNextKinematicTranslation(p(gate.x,gate.baseY+gate.lift*(3*q*q-2*q*q*q),gate.z))
      }
      step()
      for(let j=0;j<4;j++){
        if(gatePasses[j]===null&&balls[j].curr.x<gate.x)gatePasses[j]=i
        if(toes[j]===null&&balls[j].curr.x<toe)toes[j]=i
      }
      if(firstTip===null&&bodies.slice(4).some(b=>tilt(b.currRot)>60))firstTip=i
      if(i%6===0)save(i)
    }
    const angles=bodies.slice(4).map(b=>tilt(b.currRot))
    const fallen=angles.filter(a=>a>60).length
    assert(bodies.every(b=>[b.curr.x,b.curr.y,b.curr.z].every(Number.isFinite)))
    return {offset,release,held,toes,gatePasses,firstTip,fallen,angles,frames}
  }finally{
    scope.dispose()
    phy.dispose()
  }
}
const runs=[]
for(const o of [-.12,0,.12]){
  const blocked=trial(o,false), released=trial(o,true)
  assert.deepEqual(blocked.held,released.held)
  assert(blocked.gatePasses.every(x=>x===null)&&blocked.toes.every(x=>x===null)&&blocked.firstTip===null,JSON.stringify(blocked.toes))
  assert(released.toes.every(Number.isInteger)&&released.firstTip!==null&&released.fallen>0,JSON.stringify(released.toes))
  runs.push(blocked,released)
}
assert.deepEqual(trial(0,true),runs[3])
writeFileSync(proofFile,JSON.stringify({engine:'0.1.44',format:formatVersion,hz:60,gate,geometrySHA256,
  runs:runs.map(({frames,...r})=>r)},null,2)+'\n')
writeFileSync(traceFile,JSON.stringify({gate,geometrySHA256,blocked:runs[2],released:runs[3]})+'\n')
console.table(runs.map(({offset,release,gatePasses,toes,firstTip,fallen})=>({offset,release,gatePasses,toes,firstTip,fallen})))
