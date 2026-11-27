import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [out,replay]=process.argv.slice(2)
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
const {Box3,Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const file='wsc-kit-003-d7-launch-wall.glb'
const b=readFileSync(new URL('../../public/assets/wildshard-art/'+file,import.meta.url))
const sha=createHash('sha256').update(b).digest('hex')
assert.equal(sha,'d1f43ef2751d732c448bb5be70359984878bf69242d1adb50b0d3e69808dcf55')
const {scene}=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')
const rows=[{id:'east',x:-216,y:0,z:142.5,yaw:0},{id:'west',x:-224,y:0,z:142.5,yaw:Math.PI}]
const geometry=rows.map(r=>{
 scene.position.set(r.x,r.y,r.z);scene.rotation.y=r.yaw;scene.updateMatrixWorld(true)
 const a=new Vector3(),v=[],f=[]
 scene.traverse(o=>{
  if(!o.isMesh)return
  const first=v.length/3,p=o.geometry.attributes.position,g=o.geometry.index
  for(let i=0;i<p.count;i++){a.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);v.push(a.x,a.y,a.z)}
  for(let i=0;i<(g?.count??p.count);i++)f.push(first+(g?.getX(i)??i))
 })
 assert.equal(f.length/3,1438)
 return {v:new Float32Array(v),f:new Uint32Array(f),bounds:new Box3().setFromObject(scene,true)}
})
assert(Math.abs(geometry[0].bounds.min.x+216)<.001&&Math.abs(geometry[1].bounds.max.x+224)<.001)
const floor={center:[-220,.013,142.5],size:[8,.021,45],top:.0235}
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const q=n=>+n.toFixed(6)
function run(dir,z,mode,installed,returnToCenter=false){
 const host=new SimHost({version:SIM_API_VERSION,id:'w5a-channel-witness',seed:4,ground:{size:500,height:0},player:{at:{x:-220,y:.05,z},yaw:0,speed:4.3},
  entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
 const w=host.physics.world,add=d=>w.createCollider(d.setCollisionGroups(groups('WORLD')))
 // Surrounding paving is a flat witness, not the authored park terrain.
 add(R.ColliderDesc.cuboid(42,.50,28).setTranslation(-220,-.50,142.5))
 add(R.ColliderDesc.cuboid(...floor.size.map(t=>t/2)).setTranslation(...floor.center))
 if(installed)for(const m of geometry)add(R.ColliderDesc.trimesh(m.v,m.f))
 try {
  const p=host.players.get('actor.player')
  for(let i=0;i<25;i++)host.step()
  const frames=[]
  let release=null,hit=null,minHP=100,reverse=null,back=null,returnRelease=null
  const toe=dir>0?-216:-224
  const move=(n)=>dir*n
  for(let i=0;i<520;i++){
   const dv=move(p.position.x-toe)
   if(release===null&&(mode===null?i>=120:dv>=mode))release=i
   if(returnToCenter&&reverse===null&&release!==null&&i>release+140)reverse=i
   if(reverse!==null&&returnRelease===null){
    const remaining=move(p.position.x+220),speed=Math.abs(p.velocity.x)
    if(remaining<=Math.max(.08,speed*speed/5.6))returnRelease=i
   }
   if(returnRelease!==null&&i>returnRelease+115){back=i;break}
   const speed=release===null?move(1):reverse!==null&&returnRelease===null?move(-.30):0
   host.step(new Map([[p.id,{moveX:speed,moveZ:0,yaw:speed<0?Math.PI/2:-Math.PI/2,...(i===0?{hover:true}:{})}]]))
   assert(p.board.on)
   minHP=Math.min(minHP,p.health.attributes.health)
   const {x,y,z}=p.position
   if(hit===null&&move(x-toe)>=0)hit=i
   frames.push([i,q(x),q(y),q(z),q(p.velocity.x),Number(p.board.onGround),Number(p.board.hoverAir)])
  }
  const maxUp=Math.max(...frames.map(f=>f[2])),reach=Math.max(...frames.map(f=>move(f[1]-toe)))
  return {side:dir>0?'east':'west',z,mode,installed,returnToCenter,release,reverse,returnRelease,back,toeContact:hit,maxUp,reach:q(reach),minHP,last:frames.at(-1),frames}
 }finally{host.dispose()}
}
const tests=[]
for(const dir of [-1,1])for(const z of [132.5,142.5,152.5]){
 for(const release of [-2.6,-2.3,-2,-1.8,-1.45])tests.push(run(dir,z,release,true,true))
 tests.push(run(dir,z,0,true))
}
for(const dir of [-1,1])tests.push(run(dir,142.5,0,false))
const roundTrips=tests.filter(t=>t.returnToCenter), controls=tests.filter(t=>!t.installed)
const toeReleases=tests.filter(t=>!t.returnToCenter&&t.installed)
for(const t of tests)assert(t.minHP===100&&t.last[5]===1&&Math.abs(t.last[4])<.01,JSON.stringify(t.last))
assert(roundTrips.length===30&&roundTrips.every(t=>t.back!==null&&t.toeContact!==null&&t.maxUp>.9&&t.reach<9&&Math.abs(t.last[1]+220)<.30))
assert(toeReleases.length===6&&toeReleases.every(t=>t.reach>16&&t.maxUp>4.55))
assert(controls.length===2&&controls.every(t=>t.maxUp<.64))
const guide={origin:[-220,0,142.5],guideXWorld:[-222,-218],centralTestRuns:roundTrips.filter(t=>t.mode===-2).length}
writeFileSync(out,JSON.stringify({engine:'0.1.44',hz:60,file,sha,rows,floor,guide,tests:tests.map(({frames,...t})=>t)},null,2)+'\n')
writeFileSync(replay,JSON.stringify(tests.filter(t=>t.z===142.5))+'\n')
