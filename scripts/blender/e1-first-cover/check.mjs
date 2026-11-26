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
function run(row,offset,hasArt,onRoad=false){
 const c=Math.cos(row.ry),s=Math.sin(row.ry)
 const start=onRoad?[8,-7]:[row.x+offset*c+3.4*s,row.z-offset*s+3.4*c]
 const sim=new SimHost({version:SIM_API_VERSION,id:'e1-cover-witness',seed:7,ground:{size:500,height:0},
  player:{at:{x:start[0],y:.04,z:start[1]},yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},
 {rapier:R,ground:false})
 try {
  const w=sim.physics.world
  const add=d=>w.createCollider(d.setCollisionGroups(groups('WORLD')))
  add(R.ColliderDesc.cuboid(100,.5,100).setTranslation(30,-.5,0))
  if(hasArt)for(const m of mesh)add(R.ColliderDesc.trimesh(new Float32Array(m.vertices),new Uint32Array(m.indices)))
  const pl=sim.players.get('actor.player')
  for(let i=0;i<24;i++)sim.step()
  assert(pl.fall.grounded)
  let airborne=0
  const move=(x,z,ticks)=>{for(let i=0;i<ticks;i++){sim.step(new Map([[pl.id,{moveX:x,moveZ:z,yaw:0}]]));airborne+=!pl.fall.grounded}}
  if(onRoad)move(1,0,600)
  else move(-s,-c,123)
  const [x,y,z]=pl.position.toArray()
  const stop=(x-row.x)*s+(z-row.z)*c
  assert.equal(airborne,0)
  if(onRoad)assert(x>49&&Math.abs(z+7)<.001,{x,y,z})
  else if(hasArt&&offset===0)assert(stop>.49&&stop<1.15,{offset,stop})
  else assert(stop<-4,{offset,stop})
  return {coverX:row.x,localStartX:offset,hasArt,onRoad,final:[x,y,z].map(round),
    ...(onRoad?{}:{finalLocalZ:round(stop)}),airborne}
 }finally{sim.dispose()}
}
const runs=data.rows.flatMap(row=>[run(row,0,true),run(row,0,false),...[-2.8,2.8].map(x=>run(row,x,true))])
runs.push(run(data.rows[0],0,true,true))
writeFileSync(out,JSON.stringify({...data,geometry_sha256:createHash('sha256').update(raw).digest('hex'),
  engine:'0.1.44',stockPlayer:runs},null,2)+'\n')
console.table(runs)
