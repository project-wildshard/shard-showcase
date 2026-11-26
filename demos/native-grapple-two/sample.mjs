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
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const dir=resolve(process.argv[2]??'/tmp/w7a-two')
const output=process.argv[3]??join(dir,'native.json')
const digest=raw=>createHash('sha256').update(raw).digest('hex')
const read=(file)=>{const raw=readFileSync(join(dir,file));return {value:JSON.parse(raw),sha:digest(raw)}}
const corridor=read('corridor.json')
const oneDress=read('perch-dressing.json')
assert.equal(oneDress.sha,'18c875d3ed3ab629202d52dd07f72363176560173f39a8b1371a3d4f479f2ac6')
const hooks=[new Vector3(-150,12,-44),new Vector3(-170,16,-68)]
const first={x:-151,y:4.4,z:-46.62,w:3.4,d:2.24,h:.24}
const start=[-142,-22]
const s2=process.env.WSC_GRAPPLE_CANDIDATE
const second=s2 ? JSON.parse(s2) : {x:-172,y:8.2,z:-70.2,w:3.4,d:2.6,h:.24}
const dress=s2? null : read('pole-two-dressing.json')
const cues=Object.fromEntries(['fire','bite','zip','reel','dock'].map(x=>[x,x]))
const looks=Object.fromEntries(['muzzle','bite','dock','sparks','ribbon'].map(x=>[x,x]))
const profile=parseGrappleProfile({id:'w7a-two',course:{name:'West opening poles'},cues,looks,
  headless:{step:'w7a-step',lock:'w7a-lock',aim:'w7a-aim',eye:1.7,aspect:402/874,portraitFov:80}})

function simulate(dx,dz,{installed=true,keepFrames=false,named=false}={}) {
  const [x,z]=[start[0]+dx,start[1]+dz]
  const host=new SimHost({version:SIM_API_VERSION,id:'w7a-two',seed:25,ground:{size:500,height:.1},
    player:{at:{x,y:.07,z},yaw:Math.atan2(x-hooks[0].x,z-hooks[0].z),speed:4.3},entities:[],quests:[],
    weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world
  const mesh=g=>world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
  const box=d=>world.createCollider(R.ColliderDesc.cuboid(d.w/2,d.h/2,d.d/2)
    .setTranslation(d.x,d.y-d.h/2,d.z).setCollisionGroups(groups('WORLD')))
  try {
    for(const g of [...corridor.value,...oneDress.value])mesh(g)
    const colliders=[box(first),installed?box(second):null]
    if(installed&&dress)for(const g of dress.value)mesh(g)
    const claw=installGrapple(host,{commands:()=>[],emit:()=>{}},profile,DEFAULT_GRAPPLE_MODE,hooks,[])
    for(let i=0;i<30;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const hops=[]
    for(const [i,hook] of hooks.entries()){
      const feet=p.position.clone(),eye=feet.clone().add(new Vector3(0,profile.headless.eye,0))
      const ports={physics:host.physics,body:{position:feet,motor:p.motor}}
      const visible=hookVisible(ports,claw.sim.course,eye,hook)
      const reach=eye.distanceTo(hook)
      const landing=new Vector3(),side=landingFor(ports,feet,hook,landing)
      const pitch=Math.atan2(hook.y-eye.y,Math.hypot(hook.x-eye.x,hook.z-eye.z))
      // Headless look input. No position, velocity, or motor state reset between hops.
      p.yaw=Math.atan2(feet.x-hook.x,feet.z-hook.z)
      claw.press(p.id,{lock:true,...(named?{hook:i}:{}),pitch});host.step()
      const selected=claw.sim.target?.hook
      const r={start:feet.toArray(),reach,visible,side,locked:selected?.equals(hook)??false,
        landing:side?landing.toArray():null,approach:claw.sim.target?.approach.toArray()??null,
        settled:false,phases:[],frames:[]}
      hops.push(r)
      if(!r.locked)break
      claw.press(p.id,{fire:true,pitch})
      let onDeck=0
      for(let n=1;n<=250;n++){
        host.step()
        const phase=claw.sim.phase
        if(phase!==r.phases.at(-1))r.phases.push(phase)
        if(keepFrames)r.frames.push([n,p.position.toArray(),phase,p.fall.grounded])
        if(phase==='idle'&&p.fall.grounded&&colliders[i]&&p.motor.result.groundCollider?.handle===colliders[i].handle){
          r.ticks??=n
          onDeck++
        }else onDeck=0
        if(onDeck>=12){
          r.settled=true;r.end=p.position.toArray();r.settleTicks=n
          const d=i?second:first
          r.bodyMargin=Math.min(d.w/2-Math.abs(p.position.x-d.x),d.d/2-Math.abs(p.position.z-d.z))-.38
          break
        }
      }
      if(!r.settled)break
    }
    return hops
  }finally{host.dispose()}
}
const centre=simulate(0,0,{keepFrames:true})
const noSecond=simulate(0,0,{installed:false})
if(s2){console.log(JSON.stringify({second,centre:centre.map(({frames,...r})=>r),noSecond}));process.exit(0)}
assert.equal(corridor.sha,'60098a20322fb4dbc908ce9e22c53a5966e7f400a0275b5f829eb25af0deb2a6')
assert.equal(centre.length,2)
assert(centre.every(r=>r.settled&&r.bodyMargin>.09))
assert.deepEqual(centre,simulate(0,0,{keepFrames:true,named:true}))
assert.deepEqual(centre,simulate(0,0,{keepFrames:true}))
assert(noSecond[0].settled&&noSecond.length===2&&noSecond[1].visible&&noSecond[1].reach<38&&!noSecond[1].locked)
const cases=[]
for(const dx of [-1,-.5,0,.5,1])for(const dz of [-1,-.5,0,.5,1]){
  const hops=simulate(dx,dz)
  assert(hops.length===2&&hops.every(r=>r.settled&&r.bodyMargin>.09),JSON.stringify({dx,dz,hops}))
  cases.push({offset:[dx,dz],hops:hops.map(({frames,...r})=>r)})
}
const proof={scope:'Two consecutive native server hops in the W08 corridor. No course install, timer, or phone playtest.',
  engine:'0.1.44',format:'0.43.0',frequencyHz:60,meshSha:corridor.sha,
  meshObjects:corridor.value.length,meshTriangles:corridor.value.reduce((n,g)=>n+g.triangles.length/3,0),
  firstDressingSha:oneDress.sha,secondDressingSha:dress.sha,hooks:hooks.map(h=>h.toArray()),first,second,centre,noSecond,cases}
writeFileSync(output,JSON.stringify(proof)+'\n')
console.log(JSON.stringify({centre:centre.map(({frames,...r})=>r),cases:cases.length,mesh:proof.meshSha}))
