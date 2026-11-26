import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const [output,comparison]=process.argv.slice(2)
assert(output&&comparison)
const req=createRequire(process.env.WSC_NODE_PROJECT?
  join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const pkg=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(pkg)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(pkg),p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {CharacterMotor}=await at('src/shared/engine/physics/CharacterMotor.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),
  'rapier_wasm3d_bg.wasm')))
const pin=readFileSync(new URL('../../project/layouts/w9a-rock-squeeze-study.json',import.meta.url))
const layout=JSON.parse(pin)
const [xc,_,zc]=layout.north_x_y_z_world
assert.deepEqual(layout.south_x_y_z_world,[xc,0,zc+60])
const profile=layout.profile, shaft=layout.shaft_bottom_half_size_m[0]
assert.deepEqual(layout.squeeze_station_interval_m,[28,32])
const vertices=[],indices=[]
for(const [s,z,w,h] of profile){
  for(const [dx,dy] of [[-w,0],[-w*.91,h*.42],[-w*.71,h*.82],[-shaft,h],
    [0,h],[shaft,h],[w*.71,h*.82],[w*.91,h*.42],[w,0],[0,0]])vertices.push(xc+dx,z+dy,zc+s)
}
for(let i=0;i+1<profile.length;i++)for(let j=0;j<10;j++){
  if(profile[i][0]===23&&[3,4].includes(j))continue  // existing open shaft
  const a=i*10+j,b=i*10+(j+1)%10
  indices.push(a,b,b+10,a,b+10,a+10)
}
const geom=new Float32Array(vertices),faces=new Uint32Array(indices)
const round=x=>+x.toFixed(6)
function run(side,offset,crouch,alternate,trace=false){
  const start=side===1?-2.5:62.5,goal=side===1?61.5:-1.5
  const sim=new SimHost({version:SIM_API_VERSION,id:'w9a-cave-squeeze-rehearsal',seed:90,
    ground:{size:500,height:-20},player:{at:{x:xc+offset,y:.039,z:zc+start},yaw:0,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
  try{
    const p=sim.players.get('actor.player'),w=sim.physics.world,k=groups('WORLD')
    assert.equal(p.motor.opts.height,1.8)
    if(alternate){
      const o={...p.motor.opts,height:1.02}
      p.detachMotor()
      p.attachMotor(new CharacterMotor(sim.physics,o))
      p.motor.resetAt(p.position)
    }
    for(const s of [-4,64])w.createCollider(R.ColliderDesc.cuboid(5,.2,4)
      .setTranslation(xc,-.2,zc+s).setCollisionGroups(k))
    w.createCollider(R.ColliderDesc.trimesh(geom,faces).setCollisionGroups(k))
    for(let i=0;i<28;i++)sim.step()
    assert(p.fall.grounded)
    let air=0,low=0,stop=0,kinks=0,narrowSamples=0,maxAbsX=0,prior=p.position.z
    const frames=[],all=[];const push={commandVersion:1,moveX:0,moveZ:side,yaw:side===1?Math.PI:0,crouch}
    for(let i=1;i<=5000;i++){
      sim.step(new Map([[p.id,push]]))
      const feet=p.position.toArray().map(round), s=feet[2]-zc
      air+=Number(!p.fall.grounded)
      if(s>28&&s<32)narrowSamples++
      if(feet[1]<-6.05)low++
      maxAbsX=Math.max(maxAbsX,Math.abs(feet[0]-xc))
      if((feet[2]-prior)*side<-.003)kinks++
      stop=Math.abs(feet[2]-prior)<.001?stop+1:0
      if(trace&&(i%9===0||stop===46))frames.push(feet)
      prior=feet[2]
      all.push(feet)
      if((s-goal)*side>=0||stop>=46||feet[1]<-7)break
    }
    const last=all.at(-1),s=last[2]-zc
    return {side,offset,crouch,height:p.motor.opts.height,cleared:(s-goal)*side>=0,
      last,air,low,kinks,narrowSamples,maxAbsX:round(maxAbsX),ticks:all.length,
      ...(trace?{frames}: {})}
  }finally{sim.dispose()}
}
const trials=[]
for(const side of [1,-1])for(const offset of [-.15,0,.15]){
  for(const [crouch,alt] of [[false,false],[true,false],[true,true]])trials.push(run(side,offset,crouch,alt))
}
console.log(trials.map(r=>[r.side,r.offset,r.crouch,r.height,r.cleared,r.last,r.air,r.low,r.narrowSamples,r.ticks]))
assert(trials.every(r=> r.height===1.8 ? !r.cleared&&r.last[2]>40&&r.last[2]<49 :
  r.cleared&&r.narrowSamples>70&&r.low===0&&r.air===0))
const series=[run(1,0,true,false,true),run(1,0,true,true,true),run(-1,0,true,true,true)]
assert.deepEqual(series[1],run(1,0,true,true,true))
const notes={scope:'Rapier on the pinned static 60 m cave liner. Existing crouch uses the 1.80 m stock capsule. The 1.02 m candidate replaces the capsule before the first tick; no stance transitions or live terrain holes.',
  engine:'0.1.44',sourceSha256:createHash('sha256').update(pin).digest('hex'),triangles:faces.length/3,
  trials}
writeFileSync(output,JSON.stringify(notes,null,2)+'\n')
writeFileSync(comparison,JSON.stringify(series)+'\n')
