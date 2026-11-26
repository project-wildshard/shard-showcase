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
const raw=readFileSync(join(out,'collision.json'))
const parts=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
const structural=g=>g.role!=='bridge'||/\| (Cedar amber|Honey endgrain|Red cedar|Weathered timber(?: color details)?)$/.test(g.name)
const compact=parts.filter(structural)
const triangleCount=rows=>rows.reduce((s,x)=>s+x.triangles.length/3,0)
const bands={west:0,bridge:0,east:0,frame:0,deck:0,bottom:0}
function walk(offset,omitted=null,reverse=false,trace=false,geometry=parts){
  const z=-64+offset, x=reverse?195.6:181.3, dest=reverse?181.3:195.6
  const sign=Math.sign(dest-x)
  const yaw=Math.atan2(-sign,0)
  const host=new SimHost({version:SIM_API_VERSION,id:'e10c-vault-bridge-to-lower-lift',seed:25,
    ground:{size:500,height:-50},player:{at:{x,y:-44.34,z},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'fixture-disabled',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world,roles=new Map()
  try {
    for(const g of geometry){
      if(g.role===omitted)continue
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
      roles.set(c.handle,g.role)
    }
    for(let i=0;i<50;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const frames=[], ticks={...bands}
    let tick=0,air=0,minY=p.position.y,stall=0,longestStall=0
    for(;tick<500&&sign*(dest-p.position.x)>.10&&p.position.y>-47;tick++){
      const prior=p.position.clone()
      host.step(new Map([[p.id,{moveX:sign,moveZ:0,yaw}]]))
      const distance=Math.hypot(p.position.x-prior.x,p.position.z-prior.z)
      stall=distance<.004?stall+1:0
      longestStall=Math.max(longestStall,stall)
      minY=Math.min(minY,p.position.y)
      const ground=p.motor.result.groundCollider
      const role=ground?roles.get(ground.handle):null
      if(!p.fall.grounded)air++
      else if(role)ticks[role]++
      if(trace&&(tick%4===0||stall===30))frames.push({tick,feet:p.position.toArray(),role,grounded:p.fall.grounded})
      if(stall===30)break
    }
    return {offset,reverse,omitted,tick,complete:sign*(dest-p.position.x)<=.1,
      air,longestStall,minY,ticks,end:p.position.toArray(),frames}
  }finally{host.dispose()}
}
const paths=[-.45,-.225,0,.225,.45].flatMap(o=>[walk(o),walk(o,null,true)])
const reduced=[-.45,-.225,0,.225,.45].flatMap(o=>[
  walk(o,null,false,false,compact),walk(o,null,true,false,compact)])
const center=walk(0,null,false,true), control=walk(0,'bridge',false,true)
assert.deepEqual(center,walk(0,null,false,true))
assert([...paths,...reduced].every(r=>r.complete&&r.air===0&&r.longestStall===0&&r.ticks.bridge>90&&r.ticks.deck>30))
const proof=paths.map((p,i)=>({
  totalTicks:reduced[i].tick-p.tick,
  endpointDelta:Math.hypot(...reduced[i].end.map((v,k)=>v-p.end[k])),
  sagDelta:reduced[i].minY-p.minY,
}))
assert(proof.every(r=>r.totalTicks===0&&r.endpointDelta<.012&&Math.abs(r.sagDelta)<.0001))
const centerCompact=walk(0,null,false,true,compact)
assert.deepEqual(centerCompact,walk(0,null,false,true,compact))
const summary={scope:'Static exact Room 3 bridge geometry and lower lift boarding only. No rope dynamics, motion, ladder, scramble, door or phone.',
  engine:'0.1.44',collisionHash:hash,colliders:parts.length,triangles:triangleCount(parts),
  compact:{colliders:compact.length,triangles:triangleCount(compact),proof,paths:reduced},paths,center,centerCompact,control}
writeFileSync(join(out,'walk.json'),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify({paths,control:{...control,frames:[]}}))
assert(!control.complete&&control.air>0&&control.minY< -47)
