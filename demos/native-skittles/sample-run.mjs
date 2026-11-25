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
const out=process.argv[2]
assert(out, 'Destination JSON required')
const laneZ=196, floor=.04, slope=.25, rampToe=-42, rampTop=-18
const rows=[]
for(let i=0;i<4;i++){
  const x=-19.5-1.8*i
  rows.push({id:'ball-'+(i+1),kind:'prop',shape:{ball:.8},at:{x,y:(x-rampToe)*slope+.8/Math.cos(Math.atan(slope))+.014,z:laneZ},
    yaw:0,owner:{kind:'w4b-calibration',id:'ball-'+(i+1)},material:'metal',
    density:130,friction:.70,restitution:.04,angularDamping:.08,rolling:.025,ccd:true})
}
for(let r=0;r<4;r++)for(let i=0;i<=r;i++){
  const id='pin-'+(rows.length-3)
  rows.push({id,kind:'prop',shape:{cylinder:{radius:.25,halfHeight:.645}},at:{x:-50-r*1.2,y:floor+.645+.003,z:laneZ+(i-r/2)*1.1},
    yaw:0,owner:{kind:'w4b-calibration',id},material:'wood',density:170,
    friction:.58,restitution:.04,angularDamping:.22,linearDamping:.32,rolling:.045,ccd:true})
}
const data={bodies:rows,floors:[],colliders:[]}
const p=(x,y,z)=>({x,y,z})
const dt=1/60
const tilt=q=>Math.acos(Math.max(-1,Math.min(1,1-2*(q.x*q.x+q.z*q.z))))*180/Math.PI

function trial(){
  const scope=new Scope('w4b bench')
  const phy=new Physics(R)
  try{
    const box=(pos,half)=>{
      return phy.world.createCollider(R.ColliderDesc.cuboid(...half).setTranslation(...pos)
        .setCollisionGroups(groups('WORLD')).setFriction(.8))
    }
    box([-53,floor-1,196],[39,1,27])
    // Exact 24 x 4 x 6 m original art slope. The flat handoff is the
    // overlap with the original apron, not an artificial ball launch.
    phy.world.createCollider(R.ColliderDesc.trimesh(
      new Float32Array([rampToe,0,194, rampToe,0,198,
        rampTop,6,198, rampTop,6,194]),new Uint32Array([0,1,2,0,2,3]))
      .setCollisionGroups(groups('WORLD')).setFriction(.8))
    const ops=DeclaredBodyOps.native({physics:phy,scope,playerFocus:p(-46,0,196)},data)
    const id=row=>ops.registries.bodies.get(row.id)
    for (let i=0;i<rows.length;i+=4)
      ops.prepare(rows.slice(i,i+4).map(row=>[C['body.spawn'],0,id(row),0,0])).commit()
    assert(rows.every(row=>ops.read(Reads.bodyAlive,id(row),0)===1))
    const bodies=rows.map(row=>ops.body(row.id))
    const balls=bodies.slice(0,4)
    // Explicit calibration input; not a claim that the ABI exposes a
    // gate/control or that a player can pull the art lever in the shard.
    for(const b of balls) b.setEnabled(false)
    function step(){ops.pre(dt);phy.step();ops.post(dt)}
    for(let k=0;k<120;k++)step()
    assert.deepEqual(balls.map(b=>b.rb.translation().x),rows.slice(0,4).map(r=>Math.fround(r.at.x)))
    function frame(tick){
      return {tick,bodies:bodies.map((b,i)=>({id:rows[i].id,p:{...b.curr},q:{...b.currRot},speed:b.speed}))}
    }
    const frames=[frame(0)]
    for(const b of balls)b.setEnabled(true)
    const entries=Array(4).fill(null)
    let firstTilt=null, awakePeak=0
    for(let tick=1;tick<=1200;tick++){
      step()
      awakePeak=Math.max(awakePeak,bodies.filter(b=>!b.rb.isSleeping()).length)
      if (firstTilt===null && bodies.slice(4).some(b=>tilt(b.currRot)>60)) firstTilt=tick
      for(let i=0;i<4;i++)
        if(entries[i]===null && balls[i].curr.x<rampToe)entries[i]=tick
      if(tick%6===0)frames.push(frame(tick))
    }
    const angles=bodies.slice(4).map(b=>tilt(b.currRot))
    const score=angles.filter(a=>a>60).length
    assert(entries.every(Number.isInteger),'All four balls must cross the toe')
    assert(firstTilt!==null && score>0,'No pins fell')
    assert(awakePeak<=40 && angles.every(Number.isFinite))
    assert(bodies.every(b=>b.rb.isSleeping()),'Bodies did not settle')
    return {entries,firstTilt,awakePeak,angles,score,frames}
  }finally{
    scope.dispose()
    phy.dispose()
  }
}
const one=trial(), two=trial()
assert.deepEqual(one,two,'Fresh reset must replay with no pose drift')
assert(!Object.hasOwn(Reads,'bodyTilt'),'Revisit the local tilt substitute: the ABI has changed')
writeFileSync(out,JSON.stringify({engine:'0.1.44',format:formatVersion,clockHz:60,
  ramp:{toe:rampToe,crest:rampTop,rise:6,width:4,laneZ},floor,data, ...one})+'\n')
console.log(JSON.stringify(Object.fromEntries(Object.entries(one).filter(([k])=>k!=='frames'))))
