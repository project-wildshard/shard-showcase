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
const {floorBelow}=await at('src/shared/engine/physics/query.ts')
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
const summit=process.argv.includes('--summit')
const mast=summit||process.argv.includes('--mast')
const summitHook=[-211.4,46.4,-38.9], oldSummitHook=[-214.5,45.8,-34], launchPoint=[-212,45,-34]
const summitGeo=summit?read('summit.json'):null, summitRing=summit?read('summit-bracket.json'):null
if(summit)assert.equal(summitGeo.sha,'deced7e029e6c628db29a43bbb8e300139c9390a6c1c415b162a5349e8a3183b')
if(summit)assert.equal(summitRing.sha,'3d47fdf79dfe6cce585339bc85c4fede2f33405a8aba514f034c120723415aae')
const tank=mast||process.argv.includes('--tank')
const mastHook=[-200,28,-68]
const mastGeo=mast?read('mast.json'):null, receiver=mast?read('mast-receiver-dressing.json'):null
const deckFour=mast?read('mast-receiver-export.json').value.deck:null
if(mast){
  assert.equal(mastGeo.sha,'1b55eadb19d0a8829c8dd747fb14bcc31e1d04a5e615cf6cede4c9eedf1378b4')
  assert.equal(receiver.sha,'fbc84a42b30c3445dca6f038a669dd399819498d716b0972e7e21837cb37cad7')
  assert.deepEqual(deckFour,{x:-202.6,z:-63.55,y:25.6,w:3.4,d:2.8,h:.22})
}
const rim=[-193.2,21.35,-91.2], roofCentre=[-206,18,-104]
const extra=tank?read('tank.json'):null, saddle=tank?read('saddle.json'):null
if(tank)assert.equal(extra.sha,'682a9dfdc85cb5ec2f95149da9c76b2d7a935a5af72e9f603d29f3c079d5fec5')
if(tank)assert.equal(saddle.sha,'6be1f97256325705847b65b1ed3f28d5187c60699fa4a446ca63a9965e16be65')
const hooks=[new Vector3(-150,12,-44),new Vector3(-170,16,-68)]
const first={x:-151,y:4.4,z:-46.62,w:3.4,d:2.24,h:.24}
const start=[-142,-22]
const s2=process.env.WSC_GRAPPLE_CANDIDATE
assert(!(tank&&s2),'The tank proof uses the exact second tower, not a candidate.')
const second=s2 ? JSON.parse(s2) : {x:-172,y:8.2,z:-70.2,w:3.4,d:2.6,h:.24}
const dress=s2? null : read('pole-two-dressing.json')
const cues=Object.fromEntries(['fire','bite','zip','reel','dock'].map(x=>[x,x]))
const looks=Object.fromEntries(['muzzle','bite','dock','sparks','ribbon'].map(x=>[x,x]))
const profile=parseGrappleProfile({id:'w7a-two',course:{name:'West opening poles'},cues,looks,
  headless:{step:'w7a-step',lock:'w7a-lock',aim:'w7a-aim',eye:1.7,aspect:402/874,portraitFov:80}})

