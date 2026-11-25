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
assert.equal(process.argv.length, 6, 'Expected base geometry, receiver geometry, replay output and proof output');
const raw=readFileSync(process.argv[2]), geometry=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
assert.equal(hash,'b4bbdedf55a33ec120497bd36578aa8a96d2eceb1e96cc24ab6b20c410a24b27')
const receiverRaw=readFileSync(process.argv[3]), receiver=JSON.parse(receiverRaw)
const lane=[4.8,154]
const yaw=Math.PI/2
function play([height,z],{ramp=true,jumpAt=null,jumpTick=null,offset=0,startX=-114,fit=false}={}){
  const host=new SimHost({version:SIM_API_VERSION,id:'w5a-kicker-bench',seed:25,
    ground:{size:500,height:0},player:{at:{x:startX,y:.18,z:z+offset},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  try {
    for(const g of [...geometry,...(fit ? [receiver] : [])]){
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
    for(let tick=0;tick<=520;tick++){
      const jump=!pressed&&(tick===jumpTick||(jumpAt!==null&&p.position.x<=jumpAt))
      if(jump)pressed=true
      const go=p.position.x>-204.0
      host.step(new Map([[p.id,{moveX:go?-1:0,moveZ:0,yaw,
        ...(tick===0?{hover:true}:{}),...(jump?{jump:true}:{})}]]))
      if(tick===0)assert(p.board.on)
      if(p.board.on&&frames.at(-1)?.air&&!p.board.hoverAir&&frames.at(-1).v[1]-.25<-9)hardHits++
      hpMin=Math.min(hpMin,p.health.attributes.health)
      frames.push({tick,feet:p.position.toArray(),v:p.velocity.toArray(),
        onGround:p.board.onGround,air:p.board.hoverAir,jump})
      if(p.position.x<=-204.0) break // Stop capture before the separate east launch wall, not a braking claim.
    }
    return {height,z,ramp,fit,startX,jumpAt,jumpTick,offset,hardHits,hp0,hpMin,hpEnd:p.health.attributes.health,frames}
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

const table=[], controls=[], replay=[]
for(const startX of [-116,-114,-112]) for(const offset of [-1.10,-.65,0,.65,1.10]){
  const passive=play(lane,{startX,offset,fit:true})
  const noDeck=play(lane,{startX,offset})
  const target=noDeck.frames.find(k=>k.feet[0]<=-167.04).tick
  const summary=assess(passive)
  // Both routes cross the actual extended return without an artificial shove or damage.
  assert.equal(summary.airTicks,0)
  assert.equal(summary.hpMin,100)
  assert.ok(summary.last[0] <= -204.0 && summary.groundAtEnd)
  assert.ok(summary.last[1] >= .032 && summary.last[1] < .78, JSON.stringify({startX,offset,last:summary.last}))
  const batch=[]
  for(let adjust=-4;adjust<=4;adjust++){
    const jumpTick=target+adjust
    const run=play(lane,{startX,offset,jumpTick,fit:true})
    const r=assess(run)
    assert.ok(r.last[0]<=-204.0 && r.groundAtEnd && !run.frames.at(-1).air && r.hpMin===100, JSON.stringify({startX,offset,adjust,r}))
    const flew=r.airTicks>0
    if(flew) assert.ok(r.landed && r.landed.v[1]>=-9 && r.hardHits===0)
    batch.push({adjust,jumpTick,flew,airTicks:r.airTicks,apexY:r.peak.feet[1],
      landingX:r.landed?.feet[0]??null,landingVy:r.landed?.v[1]??null,
      minHP:r.hpMin,returnedY:r.last[1]})
    if(adjust===0){
      const control=play(lane,{startX,offset,jumpTick,fit:false})
      const q=assess(control)
      assert.ok(r.airTicks>0&&r.peak.feet[1]>7.3&&r.hpMin===100, JSON.stringify({startX,offset,r}))
      assert.ok(q.airTicks>0&&q.hpMin<93&&q.hardHits===1)
      controls.push({startX,offset,stock:r.landed.v[1],bare:q.landed.v[1],bareHP:q.hpMin})
      if(startX===-114&&offset===0)replay.push(passive,run,control)
    }
  }
  table.push({startX,offset,passive:summary,batch})
}
const flew=table.flatMap(v=>v.batch).filter(v=>v.flew)
const results={engine:'0.1.44', clockHz:60, exactDonor:hash,
  receiverSha256:createHash('sha256').update(receiverRaw).digest('hex'),
  fit:receiver.fit, strongestContactMps:Math.min(...flew.map(v=>v.landingVy)),
  attempts:table.length*table[0].batch.length, accepted:flew.length,
  controlledHighJumps:controls.length, passive:table.length, controls,table}
writeFileSync(process.argv[4], JSON.stringify({results:replay})+'\n')
writeFileSync(process.argv[5], JSON.stringify(results,null,2)+'\n')
console.log(JSON.stringify(Object.fromEntries(Object.entries(results).filter(([k])=>!['table','controls'].includes(k)))))
