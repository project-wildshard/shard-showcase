import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [artFile,lanternFile,out]=process.argv.slice(2)
const data=JSON.parse(readFileSync(artFile))
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const ep=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(ep)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(ep),p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {GLTFLoader}=await import(pathToFileURL(join(dirname(req.resolve('three')),'../examples/jsm/loaders/GLTFLoader.js')).href)
const {Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const [ax,ay,az]=data.center
const digest=b=>createHash('sha256').update(b).digest('hex')
async function load(file,hash,placements) {
 const b=readFileSync(file);assert.equal(digest(b),hash)
 const {scene}=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')
 return placements.map(([x,y,z])=>{
  scene.position.set(ax+x,ay+y,az+z);scene.updateMatrixWorld(true)
  const p=new Vector3(),v=[],f=[]
  scene.traverse(o=>{
   if(!o.isMesh)return
   const first=v.length/3,a=o.geometry.attributes.position,g=o.geometry.index
   for(let i=0;i<a.count;i++){p.fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld);v.push(p.x,p.y,p.z)}
   for(let i=0;i<(g?.count??a.count);i++)f.push(first+(g?.getX(i)??i))
  })
  return {v:new Float32Array(v),f:new Uint32Array(f)}
 })
}
const pit=await load(new URL('../../../public/assets/wildshard-art/e8b-big-pallet-pit.glb',import.meta.url),data.pitSha256,[[0,0,0]])
const lamps=await load(lanternFile,data.lantern.sha256,data.placements.map(r=>r.local))
assert.equal(pit[0].f.length/3,10488)
assert(lamps.every(m=>m.f.length/3===data.lantern.triangles))
const q=n=>+n.toFixed(6)
function walk(path,withLamps) {
 const [[x,z],...targets]=path
 const h=new SimHost({version:SIM_API_VERSION,id:'e8b-threshold-witness',seed:8,ground:{size:500,height:0},
   player:{at:{x:ax+x,y:.15,z:az+z},yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},
  {rapier:R,ground:false})
 try {
  const w=h.physics.world,add=d=>w.createCollider(d.setCollisionGroups(groups('WORLD')))
  add(R.ColliderDesc.cuboid(36,.5,37).setTranslation(ax,-.5,az))
  for(const m of withLamps?[...pit,...lamps]:pit)add(R.ColliderDesc.trimesh(m.v,m.f))
  const p=h.players.get('actor.player')
  for(let i=0;i<30;i++)h.step()
  let ticks=0,air=0,stall=0,maxStall=0,floor=0,ok=true
  for(const [tx,tz] of targets) {
   while(Math.hypot(ax+tx-p.position.x,az+tz-p.position.z)>.10) {
    if(stall===24||ticks===2000){ok=false;break}
    const v=p.position.clone(),dx=ax+tx-v.x,dz=az+tz-v.z,r=Math.hypot(dx,dz)
    h.step(new Map([[p.id,{moveX:dx/r,moveZ:dz/r,yaw:Math.atan2(-dx,-dz)}]]))
    if(!p.fall.grounded)air++
    if(p.position.y>.055&&Math.hypot(p.position.x-ax,p.position.z-az)<11.5)floor++
    stall=p.position.distanceTo(v)<.004?stall+1:0
    maxStall=Math.max(maxStall,stall);ticks++
   }
   if(!ok)break
  }
  return {ok,ticks,air,maxStall,floor,end:[q(p.position.x-ax),q(p.position.z-az)]}
 } finally {h.dispose()}
}
const passages=[]
for(const x of [-2.15,-1.07,0,1.07,2.15])for(const side of [-1,1]){
 const path=[[x,20*side],[x,0],[x,-20*side]],before=walk(path,false),after=walk(path,true)
 assert.deepEqual(after,before)
 assert(after.ok&&after.air===0&&after.maxStall===0&&after.floor>250,JSON.stringify({x,side,after}))
 passages.push({x,side,...after})
}
const shoulders=[]
for(const {local:[x,,z]} of data.placements){
 const sign=Math.sign(z),path=[[x,z+sign*3.2],[x,z-sign*1.0]]
 const after=walk(path,true),before=walk(path,false)
 assert(before.ok&&!after.ok&&after.maxStall===24&&Math.abs(after.end[1])>15.8,JSON.stringify({after,before}))
 shoulders.push({x,z,after,before})
}
writeFileSync(out,JSON.stringify({...data,engine:'0.1.44',scope:'Exact art on a flat stock walk fixture; no actor, stun, native level, or encounter install.',passages,shoulders},null,2)+'\n')
console.log('Cleared',passages.length,'through routes with exact lamp-off parity; blocked',shoulders.length,'shoulder approaches.')
