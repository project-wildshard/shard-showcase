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
const out=resolve(process.argv[2])
const raw=readFileSync(join(out,'handoff-collision.json'))
const parts=JSON.parse(raw)
const layout=JSON.parse(readFileSync(join(out,'handoff-layout.json')))
const collision_sha256=createHash('sha256').update(raw).digest('hex')
const rounded=v=>v.map(x=>+x.toFixed(5))

function walk(offset,mode='open',reverse=false,record=false){
  const center=207.5+offset,z=-64+offset
  const landing=[202.65,z],bend=[center,z],room=[center,-50.25]
  const path=reverse?[room,bend,landing]:[landing,bend,room]
  const [[x,startZ],...points]=path
  const host=new SimHost({version:SIM_API_VERSION,id:'e10c-e10d-vault-handoff',seed:25,
    ground:{size:500,height:-50},player:{at:{x,y:-40.45,z:startZ},speed:4.3},
    entities:[],quests:[],weapon:{id:'fixture-disabled',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),w=host.physics.world,roles=new Map()
  try{
    for(const part of parts){
      const k=part.role
      if((mode!=='sealed'&&k==='sealed-control')||(mode==='sealed'&&k==='open-final')||
         (mode==='no-throat'&&k==='throat-deck'))continue
      const g=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(part.vertices),
        new Uint32Array(part.triangles)).setCollisionGroups(groups('WORLD')))
      roles.set(g.handle,k)
    }
    for(let n=0;n<50;n++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded,JSON.stringify({mode,reverse,offset,at:p.position.toArray()}))
    const trace=[],support={}
    let n=0,idx=0,air=0,stall=0,maxStall=0,minY=p.position.y
    while(n<360&&p.position.y>-42&&idx<points.length){
      const before=p.position.clone(),[tx,tz]=points[idx]
      const dx=tx-before.x,dz=tz-before.z,d=Math.hypot(dx,dz)
      if(d<.10){idx++;continue}
      const ax=dx/d,az=dz/d,yaw=Math.atan2(-ax,-az)
      host.step(new Map([[p.id,{moveX:ax,moveZ:az,yaw}]]))
      const k=roles.get(p.motor.result.groundCollider?.handle)
      if(!p.fall.grounded)air++
      else if(k)support[k]=(support[k]??0)+1
      stall=p.position.distanceTo(before)<.004?stall+1:0
      maxStall=Math.max(stall,maxStall);minY=Math.min(minY,p.position.y);n++
      if(record&&(n%2===0||n===1))trace.push(rounded(p.position.toArray()))
      if(stall>=24)break
    }
    return {offset,mode,reverse,complete:idx===points.length,ticks:n,air,maxStall,minY:+minY.toFixed(5),
      end:rounded(p.position.toArray()),support,...(record?{trace}:{})}
  }finally{host.dispose()}
}
const offsets=[-.48,-.24,0,.24,.48]
const open=offsets.flatMap(o=>[walk(o),walk(o,'open',true)])
const closed=offsets.map(o=>walk(o,'sealed'))
const noThroat=offsets.map(o=>walk(o,'no-throat'))
const {trace}=walk(0,'open',false,true)
assert.deepEqual(trace,walk(0,'open',false,true).trace)
const receipt={scope:'Proposed WSC-KIT-008 Room 3/4 turn, existing Room 3 landing + Room 4 floor and two reused open bulkheads. No dynamic door, hazard, spawn, install or phone claims.',
  layout,engine:'0.1.44',collision_sha256,meshes:parts.length,triangles:parts.reduce((s,p)=>s+p.triangles.length/3,0),
  open,closed,noThroat,trace}
writeFileSync(join(out,'handoff-walk.json'),JSON.stringify(receipt,null,2)+'\n')
assert(open.every(r=>r.complete&&r.air===0&&r.maxStall===0&&r.support['throat-deck']>65&&r.support['room4-floor']>55),JSON.stringify(open))
assert(closed.every(r=>!r.complete&&r.air===0&&r.end[0]<203.5),JSON.stringify(closed))
assert(noThroat.every(r=>!r.complete&&r.air>0&&r.minY < -41.7),JSON.stringify(noThroat))
console.log('10 grounded round-trip legs; 5 sealed stops and 5 absent-throat falls.')
