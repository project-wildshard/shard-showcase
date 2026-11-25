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

// Match the exact D7 and receiver inputs used by the prior plane-only study.
assert.equal(process.argv.length,7,'Expected base, receiver, wall, replay and proof paths')
const digest=bytes=>createHash('sha256').update(bytes).digest('hex')
const [baseRaw,receiverRaw,wallRaw]=process.argv.slice(2,5).map(p=>readFileSync(p))
assert.equal(digest(baseRaw),'b4bbdedf55a33ec120497bd36578aa8a96d2eceb1e96cc24ab6b20c410a24b27')
assert.equal(digest(receiverRaw),'ecab77f1b4cf1b7b51d9d6f9ef87eb78591602073c3f1d12e2c649e979b02d89')
assert.equal(digest(wallRaw),'21ac39a18de8c934083b4205cbd57ce48ef6423de2780ce3d2f688bbdaf57f09')
const receiver=JSON.parse(receiverRaw), wall=JSON.parse(wallRaw)
const base=[...JSON.parse(baseRaw),receiver]
const laneZ=receiver.fit.lane_z
const wallX=receiver.fit.rollout_end-receiver.fit.wall_clearance_m
const runs=[], contacts=[]
for (const installed of [false,true]) for(const releaseX of [-171,-195]) for(const offset of [-.75,0,.75]) {
  const host=new SimHost({version:SIM_API_VERSION,id:'w5a-wall-bench',seed:25,
    ground:{size:500,height:0},player:{at:{x:-114,y:.18,z:laneZ+offset},yaw:Math.PI/2,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  try {
    for(const g of installed?[...base,...wall]:base)
      host.physics.world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
    const p=host.players.get('actor.player')
    for(let i=0;i<50;i++)host.step()
    const frames=[]
    let release=-1, hp=100
    for(let tick=0;tick<850;tick++){
      if(release<0&&p.position.x<=releaseX)release=tick
      host.step(new Map([[p.id,{moveX:release<0?-1:0,moveZ:0,yaw:Math.PI/2,...(tick===0?{hover:true}:{})}]]))
      assert(p.board.on)
      hp=Math.min(hp,p.health.attributes.health)
      frames.push({tick,feet:p.position.toArray(),v:p.velocity.toArray(),ground:p.board.onGround,air:p.board.hoverAir})
      if(release>=0&&tick>=release+330)break
    }
    assert(release>0&&frames.length>=release+300&&frames.every(f=>f.feet.every(Number.isFinite)))
    const after=frames.slice(release), passed=after.find(f=>f.feet[0]<=wallX)
    runs.push({installed,releaseX,offset,hp,release,passed:passed??null,minX:Math.min(...after.map(f=>f.feet[0])),
      last:frames.at(-1),frames})
  } finally {host.dispose()}
}
for(const offset of [-.75,0,.75]){
  const r=(installed,x)=>runs.find(v=>v.installed===installed&&v.releaseX===x&&v.offset===offset)
  assert.deepEqual(r(false,-171).frames,r(true,-171).frames)
  assert(!r(true,-171).passed)
  assert(r(false,-195).passed)
  const withWall=r(true,-195), withoutWall=r(false,-195)
  assert.equal(withWall.release,withoutWall.release)
  assert(!withWall.passed)
  assert(runs.every(run=>run.hp===100&&run.last.ground))
  assert(withWall.minX>-206.601&&withWall.minX<-206.599)
  const tick=withWall.frames.findIndex((f,i)=>f.feet[0]-withoutWall.frames[i].feet[0]>.01)
  assert(tick>withWall.release)
  const x=(run,i)=>run.frames[i].feet[0]
  const incomingMps=60*(x(withWall,tick-2)-x(withWall,tick-1))
  const nextTickMps=60*Math.abs(x(withWall,tick)-x(withWall,tick+1))
  assert(incomingMps>11.8&&incomingMps<12.4&&nextTickMps<.20)
  withWall.contactTick=tick
  contacts.push({offset,tick,incomingMps,nextTickMps,
    stoppedCenterX:withWall.last.feet[0],controlCenterX:withoutWall.last.feet[0]})
}
const wallSHA256=digest(wallRaw)
console.table(runs.map(r=>[r.installed,r.releaseX,r.offset,r.hp,r.minX.toFixed(3),
  r.last.feet.map(x=>x.toFixed(3)).join(','),r.passed?.tick]))
writeFileSync(process.argv[5],JSON.stringify({wallX,results:runs.filter(r=>r.offset===0)})+'\n')
writeFileSync(process.argv[6],JSON.stringify({engine:'0.1.44',hz:60,wallX,geometrySHA256:digest(baseRaw),
  receiverSHA256:digest(receiverRaw),wallSHA256,contacts,runs:runs.map(({frames,...r})=>r)},null,2)+'\n')
