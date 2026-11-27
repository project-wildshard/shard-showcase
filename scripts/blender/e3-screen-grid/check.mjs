import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [layout,out]=process.argv.slice(2)
const raw=readFileSync(layout), d=JSON.parse(raw)
const bit=readFileSync(new URL('../../../public/assets/wildshard-art/'+d.model.name,import.meta.url))
assert.equal(createHash('sha256').update(bit).digest('hex'),d.model.sha256)
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
const rows=d.rows.filter(a=>a.installedInFixture)
const round=n=>+n.toFixed(6)
const pAt=(row,x,z)=>[row.x+x*Math.cos(row.ry)+z*Math.sin(row.ry),row.z-x*Math.sin(row.ry)+z*Math.cos(row.ry)]
function run(path,withScreen=true) {
 const [[x,z],...targets]=path
 const host=new SimHost({version:SIM_API_VERSION,id:'e3-screen-grid',seed:31,ground:{size:500,height:0},
  player:{at:{x,y:.03,z},yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
 try {
  const w=host.physics.world,add=s=>w.createCollider(s.setCollisionGroups(groups('WORLD')))
  add(R.ColliderDesc.cuboid(80,.5,85).setTranslation(175,-.5,-179))
  if(withScreen)for(const row of rows)for(const shape of d.colliders){
   const [a,y,b]=shape.center,[px,pz]=pAt(row,a,b)
   add(R.ColliderDesc.cuboid(...shape.half).setTranslation(px,y,pz)
    .setRotation({x:0,y:Math.sin(row.ry/2),z:0,w:Math.cos(row.ry/2)}))
  }
  const p=host.players.get('actor.player')
  for(let k=0;k<24;k++)host.step()
  assert(p.fall.grounded&&p.motor.opts.radius===.38)
  let air=0,maxStall=0,ticks=0,done=true,distance=0
  for(const [tx,tz] of targets){
   let stall=0
   while(Math.hypot(tx-p.position.x,tz-p.position.z)>.10) {
    if(ticks>=2400||stall>=24){done=false;break}
    const b=p.position.clone(),dx=tx-b.x,dz=tz-b.z,len=Math.hypot(dx,dz),ux=dx/len,uz=dz/len
    host.step(new Map([[p.id,{moveX:ux,moveZ:uz,yaw:Math.atan2(-ux,-uz)}]]))
    if(!p.fall.grounded)air++
    const step=Math.hypot(p.position.x-b.x,p.position.z-b.z)
    distance+=step;stall=step<.004?stall+1:0;maxStall=Math.max(maxStall,stall);ticks++
   }
   if(!done)break
  }
  return {done,air,ticks,maxStall,distance:round(distance),end:[round(p.position.x),round(p.position.z)]}
 }finally{host.dispose()}
}
const passages=[]
for(const row of rows) {
 const pass=(ox,a,b,models=true)=>run([pAt(row,ox,a),pAt(row,ox,b)],models)
 const crosses=[]
 for(const x of [-2.6,0,2.6])for(const sign of [-1,1]) {
  const r=pass(x,3.0*sign,-3.0*sign)
  assert(r.done&&r.air===0&&r.maxStall===0,JSON.stringify({row,x,sign,r}))
  crosses.push({x,side:sign,ticks:r.ticks})
 }
 const posts=[]
 for(const x of [-4,4]){
  const hit=pass(x,3,-3),control=pass(x,3,-3,false)
  assert(!hit.done&&hit.air===0&&hit.maxStall===24,JSON.stringify({row,x,hit}))
  assert(control.done&&control.air===0)
  posts.push({x,hit,controlTicks:control.ticks})
 }
 passages.push({ordinal:row.ordinal,crosses,posts})
}
const anchor=rows.find(a=>a.ordinal===26)
const approachCandidates=[-0.46,0,.46].map(dx=>[
 [d.entry.x+dx,d.entry.z],[123.75+dx,-214],[123.25+dx,-199.50],
 pAt(anchor,-1.15+dx,-3),pAt(anchor,-1.15+dx,3),pAt(anchor,-1.15+dx,-3),
 [123.25+dx,-199.50],[123.75+dx,-214],[d.entry.x+dx,d.entry.z],
])
const approaches=approachCandidates.map(path=>({path,...run(path)}))
assert(approaches.every(r=>r.done&&r.air===0&&r.maxStall===0),JSON.stringify(approaches))
const output={...d,scope:'Flat movement fixture for 19 unchanged Round 5 screen positions. Each instance has four matching proxy boxes; not installed terrain, flight, encounter or projectile rules.',sim:'Engine 0.1.44',extractionSHA256:createHash('sha256').update(raw).digest('hex'),passages,approaches}
writeFileSync(out,JSON.stringify(output,null,2)+'\n')
console.log(JSON.stringify({instances:rows.length,cleared:passages.flatMap(p=>p.crosses).length,posts:passages.flatMap(p=>p.posts).length,approaches:approaches.map(r=>[r.distance,r.ticks])}))
