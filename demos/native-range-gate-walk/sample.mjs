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
assert(process.argv[2]&&process.argv[3],'Expected geometry input and replay JSON output')
const raw=readFileSync(process.argv[2]), geometry=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
const rows=offset=>[[-36+offset,54],[-36+offset,79.90],[-23+offset,79.90],[-23+offset,120]]
const dt=1/60
function play(offset,wall=false){
  const route=rows(offset), [x,z]=route[0]
  const host=new SimHost({version:SIM_API_VERSION,id:'w12-range-gate-walk-bench',seed:25,
    ground:{size:500,height:.1},player:{at:{x,y:.18,z},yaw:Math.PI,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  try{
    for(const g of geometry)W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles))
      .setCollisionGroups(groups('WORLD')))
    if(wall)W.createCollider(R.ColliderDesc.cuboid(2.2,1,.18).setTranslation(-36,1,62)
      .setCollisionGroups(groups('WORLD')))
    for(let k=0;k<50;k++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    let waypoint=1,stall=0,longestStall=0,longestAir=0,air=0,totalDistance=0
    const frames=[],turns=[]
    for(let tick=1;tick<=1600&&waypoint<route.length;tick++){
      let [tx,tz]=route[waypoint]
      let dx=tx-p.position.x,dz=tz-p.position.z,left=Math.hypot(dx,dz)
      if(left<.10){
        turns.push({tick,waypoint,feet:p.position.toArray()})
        waypoint++
        if(waypoint===route.length)break
        ;[tx,tz]=route[waypoint]
        dx=tx-p.position.x;dz=tz-p.position.z;left=Math.hypot(dx,dz)
      }
      const start=p.position.clone()
      const speed=Math.min(1,left/(4.3*dt))
      host.step(new Map([[p.id,{moveX:speed*dx/left,moveZ:speed*dz/left,
        yaw:Math.atan2(-dx,-dz)}]]))
      const moved=Math.hypot(p.position.x-start.x,p.position.z-start.z)
      totalDistance+=moved
      stall=moved<.004?stall+1:0
      longestStall=Math.max(longestStall,stall)
      air=p.fall.grounded?0:air+1
      longestAir=Math.max(longestAir,air)
      const row={tick,segment:waypoint,feet:p.position.toArray(),grounded:p.fall.grounded}
      if(tick%6===0||stall===30||tick===1)frames.push(row)
      if(stall>=30||p.position.y<-.4)break
    }
    return {offset,route,waypoints:turns,complete:waypoint===route.length,longestStall,longestAir,
      totalDistance,last:p.position.toArray(),frames,blockedMouth:wall}
  }finally{host.dispose()}
}
const samples=[-.65,0,.65].map(offset=>play(offset))
const wall=play(0,true)
for(const run of samples){
  console.log(JSON.stringify({...run,frames:[]}))
}
console.log('Control:',JSON.stringify({...wall,frames:[]}))
assert(samples.every(r=>r.complete&&r.longestStall===0&&r.longestAir===0))
assert(!wall.complete&&wall.longestStall===30&&wall.last[2]<62)
assert.deepEqual(samples[1],play(0))
writeFileSync(process.argv[3],JSON.stringify({engine:'0.1.44',clockHz:60,geometrySha256:hash,
  meshes:geometry.length,triangles:geometry.reduce((s,g)=>s+g.triangles.length/3,0),samples,wall})+'\n')
