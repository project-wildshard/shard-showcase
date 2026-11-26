// Verify player access around the exported cover using the real player motor.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const [input,receipt,out]=process.argv.slice(2)
assert(input&&receipt&&out)
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const engine=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(engine)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(engine),p)).href)
await at('scripts/sim-node-loader.mjs')
const { SimHost }=await at('src/server/engine/sim.ts')
const { SIM_API_VERSION }=await at('src/shared/engine/sim/apiVersion.ts')
const { loadRapier }=await at('src/shared/engine/physics/rapier.ts')
const { groups }=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const bytes=readFileSync(input), meshes=JSON.parse(bytes)
const art=JSON.parse(readFileSync(receipt))
const r=x=>+x.toFixed(5)
function run(x,withStop){
  const sim=new SimHost({version:SIM_API_VERSION,id:'e2-lane-fixture-bench',seed:29,
    ground:{size:500,height:0},player:{at:{x,y:.035,z:0},yaw:0,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
  try {
    const phys=sim.physics.world
    const collider=c=>phys.createCollider(c.setCollisionGroups(groups('WORLD')))
    collider(R.ColliderDesc.cuboid(25,1,25).setTranslation(0,-1,0))
    const selected=[...meshes.crates,...(withStop?meshes.stop:[])]
    for(const p of selected)collider(R.ColliderDesc.trimesh(new Float32Array(p.vertices),new Uint32Array(p.indices)))
    const p=sim.players.get('actor.player')
    for(let i=0;i<24;i++)sim.step()
    assert(p.fall.grounded&&p.motor.opts.radius===.38)
    const input=(a,b)=>new Map([[p.id,{moveX:a,moveZ:b,yaw:0}]])
    let airborne=0
    for(let i=0;i<195;i++) {
      sim.step(input(0,-1))
      airborne+=!p.fall.grounded
    }
    const front=p.position.toArray().map(r)
    let behind=null
    if(Math.abs(x)>1.5){
      assert(front[2]<-12)
      for(let i=0;i<27;i++) {
        sim.step(input(-Math.sign(x),0))
        airborne+=!p.fall.grounded
      }
      behind=p.position.toArray().map(r)
      assert(Math.abs(behind[0])<.25&&behind[2]<-12)
    }
    assert.equal(airborne,0)
    return {startX:x,withStop,front,behind,airborne}
  } finally {sim.dispose()}
}
const runs=[...[-.65,0,.65].flatMap(x=>[run(x,true),run(x,false)]),...[-1.85,1.85].map(x=>run(x,true))]
console.log(runs)
for(const a of runs){
  if(a.withStop&&Math.abs(a.startX)<1)assert(a.front[2]>-8.3&&a.front[2]<-7.8)
  else assert(a.front[2]<-12)
}
writeFileSync(out,JSON.stringify({...art,geometry_sha256:createHash('sha256').update(bytes).digest('hex'),
  player_bench:{scope:'Engine 0.1.44 stock player motor against exported triangle geometry on a flat test slab. No robot, hit or stun.',runs}},null,2)+'\n')
