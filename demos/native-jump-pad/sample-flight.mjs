import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(packagePath,'utf8')).version,'0.1.44')
const root=dirname(packagePath)
const formatPath=req.resolve('@wildshard/format/modes')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const {safeParse}=await import('valibot')
const {TraverseModeSchema}=await import(pathToFileURL(formatPath).href)
const format=JSON.parse(readFileSync(join(dirname(formatPath),'../../package.json'),'utf8')).version
assert.equal(format,'0.43.0')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
assert(process.argv[2],'Output path required')
const target={x:-121,y:6,z:-103,halfWidth:2,halfDepth:4}
const top=.431
const pads=[-104,-110,-116]
const radius=1.25956
const yaw=Math.PI/2
function simulate(x,sx,sy,keepFrames=false, consume=false){
  const host=new SimHost({version:SIM_API_VERSION,id:'w6b-pad-bench',seed:25,
    ground:{size:360,height:.1},player:{at:{x,y:top+.05,z:target.z},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player')
  assert(p.hasMotor&&p.motor.opts.radius===.38)
  const box=(x,y,z,hw,hh,hd)=>host.physics.world.createCollider(
    R.ColliderDesc.cuboid(hw,hh,hd).setTranslation(x,y,z).setCollisionGroups(groups('WORLD')))
  box(-111,-1,target.z,50,1.1,24)
  const pad=pads.map(x=>host.physics.world.createCollider(
    R.ColliderDesc.cylinder((top-.12)/2,radius).setTranslation(x,(top+.12)/2,target.z).setCollisionGroups(groups('WORLD'))))[pads.indexOf(x)]
  const ledge=box(target.x,5.75,target.z,target.halfWidth,.25,target.halfDepth)
  const sample=k=>({tick:k,feet:p.position.toArray(),ground:p.fall.grounded,activeGround:p.motor.result.groundCollider?.handle===ledge.handle?'ledge':null})
  try{
    for(let i=0;i<20;i++)host.step()
    // Idle does not refresh the contact probe. A deliberate tiny lean gets a
    // measured pad contact without giving the flight horizontal input.
    host.step(new Map([[p.id,{moveX:0,moveZ:.001,yaw}]]))
    assert(p.fall.grounded && Math.abs(p.position.y-top)<.035 && p.motor.result.groundCollider?.handle===pad.handle)
    const start=sample(0)
    p.addImpulse(new Vector3(-sx,sy,0))
    let touched,apex=0
    const frames=[start]
    for(let k=1;k<=180;k++){
      host.step()
      const s=sample(k)
      apex=Math.max(s.feet[1],apex)
      if(keepFrames)frames.push(s)
      if(p.fall.grounded){
        touched=s
        break
      }
    }
    const first=touched
    let settle, reair=0
    if(first?.activeGround==='ledge'){
      if(consume)p.impulse.set(0,0,0)
      for(let i=1;i<=72;i++){
        host.step()
        if(!p.fall.grounded)reair++
        if(keepFrames)frames.push(sample(first.tick+i))
      }
      settle=sample(first.tick+72)
    }
    return {start, first, settle, apex, reair, frames}
  }finally{host.dispose()}
}
const preview=process.argv[3]==='--explore'
if(preview){
  for(const x of pads)for(const y of [36,38,40,42,44,46,48]){
    const v=-(target.x-x)*3.38
    const q=simulate(x,v,y)
    console.log(x,v,y,q.apex.toFixed(4),JSON.stringify(q.first),JSON.stringify(q.settle))
  }
}else {
  const result=[]
  for(const [x,sx,sy] of [[-104,61,40],[-110,39,40],[-116,16,40]]){
    const A=simulate(x,sx,sy,true),B=simulate(x,sx,sy,true)
    assert.deepEqual(A,B)
    assert(A.first?.activeGround==='ledge'&&A.settle?.activeGround==='ledge')
    assert(A.first.tick>10&&A.first.tick<160)
    for(const v of [A.first,A.settle]){
      assert(Math.abs(v.feet[0]-target.x)<target.halfWidth-.38)
      assert(Math.abs(v.feet[1]-target.y)<.100)
    }
    const candidate=simulate(x,sx,sy,true,true)
    assert.deepEqual(candidate.first,A.first)
    assert.equal(A.reair,27,'Watch for a change in raw impulse after ledge contact')
    assert.equal(candidate.reair,0)
    assert.equal(candidate.settle?.activeGround,'ledge')
    result.push({padX:x,impulse:[-sx,sy,0],contactConsumed:{reair:candidate.reair,settle:candidate.settle},...A})
  }
  const launch=safeParse(TraverseModeSchema,{kind:'launch',id:'demo',box:{},velocity:[0,1,0],cooldown:1})
  assert(!launch.success && launch.issues.some(i=>i.path?.[0]?.key==='kind'))
  writeFileSync(process.argv[2],JSON.stringify({engine:'0.1.44',format,clockHz:60,padTop:top,target,staticFixture:true,results:result})+'\n')
  for(const r of result){const {frames,...q}=r;console.log(q)}
}
