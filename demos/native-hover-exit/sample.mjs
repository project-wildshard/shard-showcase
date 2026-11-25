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

// Bounded exit calibration: unchanged assembled surface and stock release/counter-input.
// The wall is a stop plane in this study; its collider is not installed in the fixture.
assert.equal(process.argv.length, 6, 'Expected base, receiver, replay and proof files')
const digest = bytes => createHash('sha256').update(bytes).digest('hex')
const baseRaw = readFileSync(process.argv[2]), receiverRaw = readFileSync(process.argv[3])
assert.equal(digest(baseRaw),'b4bbdedf55a33ec120497bd36578aa8a96d2eceb1e96cc24ab6b20c410a24b27')
assert.equal(digest(receiverRaw),'ecab77f1b4cf1b7b51d9d6f9ef87eb78591602073c3f1d12e2c649e979b02d89')
const receiver = JSON.parse(receiverRaw), geometry = [...JSON.parse(baseRaw), receiver]
const laneZ = receiver.fit.lane_z, wallX = receiver.fit.rollout_end - receiver.fit.wall_clearance_m
const routes = [
  {key:'early-release', at:-171, kind:'coast'},
  {key:'late-release', at:-195, kind:'coast'},
  {key:'counter-input', at:-193, kind:'counter'},
  {key:'rollout-left', at:-198, kind:'turn', turn:-31},
  {key:'rollout-right', at:-198, kind:'turn', turn:31},
  {key:'rollout-hard-left', at:-196, kind:'turn', turn:-78},
  {key:'rollout-hard-right', at:-196, kind:'turn', turn:78},
  {key:'shelf-left', at:-176, kind:'turn', turn:-35},
  {key:'shelf-right', at:-176, kind:'turn', turn:35},
]
const runs = []
for(const offset of [-.75,0,.75]) for(const route of routes) {
  const host = new SimHost({version:SIM_API_VERSION,id:'w5a-exit-bench',seed:25,
    ground:{size:500,height:0},player:{at:{x:-114,y:.18,z:laneZ+offset},yaw:Math.PI/2,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p = host.players.get('actor.player'), W = host.physics.world
  try {
    for(const g of geometry) {
      W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
    }
    for(let i=0;i<50;i++)host.step()
    const frames = [], hp0 = p.health.attributes.health
    let on = false, stop = false, minHP = hp0, start, side, passedWall = false
    for(let tick=0;tick<850;tick++) {
      if(!on && p.position.x<=route.at) {on=true;start=tick}
      let yaw = Math.PI/2, moveX = -1, moveZ = 0
      if(on) {
        if(route.kind==='coast' || stop) moveX=0
        if(route.kind==='counter' && !stop) {
          if(p.velocity.x>=-.2) {stop=true;moveX=0}
          else moveX=1  // reverse command released at zero; holding it is not a dedicated brake
        }
        if(route.kind==='turn') {
          // Six ordinary frames progressively rotate the heading and forward input.
          yaw+=route.turn*Math.PI/180*Math.min(1,(tick-start+1)/6)
          moveX=-Math.sin(yaw); moveZ=-Math.cos(yaw)
          if(Math.abs(p.position.z-laneZ)>=3.15){moveX=0; moveZ=0; stop=true}
        }
      }
      host.step(new Map([[p.id,{moveX,moveZ,yaw,...(tick===0?{hover:true}:{})}]]))
      assert(p.board.on)
      const f = {tick,feet:p.position.toArray(),v:p.velocity.toArray(),ground:p.board.onGround,air:p.board.hoverAir}
      frames.push(f)
      minHP = Math.min(minHP,p.health.attributes.health)
      if(on && !side && Math.abs(f.feet[2]-laneZ)>2.3) side=f
      if(f.feet[0]<=wallX){passedWall=true;break} // terminate before pretending a collision was simulated
      if(on && (route.kind!=='turn'||stop) && Math.abs(f.v[0])+Math.abs(f.v[2])<.051 && f.ground) break
    }
    const first = frames[start-1], last = frames.at(-1)
    assert(first && last.tick<849 && frames.every(f=>f.feet.every(Number.isFinite)))
    runs.push({key:route.key,offset,minHP,start:first,side:side??null,last,passedWall,
      distanceX:first.feet[0]-last.feet[0],speedAtEnd:Math.hypot(last.v[0], last.v[2]),
      minAfterY:Math.min(...frames.slice(start).map(f=>f.feet[1])),
      clearanceM:last.feet[0]-wallX,groundAtEnd:last.ground,airTicks:frames.filter(f=>f.air).length,frames})
  } finally {host.dispose()}
}
for (const r of runs) {
  const clearance = r.last.feet[0] - wallX
  assert.equal(r.minHP, 100)
  assert.equal(r.airTicks, 0)
  if (r.key==='early-release') assert(clearance>3 && r.distanceX>32 && r.groundAtEnd)
  else if (r.key==='late-release') assert(r.passedWall && r.speedAtEnd>=11.9)
  else if (r.key==='counter-input') assert(clearance>1.8 && r.distanceX<12 && r.groundAtEnd)
  else if (r.key.startsWith('rollout-hard')) assert(clearance>1.1 && r.side.feet[1]<.43 && r.groundAtEnd)
  else if (r.key.startsWith('rollout-')) assert(r.passedWall && r.speedAtEnd>13.5 && r.side.feet[1]<.43)
  else if (r.key.startsWith('shelf-')) assert(r.side.feet[1]>5.2 && r.last.feet[1]<.48 && r.passedWall)
  else assert.fail(r.key)
}
const proof = {engine:'0.1.44',hz:60,wallPlaneX:wallX,wallCollision:false,
  geometrySHA256:digest(baseRaw),receiverSHA256:digest(receiverRaw),routes,
  runs:runs.map(({frames,...r})=>r)}
writeFileSync(process.argv[4],JSON.stringify({results:runs.filter(r=>r.offset===0)})+'\n')
writeFileSync(process.argv[5],JSON.stringify(proof,null,2)+'\n')
console.table(proof.runs.map(r=>[r.key,r.offset,r.passedWall,r.distanceX.toFixed(2),
 r.speedAtEnd.toFixed(2),r.minHP,r.side?.feet[1].toFixed(2),r.last.feet.map(x=>x.toFixed(2)).join(',')]))
