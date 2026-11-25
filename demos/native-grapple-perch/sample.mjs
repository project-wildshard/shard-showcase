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
const formatPath=req.resolve('@wildshard/format/grapple')
assert.equal(JSON.parse(readFileSync(join(dirname(formatPath),'../../package.json'))).version,'0.43.0')
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
const {parseGrappleProfile}=await import(pathToFileURL(formatPath).href)
const {DEFAULT_GRAPPLE_MODE,hookVisible,landingFor}=await at('src/shared/game/grapple/sim.ts')
const {installGrapple}=await at('src/server/game/grapple/native.ts')
const {floorBelow}=await at('src/shared/engine/physics/query.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
assert(process.argv[2]&&process.argv[3],'Usage: sample.mjs extracted.json outcome.json')
const raw=readFileSync(process.argv[2])
const geometry=JSON.parse(raw)
const visualRaw=readFileSync(join(dirname(process.argv[2]),'perch-dressing.json'))
const dressing=JSON.parse(visualRaw)
const dressingSha=createHash('sha256').update(visualRaw).digest('hex')
const meshSha=createHash('sha256').update(raw).digest('hex')
assert.equal(meshSha,'e9a02843524cd6e65fc275bcb8aecc975a427c1a5586cade6df85c94c0c7e014')
const hook=new Vector3(-150,12,-44)
const start=[-142,-22]
const cues=Object.fromEntries(['fire','bite','zip','reel','dock'].map(x=>[x,x]))
const looks=Object.fromEntries(['muzzle','bite','dock','sparks','ribbon'].map(x=>[x,x]))
const profile=parseGrappleProfile({id:'w7a-perch-bench',course:{name:'West opening hop'},cues,looks,
  headless:{step:'w7a-step',lock:'w7a-lock',aim:'w7a-aim',eye:1.7,aspect:402/874,portraitFov:80}})
function simulate([x,z],deck,{keepFrames=false,named=true}={}) {
  const host=new SimHost({version:SIM_API_VERSION,id:'w7a-perch-bench',seed:25,ground:{size:500,height:.1},
    player:{at:{x,y:.07,z},yaw:Math.atan2(x-hook.x,z-hook.z),speed:4.3},entities:[],quests:[],
    weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player')
  const world=host.physics.world
  try {
    for(const g of geometry)world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
    const perch=deck&&world.createCollider(R.ColliderDesc.cuboid(deck.width/2,.12,deck.length/2)
      .setTranslation(deck.x,deck.y-.12,deck.z).setCollisionGroups(groups('WORLD')))
    if(deck) for(const g of dressing)world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
    const claw=installGrapple(host,{commands:()=>[],emit:()=>{}},profile,DEFAULT_GRAPPLE_MODE,[hook],[])
    for(let i=0;i<30;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const feet=p.position.clone(), eye=feet.clone().add(new Vector3(0,profile.headless.eye,0))
    const ports={physics:host.physics,body:{position:feet,motor:p.motor}}
    const visible=hookVisible(ports,claw.sim.course,eye,hook)
    const inRange=eye.distanceTo(hook)<DEFAULT_GRAPPLE_MODE.maxRange
    const landing=new Vector3(), side=landingFor(ports,feet,hook,landing)
    const pitch=Math.atan2(hook.y-eye.y,Math.hypot(hook.x-eye.x,hook.z-eye.z))
    claw.press(p.id,{lock:true,...(named?{hook:0}:{}),pitch});host.step()
    const target=claw.sim.target?.approach.toArray()??null
    const locked=target!==null
    assert.equal(locked,visible&&inRange&&side!==0)
    if(locked)claw.press(p.id,{fire:true,pitch})
    let result={visible,inRange,reach:eye.distanceTo(hook),side,locked,landing:locked?landing.toArray():null,
      target,start:feet.toArray(),ymax:feet.y,settled:false,phases:[],frames:[]}
    let groundRun=0
    for(let i=0;locked&&i<220;i++){
      host.step()
      result.ymax=Math.max(result.ymax,p.position.y)
      const phase=claw.sim.phase
      if(phase!==result.phases.at(-1))result.phases.push(phase)
      if(keepFrames)result.frames.push([i,p.position.toArray(),phase,p.fall.grounded])
      if(phase==='idle'&&p.fall.grounded&&perch&&p.motor.result.groundCollider?.handle===perch.handle){
        result.ticks??=i+1
        groundRun++
      }else groundRun=0
      if(groundRun>=12&&Math.abs(p.position.y-deck.y)<.04){
        result.settleTicks=i+1
        result.end=p.position.toArray()
        result.settled=!!perch&&Math.abs(p.position.y-deck.y)<.04&&
          p.motor.result.groundCollider?.handle===perch.handle
        break
      }
    }
    result.floorAtEnd=floorBelow(host.physics,p.position.x,p.position.z,p.position.y+.1,1,p.motor.collider)
    return result
  }finally{host.dispose()}
}
const base=simulate(start)
assert(base.visible&&base.inRange&&!base.locked&&base.side===0)
const deck={x:-151,y:4.4,z:-46.62,width:3.4,length:2.24}
const centre=simulate(start,deck,{keepFrames:true})
assert.deepEqual(centre,simulate(start,deck,{keepFrames:true}))
const camera=simulate(start,deck,{keepFrames:true,named:false})
assert.deepEqual(camera,centre)
assert(centre.settled&&centre.side===2)
assert.deepEqual(centre.phases,['fire','bite','zip','vault','settle','idle'])
const perturbations=[]
for(const dx of [-1,-.5,0,.5,1])for(const dz of [-1,-.5,0,.5,1]){
  const r=simulate([start[0]+dx,start[1]+dz],deck)
  assert(r.settled&&r.side===2&&r.ticks<150,JSON.stringify({dx,dz,...r}))
  const edge=Math.min(deck.width/2-Math.abs(r.end[0]-deck.x),deck.length/2-Math.abs(r.end[2]-deck.z))-.38
  assert(edge>.10,JSON.stringify({dx,dz,edge,end:r.end}))
  perturbations.push({offset:[dx,dz],ticks:r.ticks,end:r.end,bodyMargin:edge})
}
const {frames,...core}=centre
console.log(JSON.stringify({base,centre:core,firstAndLast:perturbations.filter((_,i)=>i===0||i===24)}))
writeFileSync(process.argv[3],JSON.stringify({meshSha,dressingSha,gravityContact:'SimHost.motor',
  engine:'0.1.44',format:'0.43.0',clockHz:60,hook:hook.toArray(),
  startPadThreeXZ:start,eyeHeight:profile.headless.eye,cameraAspect:profile.headless.aspect,
  defaultMaxRange:DEFAULT_GRAPPLE_MODE.maxRange,base,deck,centre:core,frames,perturbations})+'\n')
