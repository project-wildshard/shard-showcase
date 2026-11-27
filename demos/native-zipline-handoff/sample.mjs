import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
const root=dirname(packagePath)
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const dir=resolve(process.argv[2]), digest=raw=>createHash('sha256').update(raw).digest('hex')
const meshRaw=readFileSync(join(dir,'terminal-mesh.json'))
const geo=JSON.parse(meshRaw)
assert.equal(digest(meshRaw),'a8b955c7f7baa9e95c2b8bcdfdb0e3b7b6a6d5f1b3a3847500b338f46130be55')
const ride=JSON.parse(readFileSync(join(dir,'ride.json')))
assert.equal(ride.engine,'0.1.44')
const variant=process.argv[3] ?? 'baseline'
const expected={baseline:[562,9.8,22],short:[282,48,26],capped:[302,64,22]}[variant]
assert(expected, 'Choose baseline, short or capped')
assert.deepEqual([ride.final.tick,ride.row.gravity,ride.row.maxSpeed],expected)
assert.equal(ride.row.drag,.012)
const start=new Vector3(...ride.frames.at(-2).rider), end=new Vector3(...ride.final.rider)
const axis=end.clone().sub(start).setY(0).normalize(), side=new Vector3(-axis.z,0,axis.x)
const approachTicks=8, groundTicks=12, dt=1/60
const eps=.04,maxRequestedStep=.18

function trial(lateral,vertical,blocked=false){
  const origin=start.clone().addScaledVector(side,lateral);origin.y+=vertical
  const host=new SimHost({version:SIM_API_VERSION,id:'w7b-handoff',seed:1,ground:{size:500,height:.1},
    player:{at:{x:origin.x,y:origin.y,z:origin.z},speed:4.3},entities:[],quests:[],
    weapon:{id:'bench-disabled',damage:0}},{rapier:R,ground:false})
  const player=host.players.get('actor.player'), world=host.physics.world, names=new Map()
  const goal=end.clone().addScaledVector(side,lateral)
  let wall
  try{
    for(const g of geo){
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
      names.set(c.handle,g.name)
    }
    if(blocked){
      const p=origin.clone().lerp(goal,.58)
      wall=world.createCollider(R.ColliderDesc.cuboid(.08,1,1)
        .setTranslation(p.x,p.y+.5,p.z).setCollisionGroups(groups('WORLD')))
      names.set(wall.handle,'Control | closed transit shutter')
    }
    world.step()
    assert(player.hasMotor&&player.motor.opts.radius===.38)
    assert(player.position.distanceTo(origin)<1e-8)
    const frames=[]
    const move=(delta,stage)=>{
      const before=player.position.clone()
      const r=player.motor.move(player.position,delta)
      const g=r.groundCollider===null?null:names.get(r.groundCollider.handle)
      frames.push({stage,feet:player.position.toArray(),ground:g??null,grounded:r.grounded,move:player.position.distanceTo(before),requested:delta.length()})
      world.step()
    }
    for(let n=1;n<=approachTicks;n++){
      const target=origin.clone().lerp(goal,n/approachTicks)
      move(target.sub(player.position).clampLength(0,maxRequestedStep),'handoff')
    }
    const arrival=player.position.distanceTo(goal)
    if(arrival<=eps)for(let n=0;n<groundTicks;n++)move(new Vector3(0,-1.6*dt,0),'settle')
    const last=frames.at(-1)
    return {lateral,vertical,blocked,arrival,capsule:{radius:player.motor.opts.radius,height:player.motor.opts.height},pass:arrival<=eps&&last.grounded&&last.ground?.startsWith('PROP-035'),
      maxStep:Math.max(...frames.map(f=>f.move)),last,frames}
  }finally{host.dispose()}
}
const center=trial(0,0), closed=trial(0,0,true)
const trials=[]
for(const x of [-.10,-.05,0,.05,.10])for(const y of [-.025,0,.025])trials.push(trial(x,y))
const summary=r=>({...r,frames:undefined})
console.log(JSON.stringify({center:summary(center),closed:summary(closed),cases:trials.map(summary)}))
assert(center.pass&&trials.every(t=>t.pass))
assert(!closed.pass&&closed.arrival>.70)
assert(closed.frames.every(x=>x.requested<=maxRequestedStep+1e-9))
assert.deepEqual(center,trial(0,0))
assert(trials.every(t=>t.maxStep<.20))
assert(trials.every(t=>t.frames.slice(-5).every(f=>f.grounded&&f.ground.startsWith('PROP-035'))))
writeFileSync(join(dir,'handoff.json'),JSON.stringify({
  scope:'Release-only bench: native motor on W08 art triangles. No native carry owner, trigger or course install.',
  engine:'0.1.44', meshSha:digest(meshRaw),meshNames:geo.map(g=>g.name),
  meshTriangles:geo.reduce((n,g)=>n+g.triangles.length/3,0),
  frequencyHz:60,maxRequestedStep,approachTicks,groundTicks,stockDismountStep:start.distanceTo(end),start:start.toArray(),goal:end.toArray(),
  center,closed,cases:trials.map(summary),
})+'\n')
