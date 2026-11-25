import assert from 'node:assert/strict'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
import {readFileSync,writeFileSync} from 'node:fs'

const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
const root=dirname(packagePath)
const formatPath=req.resolve('@wildshard/format/modes')
const at=p=>import(pathToFileURL(join(root,p)).href)
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44')
assert.equal(JSON.parse(readFileSync(join(dirname(formatPath),'../../package.json'))).version,'0.43.0')
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {safeParse}=await import('valibot')
const {TraverseModeSchema}=await import(pathToFileURL(formatPath).href)
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const dt=1/60, top=.5195, halfW=.639, halfL=2.059, lane=-103
const belts=[{x:-84,v:-3},{x:-90,v:4},{x:-96,v:-5}]
const yaw=Math.PI/2, crateHalf=.244
assert(process.argv[2],'Output path required')
const rejected=safeParse(TraverseModeSchema,{kind:'conveyor',id:'w6b-belt',box:{},velocity:[-3,0]})
assert(!rejected.success&&rejected.issues.some(i=>i.path?.[0]?.key==='kind'))
const point=(x,y,z)=>({x,y,z})
const sampleBody=(b)=>{const t=b.translation(),v=b.linvel();return {pos:[t.x,t.y,t.z],vel:[v.x,v.y,v.z]}}
function trial(belt,config={}){
  const {active=true,crate=false,block=false,walk=0,jump=false,off=false,board=false}=config
  const x=belt.x+(block?.9*Math.sign(belt.v):0)
  const host=new SimHost({version:SIM_API_VERSION,id:'w6b-belt-bench',seed:25,
    ground:{size:500,height:.1},player:{at:{x:crate?x-.7:x,y:crate?.105:top+.055,z:off||crate?lane+2:lane},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'), W=host.physics.world
  const box=(x,y,z,l,h,w,friction=.7)=>W.createCollider(R.ColliderDesc.cuboid(l,h,w)
      .setTranslation(x,y,z).setCollisionGroups(groups('WORLD')).setFriction(friction))
  box(-90,-.91,lane,10,1,2.5)
  const at=belts.map(b=>box(b.x,top-.22,lane,halfL,.22,halfW,0))
  const floor=at[belts.indexOf(belt)]
  if(block)box(belt.x+Math.sign(belt.v)*1.64,top+.5,lane,.105,.5,.625)
  let rb=null,item=null
  if(crate){
    rb=W.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(x,top+crateHalf+.02,lane).lockRotations().setCanSleep(false))
    item=W.createCollider(R.ColliderDesc.cuboid(crateHalf,crateHalf,crateHalf)
      .setCollisionGroups(groups('ITEM')).setFriction(0).setDensity(100),rb)
  }
  const trace=[]
  let controlStarted=false
  let contact=false
  function input(k){
    return new Map([[p.id,{moveX:walk,moveZ:0,yaw,jump:jump&&k===6,hover:board&&k===0}]])
  }
  try {
    for(let i=0;i<48;i++)host.step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    assert(crate||off||Math.abs(p.position.y-top)<.04)
    for(let tick=0;tick<=78;tick++){
      // Force only during actual tread contact. The deck is stationary and
      // no row is inserted by the stock room: this is the local bench adapter.
      let drive=0
      if(active&&rb&&contact) {
        const v=rb.linvel()
        const dv=Math.min(24*dt,Math.max(-24*dt,belt.v-v.x))
        rb.applyImpulse(point(dv*rb.mass(),0,0),true)
        drive=dv
      }
      host.step(input(tick))
      if(rb){
        contact=false
        W.contactPair(item,floor,(m)=>{
          if(m.numSolverContacts()>0 && Math.abs(m.normal().y)>.9 && Math.abs(rb.translation().y-crateHalf-top)<.035)contact=true
        })
      }else{
        // A tiny ordinary downward probe refreshes the stock collider ID
        // during neutral controls. It does not add horizontal movement.
        if(p.fall.grounded&&!p.board.on)p.motor.move(p.position,point(0,-.004,0))
        contact=!p.board.on&&p.fall.grounded&&p.motor.result.groundCollider?.handle===floor.handle
        if(active&&contact){
          const old=p.position.x
          const moved=p.motor.move(p.position,point(belt.v*dt,-.004,0))
          p.fall.grounded=moved.grounded
          drive=p.position.x-old
        }
      }
      controlStarted ||= contact
      const state=rb?sampleBody(rb):{pos:p.position.toArray(),vel:p.velocity.toArray()}
      trace.push({tick,contact,drive,board:p.board.on,...state})
    }
    return {trace,controlStarted,groundY:.09}
  } finally {host.dispose()}
}
const trials=[]
for(const b of belts){
  const stationary=trial(b,{active:false}), moving=trial(b)
  const crateBase=trial(b,{crate:true,active:false}), cargo=trial(b,{crate:true})
  const best=(r,a,c)=>(r.trace[c].pos[0]-r.trace[a].pos[0])*60/(c-a)
  assert(moving.controlStarted&&cargo.controlStarted)
  assert(Math.abs(best(stationary,2,20))<.01 && Math.abs(best(crateBase,2,20))<.01)
  const pace=best(moving,2,20), cargoPace=best(cargo,15,24)
  assert(Math.abs(pace-b.v)<.03&&Math.abs(cargoPace-b.v)<.04,JSON.stringify({pace,cargoPace,b}))
  const exit=moving.trace.find((f,i,a)=>i>1&&a[i-1].contact&&!f.contact)
  assert(exit&&moving.trace.slice(exit.tick+1).every(f=>Math.abs(f.drive)<1e-6))
  const air=trial(b,{jump:true})
  assert(air.trace.some(f=>f.tick>=6 && f.pos[1]>top+.20 && f.drive===0))
  assert(air.trace.every(f=>f.pos[1]<=top+.15||f.drive===0))
  const off=trial(b,{off:true})
  assert(off.trace.every(f=>!f.contact && f.drive===0))
  const wall=trial(b,{block:true})
  const maxRelative=Math.max(...wall.trace.map(f=>(f.pos[0]-b.x)*Math.sign(b.v)))
  assert(maxRelative<1.64-.105-.38+.045)
  const walkAlongSign=Math.sign(b.v)
  const withbelt=trial(b,{walk:walkAlongSign})
  const against=trial(b,{walk:-walkAlongSign})
  assert(Math.sign(best(withbelt,2,10))===Math.sign(b.v))
  const deltaWith=best(withbelt,2,10), deltaAgainst=best(against,2,10)
  const baseWith=best(trial(b,{walk:walkAlongSign,active:false}),2,10)
  const baseAgainst=best(trial(b,{walk:-walkAlongSign,active:false}),2,10)
  assert(Math.abs(deltaWith-baseWith-b.v)<.06 && Math.abs(deltaAgainst-baseAgainst-b.v)<.06,JSON.stringify({belt:b.v,deltaWith,deltaAgainst,baseWith,baseAgainst}))
  const board=trial(b,{board:true})
  assert(board.trace.every(f=>f.board && !f.contact && f.drive===0))
  assert.deepEqual(board,trial(b,{board:true,active:false}))
  assert.deepEqual(cargo,trial(b,{crate:true}))
  assert.deepEqual(moving,trial(b))
  trials.push({belt:b,pace,cargoPace,exitTick:exit.tick,jumpNoDrive:true,offNoDrive:true,boardNoDrive:true,maxRelative,deltaWith,deltaAgainst,baseWith,baseAgainst,
    player:moving.trace,cargo:cargo.trace,jump:air.trace})
}
const summary=trials.map(({player,cargo,jump,...v})=>v)
console.log(JSON.stringify(summary))
writeFileSync(process.argv[2],JSON.stringify({scope:'Explicit local conveyor contact adapter with native player capsule and separate native rigid body trials; no stock conveyor row or live installation.',
  engine:'0.1.44',format:'0.43.0',clockHz:60,lane,top,halfW,halfL,crateHalf,summary,trials})+'\n')