function simulate(dx,dz,{installed=true,keepFrames=false,named=false,roofHook=rim,bracket=true,installedMast=true,crossRoof=true,summitTarget=summitHook,summitBracket=true}={}) {
  const route=tank?[...hooks,new Vector3(...roofHook)]:hooks
  if(mast)route.push(new Vector3(...mastHook))
  if(summit)route.push(new Vector3(...summitTarget))
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
    if(tank) {
      for(const g of extra.value){
        const c=mesh(g)
        if(g.name==='JUNCTION | continuous landable roof')colliders[2]=c
      }
      assert(colliders[2])
      if(bracket)for(const g of saddle.value)mesh(g)
      if(mast){
        for(const g of mastGeo.value)mesh(g)
        if(summit){
          for(const g of summitGeo.value){
            const c=mesh(g)
            if(g.name.endsWith('Textured gray deck panels'))colliders[4]=c
          }
          assert(colliders[4])
          if(summitBracket)for(const g of summitRing.value)mesh(g)
        }
        if(installedMast){
          colliders[3]=box(deckFour)
          for(const g of receiver.value)mesh(g)
        }
      }
    }
    if(installed&&dress)for(const g of dress.value)mesh(g)
    const claw=installGrapple(host,{commands:()=>[],emit:()=>{}},profile,DEFAULT_GRAPPLE_MODE,route,[])
    for(let i=0;i<30;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const hops=[]
    for(const [i,hook] of route.entries()){
      let roofWalk
      if(i===3&&crossRoof){
        const x=-197.12,z=-93.35,begin=p.position.clone()
        let walkTicks=0,airTicks=0
        const frames=[]
        for(;walkTicks<120;walkTicks++){
          const dx=x-p.position.x,dz=z-p.position.z,left=Math.hypot(dx,dz)
          if(left<.085)break
          const magnitude=Math.min(1,left*60/4.3)
          host.step(new Map([[p.id,{moveX:magnitude*dx/left,moveZ:magnitude*dz/left,yaw:Math.atan2(-dx,-dz)}]]))
          if(!p.fall.grounded)airTicks++
          if(keepFrames)frames.push(p.position.toArray())
        }
        assert(walkTicks<120&&airTicks===0&&Math.abs(p.position.y-begin.y)<.03)
        roofWalk={target:[x,z],start:begin.toArray(),end:p.position.toArray(),walkTicks,airTicks,distance:begin.distanceTo(p.position),frames}
      }
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
      if(roofWalk)r.roofWalk=roofWalk
      hops.push(r)
      if(!r.locked)break
      claw.press(p.id,{fire:true,pitch})
      let onDeck=0
      for(let n=1;n<=250;n++){
        host.step()
        const phase=claw.sim.phase
        if(phase!==r.phases.at(-1))r.phases.push(phase)
        if(keepFrames)r.frames.push([n,p.position.toArray(),phase,p.fall.grounded])
        if(phase==='idle'&&p.fall.grounded&&(i!==4||p.position.y>44.85)&&colliders[i]&&p.motor.result.groundCollider?.handle===colliders[i].handle){
          r.ticks??=n
          onDeck++
        }else onDeck=0
        if(onDeck>=12){
          r.settled=true;r.end=p.position.toArray();r.settleTicks=n
          if(i===4){
            const {x,y,z}=p.position
            const radius=.58
            for(let ray=0;ray<16;ray++){
              const angle=ray*Math.PI/8
              const f=floorBelow(host.physics,x+Math.cos(angle)*radius,z+Math.sin(angle)*radius,y+.16,.27,
                p.motor.collider,c=>c.handle===colliders[4].handle)
              assert(f!==undefined&&Math.abs(f-45.05)<.012,JSON.stringify({x,y,z,ray,f}))
            }
            r.supportProbeRadius=radius
          }else if(i===2){
            // Conservative inscribed 96-gon radius, then capsule radius.
            r.bodyMargin=16*Math.cos(Math.PI/96)-Math.hypot(p.position.x+206,p.position.z+104)-.38
          }else{
            const d=i===3?deckFour:i?second:first
            r.bodyMargin=Math.min(d.w/2-Math.abs(p.position.x-d.x),d.d/2-Math.abs(p.position.z-d.z))-.38
          }
          break
        }
      }
      if(!r.settled){if(summit)r.last=p.position.toArray();break}
    }
    return hops
  }finally{host.dispose()}
}
const centre=simulate(0,0,{keepFrames:true})
const noSecond=simulate(0,0,{installed:false})
if(s2){console.log(JSON.stringify({second,centre:centre.map(({frames,...r})=>r),noSecond}));process.exit(0)}
assert.equal(corridor.sha,'60098a20322fb4dbc908ce9e22c53a5966e7f400a0275b5f829eb25af0deb2a6')
if(summit){
  const trim=hops=>hops.map(({frames,...r})=>{
    if(r.roofWalk){const {frames,...walk}=r.roofWalk;r.roofWalk=walk}
    return r
  })
  const old=simulate(0,0,{summitTarget:oldSummitHook,summitBracket:false})
  const cable=simulate(0,0,{summitTarget:launchPoint,summitBracket:false})
  const good=hops=>hops.length===5&&hops.every(r=>r.settled)&&hops[4].supportProbeRadius===.58
  assert(good(centre),JSON.stringify(trim(centre)))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true,named:true}))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true}))
  assert(old.length===5&&old[4].reach<38&&!old[4].visible&&!old[4].locked)
  assert(cable.length===5&&cable[4].locked&&!cable[4].settled&&cable[4].last[1]<37)
  const cases=[]
  for(const dx of [-1,-.5,0,.5,1])for(const dz of [-1,-.5,0,.5,1]){
    const h=simulate(dx,dz)
    assert(good(h),JSON.stringify({dx,dz,hops:trim(h)}))
    cases.push({offset:[dx,dz],hops:trim(h)})
  }
  const proof={scope:'Ground to summit, five native server hops. No zipline carry, course install, clock or phone test.',
    engine:'0.1.44',format:'0.43.0',frequencyHz:60,summitMeshSha:summitGeo.sha,summitRingSha:summitRing.sha,
    summitTriangles:summitGeo.value.reduce((n,g)=>n+g.triangles.length/3,0),
    hooks:[...hooks.map(h=>h.toArray()),rim,mastHook,summitHook],unchangedZiplineLaunch:launchPoint,
    centre,cases,oldProxyControl:trim(old).at(-1),cableAnchorControl:trim(cable).at(-1)}
  writeFileSync(output,JSON.stringify(proof)+'\n')
  console.log(JSON.stringify({hops:trim(centre),cases:cases.length,old:proof.oldProxyControl,cable:proof.cableAnchorControl}))
  process.exit(0)
}
if(mast){
  const trim=hops=>hops.map(({frames,...r})=>{
    if(r.roofWalk){const {frames,...walk}=r.roofWalk;r.roofWalk=walk}
    return r
  })
  const misses=simulate(0,0,{installedMast:false})
  const rawLock=simulate(-1,-1,{crossRoof:false})
  assert(rawLock.length===4&&!rawLock[3].visible&&!rawLock[3].locked)
  assert(centre.length===4&&centre.every(r=>r.settled&&r.bodyMargin>.09),JSON.stringify(trim(centre)))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true,named:true}))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true}))
  assert.deepEqual(trim(centre.slice(0,3)),trim(misses.slice(0,3)))
  assert(misses.length===4&&misses[3].visible&&misses[3].reach<38&&!misses[3].locked)
  const handbook=new Vector3(-212,45,-34)
  const visibleTowerProxy=new Vector3(-214.5,45.8,-34)
  const cases=[]
  for(const dx of [-1,-.5,0,.5,1])for(const dz of [-1,-.5,0,.5,1]){
    const hops=simulate(dx,dz),r=hops[3]
    assert(hops.length===4&&hops.every(h=>h.settled&&h.bodyMargin>.09),JSON.stringify({dx,dz,hops:trim(hops)}))
    const eye=new Vector3(...r.end).add(new Vector3(0,1.7,0))
    const nextPlanM=eye.distanceTo(handbook),nextProxyM=eye.distanceTo(visibleTowerProxy)
    assert(nextPlanM<38&&nextProxyM<38)
    cases.push({offset:[dx,dz],hops:trim(hops),nextPlanM,nextProxyM})
  }
  const proof={scope:'Four native server hops. Exact W08 mast with optional fourth deck; no fifth lock, timer, course install or phone test.',
    engine:'0.1.44',format:'0.43.0',frequencyHz:60,meshSha:corridor.sha,tankMeshSha:extra.sha,mastMeshSha:mastGeo.sha,
    mastTriangles:mastGeo.value.reduce((n,g)=>n+g.triangles.length/3,0),firstDressingSha:oneDress.sha,
    secondDressingSha:dress.sha,saddleSha:saddle.sha,receiverSha:receiver.sha,deck:deckFour,
    hooks:[...hooks.map(h=>h.toArray()),rim,mastHook],nextPlan:handbook.toArray(),nextProxy:visibleTowerProxy.toArray(),
    centre,cases,withoutReceiver:trim(misses),noWalk:trim(rawLock)}
  writeFileSync(output,JSON.stringify(proof)+'\n')
  console.log(JSON.stringify({hops:trim(centre),cases:cases.length,nextPlanM:cases[12].nextPlanM,nextProxyM:cases[12].nextProxyM}))
  process.exit(0)
}
if(tank) {
  const trim=hops=>hops.map(({frames,...r})=>r)
  const centreControl=simulate(0,0,{roofHook:roofCentre,bracket:false})
  const noBracket=simulate(0,0,{bracket:false})
  assert(centre.length===3&&centre.every(r=>r.settled&&r.bodyMargin>.09),JSON.stringify(centre.map(({frames,...r})=>({...r,last:frames.at(-1)}))))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true,named:true}))
  assert.deepEqual(centre,simulate(0,0,{keepFrames:true}))
  assert.deepEqual(centre.map(r=>[r.ticks,r.end]),noBracket.map(r=>[r.ticks,r.end]))
  assert(centreControl.slice(0,2).every(r=>r.settled))
  assert(centreControl.length===3&&centreControl[2].reach>38&&!centreControl[2].locked)
  const cases=[]
  for(const dx of [-1,-.5,0,.5,1])for(const dz of [-1,-.5,0,.5,1]){
    const hops=simulate(dx,dz)
    assert(hops.length===3&&hops.every(r=>r.settled&&r.bodyMargin>.09),JSON.stringify({dx,dz,hops:trim(hops)}))
    cases.push({offset:[dx,dz],hops:trim(hops)})
  }
  const proof={scope:'Three consecutive native server hops. Exact W08 roof, guard and shell; optional rim hook. No course install, timer, or phone playtest.',
    engine:'0.1.44',format:'0.43.0',frequencyHz:60,meshSha:corridor.sha,tankMeshSha:extra.sha,
    tankTriangles:extra.value.reduce((n,g)=>n+g.triangles.length/3,0),
    firstDressingSha:oneDress.sha,secondDressingSha:dress.sha,saddleSha:saddle.sha,
    hooks:[...hooks.map(h=>h.toArray()),rim],centre,cases,centreControl:trim(centreControl),noBracket:trim(noBracket),
    nextMastEyeDistance:Math.hypot(centre[2].end[0]+200,centre[2].end[1]+1.7-28,centre[2].end[2]+68)}
  writeFileSync(output,JSON.stringify(proof)+'\n')
  console.log(JSON.stringify({centre:trim(centre),cases:cases.length,centreControl:centreControl[2],nextMastEyeDistance:proof.nextMastEyeDistance}))
  process.exit(0)
}
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
