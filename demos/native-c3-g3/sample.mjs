import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44')
const root=dirname(packagePath)
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const out=resolve(process.argv[2])
const raw=readFileSync(join(out,'route-geometry.json'))
const data=JSON.parse(raw), hash=createHash('sha256').update(raw).digest('hex')
assert.equal(hash,'67eb5896958a84569133d9957276f394a7b5edabf1a8193c88e4d4298fc6a03d')
function path(off,roundTrip){
  const coords=[[112.4,214+off],[118.5,210.84+off],[128,202.25+off],[136.5,194.9+off],
    [145.2,186.8+off],[156,186+off],[174,186+off],[191,186+off],
    [210,186+off],[214.2+off,186.7],[215.7+off,194.8]]
  return roundTrip?coords.concat(coords.slice(0,-1).reverse()):coords
}
function run(offset,enabled,record=false){
  const course=path(offset,enabled),[x,z]=course[0]
  const host=new SimHost({version:SIM_API_VERSION,id:'c3-exact-centre-floor',seed:25,
    ground:{size:500,height:0},player:{at:{x,y:.15,z},yaw:Math.PI,speed:4.3},entities:[],quests:[],
    weapon:{id:'bench-only',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world,names=new Map()
  try {
    for(const g of data){
      if(g.asset==='apron'&&!enabled)continue
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
      names.set(c.handle,g.name==='Yard base at original zero datum'?'datum':g.asset)
    }
    for(let i=0;i<40;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const groundTicks={g2:0,office:0,infill:0,apron:0,g3:0,datum:0},frames=[]
    let leg=1,stall=0,longestStall=0,air=0,dist=0,tick=0,apronMinY=Infinity,apronMaxY=-Infinity
    for(;tick<4000&&leg<course.length&&p.position.y>-.30;tick++){
      let [a,b]=course[leg],dx=a-p.position.x,dz=b-p.position.z,left=Math.hypot(dx,dz)
      if(left<.095){
        if(++leg===course.length)break
        if(record)frames.push({tick,leg,feet:p.position.toArray()})
        ;[a,b]=course[leg];dx=a-p.position.x;dz=b-p.position.z;left=Math.hypot(dx,dz)
      }
      const prior=p.position.clone(),m=Math.min(1,left*60/4.3)
      host.step(new Map([[p.id,{moveX:m*dx/left,moveZ:m*dz/left,yaw:Math.atan2(-dx,-dz)}]]))
      const moved=Math.hypot(p.position.x-prior.x,p.position.z-prior.z)
      stall=moved<.004?stall+1:0
      longestStall=Math.max(longestStall,stall);dist+=moved
      if(!p.fall.grounded)air++
      const c=p.motor.result.groundCollider,g=c?names.get(c.handle):null
      if(g in groundTicks&&p.fall.grounded)groundTicks[g]++
      if(p.position.x>175&&p.position.x<187){apronMinY=Math.min(apronMinY,p.position.y);apronMaxY=Math.max(apronMaxY,p.position.y)}
      if(record&&tick%5===0)frames.push({tick,leg,feet:p.position.toArray(),ground:g})
    }
    return {offset,completed:leg===course.length,distanceM:dist,tick,air,longestStall,groundTicks,apronMinY,apronMaxY,frames,
      end:p.position.toArray()}
  }finally{host.dispose()}
}
const offsets=[-1.3,-.65,0,.65,1.3],samples=offsets.map(o=>run(o,true))
const full=run(0,true,true),without=run(0,false,true)
console.log(JSON.stringify({samples:samples.map(({frames,...r})=>r),without:{...without,frames:undefined}}))
assert(samples.every(s=>s.completed&&s.air===0&&s.longestStall===0&&s.groundTicks.apron>200&&s.groundTicks.g3>200&&s.groundTicks.datum===0&&s.apronMinY>.058))
assert(without.groundTicks.datum>80&&without.apronMinY<.025&&without.groundTicks.apron===0)
assert.deepEqual(full,run(0,true,true))
const proof={scope:'G2 through C3 and G3 into Titan Lane with gate assumed open. No combat, live gate or phone.',
  engine:'0.1.44',geometrySha:hash,samples,centre:full,without}
writeFileSync(join(out,'walk.json'),JSON.stringify(proof)+'\n')
