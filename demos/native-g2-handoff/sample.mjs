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
const raw=readFileSync(process.argv[2]), {original,extension,capName}=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
assert.equal(hash,"b5f0dc55342c6d2799240d88c01f8dc08342938dd53fa38517994c4110490175")

const entrances=[48,76]
function course(lane,offset){
  const x=entrances[lane]+offset, ramp=(lane===0?30:80)+offset
  return [[62+offset,118],[62+offset,126],[62+offset,146],[ramp,146],[ramp,160],
    ...(lane===0?[[29+offset,172],[30+offset,181]]:[[80+offset,162],[68+offset,177],[30+offset,181]]),
    [30+offset,194.5],[x,194.5],[x,207.25],
    ...(lane===0?[[48+offset,211],[45+offset,217],[65+offset,217],[76+offset,217]]:[[x,217]]),
    [89+offset,214],[96.8,214+offset],[107.5,214+offset]]
}
function play(route,retainCap){
  const geometry=[...original.filter(g=>retainCap||g.name!==capName||g.asset!=='c2-pit'),...extension]
  const [x,z]=route[0]
  const host=new SimHost({version:SIM_API_VERSION,id:'e11c-g2-c3-threshold',seed:25,
    ground:{size:500,height:0},player:{at:{x,y:.13,z},yaw:Math.PI,speed:4.3},
    entities:[],quests:[],weapon:{id:'bench-only',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  try{
    for(const g of geometry)W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles))
      .setCollisionGroups(groups('WORLD')))
    for(let k=0;k<55;k++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded,JSON.stringify(p.position.toArray()))
    let i=1,stall=0,longestStall=0,air=0,longestAir=0,totalDistance=0,airTicks=0
    const frames=[],waypoints=[]
    for(let tick=1;tick<=4800&&i<route.length;tick++){
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
const samples=cases.map(([lane,offset])=>({lane,offset,...play(course(lane,offset).concat(
  [[110,214+offset],[115,214+offset],[120.77,209.50+offset],[128.5,202.0+offset],[130.1,200.3+offset]]),false)}))
const capped=play(course(1,0).concat([[115,214]]),true)
const side=play(course(1,0).concat([[113,214],[113,219.4]]),false)
const concise=({frames,route,waypoints,...r})=>r
for(const r of [...samples,capped,side])console.log(JSON.stringify(concise(r)))
assert(samples.every(r=>r.complete&&r.longestStall===0&&r.airTicks===0&&r.last[0]>129.9))
assert(samples.every(r=>r.last[1]>.045&&r.last[1]<.10))
assert(!capped.complete&&capped.longestStall===40&&capped.last[0]>108&&capped.last[0]<109.6)
assert(!side.complete&&side.longestStall===40&&side.last[2]>216&&side.last[2]<217.7)
const r=samples[1]
assert.deepEqual(play(r.route,false),Object.fromEntries(Object.entries(r).filter(([k])=>k!=='lane'&&k!=='offset')))
writeFileSync(process.argv[3],JSON.stringify({scope:'G2 walk into an authored C3 entrance sector, not full C3.',
  engine:'0.1.44',clockHz:60,geometrySha256:hash,removedFromOpenFixture:capName,
  originalMeshes:original.length,extensionMeshes:extension.length,samples,capped,side})+'\n')
