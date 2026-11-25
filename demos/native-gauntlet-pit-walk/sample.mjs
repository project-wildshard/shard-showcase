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

const entrances=[48,76]
const approach=offset=>[[30+offset,185.25],[30+offset,194.5]]
function course(lane,offset){
  const x=entrances[lane]+offset
  return [...approach(offset),[x,194.5],[x,207.25],
    ...(lane===0?[[48+offset,211],[45+offset,217],[65+offset,217],[76+offset,217]]:[[x,217]]),
    [89+offset,214],[96.8,214+offset],[107.5,214+offset]]
}
function play(route){
  const [x,z]=route[0]
  const host=new SimHost({version:SIM_API_VERSION,id:'e11c-c2-pit-walk',seed:25,
    ground:{size:500,height:0},player:{at:{x,y:1.25,z},yaw:Math.PI,speed:4.3},
    entities:[],quests:[],weapon:{id:'bench-only',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  try{
    for(const g of geometry)W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles))
      .setCollisionGroups(groups('WORLD')))
    for(let k=0;k<55;k++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded,JSON.stringify(p.position.toArray()))
    let i=1,stall=0,longestStall=0,air=0,longestAir=0,totalDistance=0,airTicks=0
    const frames=[],waypoints=[]
    for(let tick=1;tick<=2200&&i<route.length;tick++){
      let [tx,tz]=route[i], dx=tx-p.position.x,dz=tz-p.position.z,left=Math.hypot(dx,dz)
      if(left<.105){
        waypoints.push({tick,index:i,feet:p.position.toArray()})
        if(++i===route.length)break
        ;[tx,tz]=route[i]
        dx=tx-p.position.x;dz=tz-p.position.z;left=Math.hypot(dx,dz)
      }
      const last=p.position.clone(), mag=Math.min(1,left*60/4.3)
      host.step(new Map([[p.id,{moveX:mag*dx/left,moveZ:mag*dz/left,yaw:Math.atan2(-dx,-dz)}]]))
      const moved=Math.hypot(p.position.x-last.x,p.position.z-last.z)
      totalDistance+=moved
      stall=moved<.004?stall+1:0
      longestStall=Math.max(stall,longestStall)
      air=p.fall.grounded?0:air+1
      if(air)airTicks++
      longestAir=Math.max(air,longestAir)
      if(tick%6===0||stall===40||tick===1)frames.push({tick,segment:i,feet:p.position.toArray(),grounded:p.fall.grounded})
      if(stall>=40||p.position.y<-.4)break
    }
    return {route,complete:i===route.length,longestStall,longestAir,airTicks,totalDistance,last:p.position.toArray(),waypoints,frames}
  }finally{host.dispose()}
}

const cases=[0,1].flatMap(l=>[-.64,0,.64].map(o=>[l,o]))
const samples=cases.map(([lane,offset])=>({lane,offset,...play(course(lane,offset))}))
const stop=course(1,0).concat([[114,214]])
const wall=play(stop)
const pillar=play([[30,185.25],[30,194.5],[48,194.5],[48,207.25],[40,207.25],[40,214]])
for(const r of [...samples,wall,pillar])console.log(JSON.stringify({...r,frames:undefined,waypoints:r.waypoints.slice(-2)}))
assert(samples.every(r=>r.complete&&r.longestStall===0&&r.airTicks===0
  && r.waypoints[1].feet[1]>2.49 && r.waypoints[2].feet[1]<.04))
assert(samples.every(r=>r.last[0]>107.3&&r.last[0]<107.6))
assert(!wall.complete&&wall.longestStall===40&&wall.last[0]>108&&wall.last[0]<109.6)
assert(!pillar.complete&&pillar.longestStall===40&&pillar.last[2]>212&&pillar.last[2]<213)
assert.deepEqual(play(course(0,0)),Object.fromEntries(Object.entries(samples[1]).filter(([k])=>k!=='lane'&&k!=='offset')))
writeFileSync(process.argv[3],JSON.stringify({engine:'0.1.44',clockHz:60,geometrySha256:hash,
  meshes:geometry.length,triangles:geometry.reduce((s,g)=>s+g.triangles.length/3,0),samples,wall,pillar})+'\n')
