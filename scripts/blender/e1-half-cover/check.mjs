import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [receipt,geom,out]=process.argv.slice(2)
const data=JSON.parse(readFileSync(receipt)), raw=readFileSync(geom), mesh=JSON.parse(raw)
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(engine)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(engine),p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const round=n=>+n.toFixed(6)
// Local X is across the straight barrier, positive Z points into the return.
// Transform against all nine placements, not a camera-plane proxy.
function run(row,path,withCover){
 const c=Math.cos(row.ry),s=Math.sin(row.ry)
 const point=([x,z])=>[row.x+x*c+z*s,row.z-x*s+z*c]
 const [x,z]=point(path[0])
 const host=new SimHost({version:SIM_API_VERSION,id:'e1-half-cover',seed:7,
   ground:{size:500,height:0},player:{at:{x,y:.05,z},yaw:0,speed:4.3},entities:[],quests:[],
   weapon:{id:'disabled',damage:0}}, {rapier:R,ground:false})
 try {
  const world=host.physics.world
  const add=d=>world.createCollider(d.setCollisionGroups(groups('WORLD')))
  add(R.ColliderDesc.cuboid(145,.50,145).setTranslation(66,-.50,-50))
  if(withCover)for(const m of mesh)add(R.ColliderDesc.trimesh(new Float32Array(m.vertices),new Uint32Array(m.indices)))
  const p=host.players.get('actor.player')
  for(let i=0;i<35;i++)host.step()
  assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
  let air=0,stall=0,longest=0,ticks=0,done=true
  for(const shall of path.slice(1)){
   const [tx,tz]=point(shall)
   while(Math.hypot(tx-p.position.x,tz-p.position.z)>.10){
    if(ticks>=2000||stall>=24){done=false;break}
    const before=p.position.clone(),dx=tx-before.x,dz=tz-before.z
    const d=Math.hypot(dx,dz),xx=dx/d,zz=dz/d
    host.step(new Map([[p.id,{moveX:xx,moveZ:zz,yaw:Math.atan2(-xx,-zz)}]]))
    if(!p.fall.grounded)air++
    stall=Math.hypot(p.position.x-before.x,p.position.z-before.z)<.004?stall+1:0
    longest=Math.max(longest,stall);ticks++
   }
   if(!done)break
  }
  const dx=p.position.x-row.x,dz=p.position.z-row.z
  return {withCover,done,air,longest,ticks,endLocal:[round(dx*c-dz*s),round(dx*s+dz*c)],
    endWorld:[round(p.position.x),round(p.position.z)]}
 } finally{host.dispose()}
}
const scenarios={
 face:[[0,-3.1],[0,3.3]],return:[[5.9,1.52],[.75,1.52]],
 left:[[-3.18,-2.2],[-3.18,3.35]],right:[[3.98,-2.2],[3.98,3.35]],
}
const runs=[]
for(const row of data.rows){
 for(const [name,path] of Object.entries(scenarios)){
  const r=run(row,path,true)
  if(name==='face')assert(!r.done&&r.longest>=24&&r.endLocal[1]<-.47&&r.endLocal[1]>-.94,JSON.stringify({name,row,r}))
  else if(name==='return')assert(!r.done&&r.longest>=24&&r.endLocal[0]>3.60&&r.endLocal[0]<3.86,JSON.stringify({name,row,r}))
  else assert(r.done&&r.longest===0,JSON.stringify({name,row,r}))
  assert.equal(r.air,0);runs.push({x:row.x,name,...r})
  if(name==='face'||name==='return'){
   const control=run(row,path,false)
   assert(control.done&&control.air===0,JSON.stringify(control))
   runs.push({x:row.x,name,...control})
  }
 }
}
// With yaw 0 these local coordinates are the world coordinates.
const road=run({x:0,z:0,ry:0},[[8,-7],[117,-7]],true)
assert(road.done&&road.air===0&&road.longest===0&&road.endWorld[0]>116.8)
const closest=data.rows.map(r=>round(Math.min(...data.dayPacks.map(p=>Math.hypot(p.x-r.x,p.z-r.z)))))
const result={...data,scope:'Exact archived Band 1 half-cover proposal with flat native movement witness; no terrain install, AI/aggro, combat or phone validation.',
  geometrySHA256:createHash('sha256').update(raw).digest('hex'),engine:'0.1.44',
  colliderTrianglesEach:mesh[0].indices.length/3,runs,road,closestOriginalDayPackCenterByAnchorM:closest}
writeFileSync(out,JSON.stringify(result,null,2)+'\n')
console.log(JSON.stringify({candidateBlocks:runs.filter(r=>r.withCover&&!r.done).length,
 controls:runs.filter(r=>!r.withCover).length,flanks:runs.filter(r=>r.withCover&&r.done).length,
 road,closest,clearance:data.roadClearances,colliderTrianglesEach:result.colliderTrianglesEach,model:data.model}))
