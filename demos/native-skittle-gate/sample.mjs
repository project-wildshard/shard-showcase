import { createHash } from 'node:crypto'
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const req = createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT), 'package.json') : import.meta.url)
const root = dirname(req.resolve('@wildshard/engine/package.json'))
assert.equal(JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version, '0.1.44')
const formatVersion = JSON.parse(readFileSync(join(dirname(req.resolve('@wildshard/format/scriptAbiV1')),'../../package.json'),'utf8')).version
assert.equal(formatVersion,'0.43.0')
const at = relative => import(pathToFileURL(join(root,relative)).href)
await at('scripts/sim-node-loader.mjs')
const {Physics}=await at('src/shared/engine/physics/Physics.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {Scope}=await at('src/shared/engine/app/scope.ts')
const {DeclaredBodyOps}=await at('src/server/game/quest/bodyOps.ts')
const {SCRIPT_V1_COMMANDS: C,SCRIPT_V1_READS: Reads}=await import('@wildshard/format/scriptAbiV1')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const [geometryFile,proofFile,traceFile,mode]=process.argv.slice(2)
assert(mode===undefined||mode==='--lever'||mode==='--reset','Unknown fixture mode')
const bench=mode?await import('./lever.mjs'):null
assert(geometryFile&&proofFile&&traceFile,'Need ramp triangles, proof, replay paths')
const input=readFileSync(geometryFile)
const geometrySHA256=createHash('sha256').update(input).digest('hex')
assert.equal(geometrySHA256,'7cab1ab062d1e498457d701eeccfc06704ff88f1c3d7e15c4fcb835e9657f57b')
const geometry=JSON.parse(input)
const laneZ=196, floor=.04, slope=.25, toe=-42
const gate={x:-26.14,baseY:4.72,z:laneZ,half:[.088,.49,1.83],lift:1.78,ticks:36}
const dt=1/60, roundTicks=1200, resultWindowTicks=60, settleTicks=240
const p=(x,y,z)=>({x,y,z})
const tilt=q=>Math.acos(Math.max(-1,Math.min(1,1-2*(q.x*q.x+q.z*q.z))))*180/Math.PI

function trial(offset,release,exercise){
  const rows=[]
  for(let i=0;i<4;i++){
    const x=-19.5-1.8*i
    rows.push({id:'ball-'+(i+1),kind:'prop',shape:{ball:.8},
      at:p(x,(x-toe)*slope+.8/Math.cos(Math.atan(slope))+.014,laneZ+offset), yaw:0,
      owner:{kind:'w4b-gate-fixture',id:'ball-'+(i+1)},material:'metal',density:130,
      friction:.70,restitution:.04,angularDamping:.08,rolling:.025,ccd:true})
  }
  for(let r=0;r<4;r++)for(let i=0;i<=r;i++){
    const id='pin-'+(rows.length-3)
    rows.push({id,kind:'prop',shape:{cylinder:{radius:.25,halfHeight:.645}},at:p(-50-r*1.2,floor+.648,laneZ+(i-r/2)*1.1),
      yaw:0,owner:{kind:'w4b-gate-fixture',id},material:'wood',density:170,
      friction:.58,restitution:.04,angularDamping:.22,linearDamping:.32,rolling:.045,ccd:true})
  }
  const session=exercise===undefined?null:bench.make(R,exercise)
  // The lever bench lends the exact physics world used by its own stock player.
  const scope=session?.sim.scope??new Scope('w4b gate')
  const phy=session?.sim.physics??new Physics(R)
  try{
    const W=phy.world
    W.createCollider(R.ColliderDesc.cuboid(39,1,27).setTranslation(-53,floor-1,laneZ).setCollisionGroups(groups('WORLD')).setFriction(.8))
    W.createCollider(R.ColliderDesc.trimesh(new Float32Array(geometry.vertices),new Uint32Array(geometry.triangles))
      .setCollisionGroups(groups('WORLD')).setFriction(.8))
    const bar=W.createRigidBody(R.RigidBodyDesc.kinematicPositionBased().setTranslation(gate.x,gate.baseY,gate.z))
    W.createCollider(R.ColliderDesc.cuboid(...gate.half).setCollisionGroups(groups('WORLD')).setFriction(.42),bar)
    const data={bodies:rows,floors:[],colliders:[]}
    const ops=DeclaredBodyOps.native({physics:phy,scope,playerFocus:p(-46,0,laneZ)},data)
    const id=row=>ops.registries.bodies.get(row.id)
    for(let i=0;i<rows.length;i+=4)
      ops.prepare(rows.slice(i,i+4).map(row=>[C['body.spawn'],0,id(row),0,0])).commit()
    assert(rows.every(row=>ops.read(Reads.bodyAlive,id(row),0)===1))
    const bodies=rows.map(row=>ops.body(row.id)), balls=bodies.slice(0,4)
    session?.setup(W)
    function step(input){ops.pre(dt);if(session===null)phy.step();else session.sim.step(input);ops.post(dt)}
    for(let i=0;i<settleTicks;i++)step()
    const held=balls.map(b=>({...b.curr}))
    assert(held.every(v=>v.x>gate.x+.49&&v.x<-19&&Math.abs(v.z-laneZ)<1.05),JSON.stringify(held))
    const activated=session?.approach(step)
    const frame=tick=>({tick,bar:{...bar.translation()},bodies:bodies.map((b,i)=>({id:rows[i].id,p:{...b.curr},q:{...b.currRot}}))})
    function roll(){
      const frames=[]
      const toes=Array(4).fill(null), gatePasses=Array(4).fill(null)
      let firstTip=null
      const endCounts=[]
      frames.push(frame(0))
      for(let i=1;i<=roundTicks;i++){
        if((session===null?release:session.on()) && i<=gate.ticks){
          const q=i/gate.ticks
          bar.setNextKinematicTranslation(p(gate.x,gate.baseY+gate.lift*(3*q*q-2*q*q*q),gate.z))
        }
        step()
        for(let j=0;j<4;j++){
          if(gatePasses[j]===null&&balls[j].curr.x<gate.x)gatePasses[j]=i
          if(toes[j]===null&&balls[j].curr.x<toe)toes[j]=i
        }
        if(firstTip===null&&bodies.slice(4).some(b=>tilt(b.currRot)>60))firstTip=i
        if(exercise==='replay'&&i>roundTicks-resultWindowTicks)endCounts.push(bodies.slice(4).filter(b=>tilt(b.currRot)>60).length)
        if(i%6===0)frames.push(frame(i))
      }
      const angles=bodies.slice(4).map(b=>tilt(b.currRot))
      const fallen=angles.filter(a=>a>60).length
      assert(bodies.every(b=>[b.curr.x,b.curr.y,b.curr.z].every(Number.isFinite)))
      return {toes,gatePasses,firstTip,fallen,angles,frames,...(exercise==='replay'?{endCounts}:{})}
    }
    if(exercise==='replay')session.earlyReset(step)
    const first=roll()
    if(exercise!=='replay')return {offset,release,held,...first,
      ...(session===null?{}:{exercise,activation:activated,transitions:session.transitions()})}
    let current=0, best=0
    const score=entry=>{
      assert(entry.toes.every(Number.isInteger))
      assert(entry.endCounts.length===resultWindowTicks&&entry.endCounts.every(n=>n===entry.fallen))
      assert(entry.fallen>0&&entry.fallen<=10)
      current=entry.fallen
      best=Math.max(best,current)
      return current
    }
    const scores=[score(first)], bestAfterFirst=best
    session.result()
    // No unprompted reset as the finished player waits at the handle.
    for(let i=0;i<60;i++)step()
    assert(balls.every(b=>b.curr.x<toe))
    session.reset(step)
    current=0
    session.duringReset(step)
    const clear=()=>bodies.every(b=>[b.curr.x,b.curr.y,b.curr.z].every(Number.isFinite))
    // All four balls have left the bar before this reset can be requested.
    for(let i=1;i<=gate.ticks;i++){
      const q=i/gate.ticks
      bar.setNextKinematicTranslation(p(gate.x,gate.baseY+gate.lift*(1-3*q*q+2*q*q*q),gate.z))
      step()
    }
    const resetBar={...bar.translation()}
    assert(Math.abs(resetBar.y-gate.baseY)<1e-5)
    ops.prepare(rows.map(row=>[C['body.teleport'],id(row),row.at.x,row.at.y,row.at.z])).commit()
    for(let i=0;i<settleTicks;i++)step()
    assert(clear())
    assert(rows.every((row,i)=>ops.body(row.id)===bodies[i]))
    const resetHeld=balls.map(b=>({...b.curr}))
    assert(resetHeld.every(v=>v.x>gate.x+.49&&v.x<-19&&Math.abs(v.z-laneZ)<1.05))
    assert(bodies.slice(4).every(b=>tilt(b.currRot)<2))
    assert.equal(best,bestAfterFirst)
    const scoreAfterReset={current,best}
    const resetFrame=frame(0)
    session.rearm()
    session.replay(step)
    const second=roll()
    scores.push(score(second))
    assert.equal(session.transitions(),3)
    return {activation:activated,earlyResetRejected:true,unpromptedResetRejected:true,releaseDuringResetRejected:true,first,second,resetFrame,resetHeld,resetBar,scores,scoreAfterReset,best,transitions:3}
  }finally{
    if(session)session.sim.dispose()
    else {scope.dispose();phy.dispose()}
  }
}
if(bench!==null){
  await bench.init(at)
  const runs=['no-input','blocked-sight','press','press'].map(kind=>trial(0,kind==='press',kind))
  assert.deepEqual(runs[2],runs[3])
  const [idle,blocked,pressed]=runs
  for(const row of [idle,blocked]){
    assert.equal(row.transitions,0)
    assert.deepEqual(row.toes,[null,null,null,null])
    assert.equal(row.fallen,0)
  }
  assert.deepEqual(idle.held,blocked.held)
  assert.deepEqual(idle.held,pressed.held)
  assert.equal(pressed.transitions,1)
  for(const frame of pressed.frames.slice(-11))assert.equal(frame.bodies.slice(4).filter(b=>tilt(b.q)>60).length,pressed.fallen)
  assert(pressed.toes.every(Number.isInteger)&&pressed.fallen>0,JSON.stringify(pressed.toes))
  const assets=new URL('../../public/assets/wildshard-art/',import.meta.url)
  const donors=Object.fromEntries(['w4b-release-stand.glb','w4b-ball-gate-bar.glb','w4b-ball-gate-yoke.glb','wsc-plan-004-rolling-ball.glb','wsc-plan-005-skittle-pin.glb']
    .map(name=>[name,createHash('sha256').update(readFileSync(new URL(name,assets))).digest('hex')]))
  assert.deepEqual(donors,{
    'w4b-release-stand.glb':'c81fe635452ec55a31bdbd6db1980a26a252f0c3dbc945aefa89cd1b462eb54d',
    'w4b-ball-gate-bar.glb':'904f00c4786f491114112a165e516eb2ff3ae5aabe76a886bcb8bfd72165c960',
    'w4b-ball-gate-yoke.glb':'bfc8d29690d27da4bafe01feee379aaabb875aec6db0f01781ba3f4dcb79624c',
    'wsc-plan-004-rolling-ball.glb':'c04881c87359049db80b6f17772628543628688dd6fee3c58e1bf6f7f3ebe171',
    'wsc-plan-005-skittle-pin.glb':'6863ee9338d4859d2a7ef68dd556e16cdeb2949c6cb33a9ca90c808531fe1d43',
  })
  if(mode==='--reset'){
    const r=trial(0,true,'replay'), repeat=trial(0,true,'replay')
    assert.deepEqual(r,repeat)
    const brief=({frames,endCounts,...entry})=>entry
    const {first,second,resetFrame,...evidence}=r
    const summary={scope:'Isolated native player, prompt and physical prop bench; in-memory score only.',engine:'0.1.44',format:formatVersion,
      hz:60,geometrySHA256,donors,stand:bench.stand,spot:bench.spot,gate,roundTicks,scoreWindowTicks:resultWindowTicks,
      resetGateTicks:gate.ticks,resetSettleTicks:settleTicks,samePlayerSession:true,independentReplayMatched:true,
      ...evidence,first:brief(first),second:brief(second)}
    writeFileSync(proofFile,JSON.stringify(summary,null,2)+'\n')
    writeFileSync(traceFile,JSON.stringify({gate,geometrySHA256,blocked:idle,released:pressed,stand:bench.stand,
      spot:bench.spot,donors,replay:{activation:r.activation,first,resetFrame,second}})+'\n')
    console.log(JSON.stringify({scores:r.scores,scoreAfterReset:r.scoreAfterReset,toes:[first.toes,second.toes]}))
  }else{
    const summary={scope:'Authored prompt and stock player in the isolated native ramp bench; physical lift bridge belongs to the fixture.',engine:'0.1.44',format:formatVersion,
      hz:60,geometrySHA256,donors,stand:bench.stand,spot:bench.spot,gate,runs:runs.slice(0,3).map(({frames,...row})=>row),freshReplayMatched:true}
    writeFileSync(proofFile,JSON.stringify(summary,null,2)+'\n')
    writeFileSync(traceFile,JSON.stringify({gate,geometrySHA256,blocked:idle,released:pressed,stand:bench.stand,spot:bench.spot,donors})+'\n')
    console.table(summary.runs.map(({exercise,activation,transitions,toes,fallen})=>({exercise,activation:JSON.stringify(activation),transitions,toes,fallen})))
  }
} else {
  const runs=[]
  for(const o of [-.12,0,.12]){
    const blocked=trial(o,false), released=trial(o,true)
    assert.deepEqual(blocked.held,released.held)
    assert(blocked.gatePasses.every(x=>x===null)&&blocked.toes.every(x=>x===null)&&blocked.firstTip===null,JSON.stringify(blocked.toes))
    assert(released.toes.every(Number.isInteger)&&released.firstTip!==null&&released.fallen>0,JSON.stringify(released.toes))
    runs.push(blocked,released)
  }
  assert.deepEqual(trial(0,true),runs[3])
  writeFileSync(proofFile,JSON.stringify({engine:'0.1.44',format:formatVersion,hz:60,gate,geometrySHA256,
    runs:runs.map(({frames,...r})=>r)},null,2)+'\n')
  writeFileSync(traceFile,JSON.stringify({gate,geometrySHA256,blocked:runs[2],released:runs[3]})+'\n')
  console.table(runs.map(({offset,release,gatePasses,toes,firstTip,fallen})=>({offset,release,gatePasses,toes,firstTip,fallen})))
}
