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
assert(process.argv[2]&&process.argv[3]&&process.argv[4],'Expected geometry input, replay JSON output and compact proof')
const raw=readFileSync(process.argv[2]), geometry=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
const lanes=[[2.4,132],[3.6,143],[4.8,154]]
const yaw=Math.PI/2
function play([height,z],{ramp=true,jumpAt=null,jumpTick=null,offset=0}={}){
  const host=new SimHost({version:SIM_API_VERSION,id:'w5a-kicker-bench',seed:25,
    ground:{size:500,height:0},player:{at:{x:-114,y:.18,z:z+offset},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  try {
    for(const g of geometry){
      if(g.name.includes('ramp ')&&(!ramp||!g.name.includes('ramp '+height.toFixed(1)+' ')))continue
      if(g.name.includes('run-up ')&&!g.name.includes('run-up '+height.toFixed(1)+' '))continue
      W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
    }
    for(let k=0;k<50;k++)host.step()
    assert(p.hasMotor&&p.fall.grounded)
    const frames=[]
    let hardHits=0, hpMin=100
    const hp0=p.health.attributes.health
    let pressed=false
    for(let tick=0;tick<=380;tick++){
      const jump=!pressed&&(tick===jumpTick||(jumpAt!==null&&p.position.x<=jumpAt))
      if(jump)pressed=true
      const go=p.position.x>-183
      host.step(new Map([[p.id,{moveX:go?-1:0,moveZ:0,yaw,
        ...(tick===0?{hover:true}:{}),...(jump?{jump:true}:{})}]]))
      if(tick===0)assert(p.board.on)
      if(p.board.on&&frames.at(-1)?.air&&!p.board.hoverAir&&frames.at(-1).v[1]-.25<-9)hardHits++
      hpMin=Math.min(hpMin,p.health.attributes.health)
      frames.push({tick,feet:p.position.toArray(),v:p.velocity.toArray(),
        onGround:p.board.onGround,air:p.board.hoverAir,jump})
    }
    return {height,z,ramp,jumpAt,jumpTick,offset,hardHits,hp0,hpMin,hpEnd:p.health.attributes.health,frames}
  }finally{host.dispose()}
}
function assess(r){
  const {frames,...properties}=r
  const press=frames.find(f=>f.jump)
  const air=frames.filter(f=>f.air)
  const peak=frames.reduce((p,q)=>p.feet[1]>q.feet[1]?p:q)
  const start=air[0], end=air.at(-1), landed=end&&frames[end.tick+1]
  return {...properties,press,airTicks:air.length,peak,start,end,landed,
    peakSpeed:Math.max(...frames.map(f=>Math.abs(f.v[0]))),
    groundAtEnd:frames.at(-1).onGround,last:frames.at(-1).feet}
}
const results=[], report=[]
for(const lane of lanes){
  const passive=play(lane), baseline=assess(passive)
  assert(baseline.peak.feet[1]>=lane[0]&&baseline.peak.feet[1]<lane[0]+.32)
  assert(baseline.hp0===100&&baseline.hpEnd===100&&baseline.airTicks===0&&baseline.groundAtEnd&&baseline.last[0]<-187)
  const ticks=passive.frames.filter(f=>f.feet[0]<=-157&&f.feet[0]>=baseline.peak.feet[0]).map(f=>f.tick)
  const trials=ticks.map(jumpTick=>assess(play(lane,{jumpTick})))
  const accepted=trials.filter(t=>t.airTicks>0&&t.start.tick===t.jumpTick)
  const refused=trials.filter(t=>t.airTicks===0)
  assert(accepted.length>0&&refused.length>0&&accepted.length+refused.length===trials.length)
  for(const t of refused)assert.deepEqual(t.last,baseline.last)
  const late=accepted.filter(t=>t.peak.feet[1]>lane[0]+.65&&t.groundAtEnd)
  const chosen=late.sort((a,b)=>b.peak.feet[1]-a.peak.feet[1])[0]
  assert(chosen&&chosen.landed&&chosen.hp0===100&&chosen.hpMin>=92&&chosen.hpMin<92.07)
  const ref=play(lane,{jumpTick:chosen.jumpTick}), without=play(lane,{ramp:false,jumpTick:chosen.jumpTick})
  assert.deepEqual(ref,play(lane,{jumpTick:chosen.jumpTick}))
  assert(assess(without).peak.feet[1]<chosen.peak.feet[1])
  const width=[-.5,.5].map(offset=>assess(play(lane,{jumpTick:chosen.jumpTick,offset})))
  const ranges=ts=>ts.reduce((a,t)=>{ const p=a.at(-1)
    if(p&&t.jumpTick===p[1]+1)p[1]=t.jumpTick
    else a.push([t.jumpTick,t.jumpTick])
    return a },[])
  results.push(passive,ref,without)
  report.push({height:lane[0],z:lane[1],baseline,chosen,without:assess(without),width,
    sampleCount:ticks.length,acceptedTicks:ranges(accepted),refusedTicks:ranges(refused),
    lastSafeCandidate:accepted.filter(t=>t.hpMin===100&&t.peak.feet[1]>lane[0]+.4).at(-1)?.jumpTick??null})
}
const meta={engine:'0.1.44',clockHz:60,geometrySha256:hash,meshes:geometry.length,
  triangles:geometry.reduce((s,g)=>s+g.triangles.length/3,0)}
writeFileSync(process.argv[3],JSON.stringify({...meta,results})+'\n')
writeFileSync(process.argv[4],JSON.stringify({...meta,lanes:report},null,2)+'\n')
for(const {height,baseline,chosen,without,width,sampleCount,acceptedTicks,refusedTicks,lastSafeCandidate} of report){
 console.log(JSON.stringify({height,peak:baseline.peak.feet[1],sampleCount,acceptedTicks,refusedTicks,lastSafeCandidate,
   best:[chosen.jumpTick,chosen.start.feet,chosen.peak.feet,chosen.airTicks,chosen.hardHits,chosen.hp0,chosen.hpMin,chosen.hpEnd],
   noRamp:without.peak.feet[1],offsets:width.map(t=>[t.airTicks,t.peak.feet[1],t.hardHits,t.groundAtEnd])}))
}
