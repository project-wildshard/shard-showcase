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
const raw=readFileSync(join(out,'room2-collision.json'))
const parts=JSON.parse(raw)
const collisionSHA=createHash('sha256').update(raw).digest('hex')

function walk(offset,mode='open',reverse=false,record=false){
  const z=-64+offset, x=reverse?173.3:164.6, dest=reverse?164.6:173.3
  const sign=Math.sign(dest-x), yaw=Math.atan2(-sign,0)
  const host=new SimHost({version:SIM_API_VERSION,id:'e10c-room2-to-room3',seed:25,
    ground:{size:500,height:-50},player:{at:{x,y:-48.92,z},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'fixture-disabled',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world,roles=new Map()
  try {
    for(const g of parts){
      if((mode==='sealed'&&g.role==='open')||(mode!=='sealed'&&g.role==='sealed')||
         (mode==='no-threshold'&&g.role==='threshold'))continue
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
      roles.set(c.handle,g.role)
    }
    for(let i=0;i<50;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const trace=[], groundedTicksByRole={}
    let tick=0,air=0,minY=p.position.y,stall=0,longestStall=0
    for(;tick<300&&sign*(dest-p.position.x)>.10&&p.position.y>-50.2;tick++){
      const prior=p.position.clone()
      host.step(new Map([[p.id,{moveX:sign,moveZ:0,yaw}]]))
      const distance=Math.hypot(p.position.x-prior.x,p.position.z-prior.z)
      stall=distance<.004?stall+1:0
      longestStall=Math.max(longestStall,stall)
      minY=Math.min(minY,p.position.y)
      const ground=p.motor.result.groundCollider,role=ground&&roles.get(ground.handle)
      if(!p.fall.grounded)air++
      else if(role)groundedTicksByRole[role]=(groundedTicksByRole[role]??0)+1
      if(record&&tick%3===0)trace.push(p.position.toArray().map(v=>+v.toFixed(4)))
      if(stall===24)break
    }
    return {offset,mode,reverse,ticks:tick,complete:sign*(dest-p.position.x)<=.1,
      air,longestStall,minY,groundedTicksByRole,end:p.position.toArray(),...(record?{trace}:{})}
  }finally{host.dispose()}
}

const offsets=[-.45,-.225,0,.225,.45]
const open=offsets.flatMap(o=>[walk(o),walk(o,'open',true)])
const sealed=offsets.map(o=>walk(o,'sealed'))
const omitted=offsets.map(o=>walk(o,'no-threshold'))
const reviewPaths=[walk(0,'open',false,true),walk(-.45,'sealed',false,true)]
assert.deepEqual(reviewPaths[0],walk(0,'open',false,true))
const receipt={scope:'Headless, straight crossing of existing E10c Room 2 floor, threshold and Room 3 tread; sealed donor is a static control. No state machine, Room 1 connection, full field, phone or install.',
  engine:'0.1.44',collisionSHA,geometry:parts.map(({role,triangles})=>({role,triangles:triangles.length/3})),
  open,sealed,omitted,review_paths:reviewPaths}
writeFileSync(join(out,'room2-walk.json'),JSON.stringify(receipt,null,2)+'\n')
assert(open.every(r=>r.complete&&r.air===0&&r.longestStall===0&&r.groundedTicksByRole.threshold>17),JSON.stringify(open))
assert(sealed.every(r=>!r.complete&&r.air===0&&r.longestStall===24&&r.end[0]<167.95),JSON.stringify(sealed))
assert(omitted.every(r=>!r.complete&&r.air>0&&r.minY< -50),JSON.stringify(omitted))
console.log('All ten open crossings, five sealed and five missing-threshold controls passed.')
