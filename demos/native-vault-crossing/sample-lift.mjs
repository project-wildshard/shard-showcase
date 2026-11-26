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
const format=req.resolve('@wildshard/format/movers')
assert.equal(JSON.parse(readFileSync(join(dirname(format),'../../package.json'))).version,'0.43.0')
const {parseMovers}=await import(pathToFileURL(format).href)
const {lowerMoverMotion}=await import(pathToFileURL(req.resolve('@wildshard/format/moverMotion')).href)
const {MoverScriptDriver}=await at('src/server/game/plugin/mover.ts')
const {tagOf}=await at('src/shared/engine/physics/surface.ts')
const out=resolve(process.argv[2])
const raw=readFileSync(join(out,'lift-collision.json'))
const parts=JSON.parse(raw)
const y=-44.5,x=196,z=-64,rise=4,euler={x:0,y:0,z:0},rot={...euler,w:1}
const origin={x,y,z}
const track={clip:'VaultLift',duration:2.5,loop:'once',speed:1,times:[0,.25,.6,1.25,1.9,2.25,2.5],
  position:[0,.085,.436,2,3.564,3.915,rise].map(h=>[x,y+h,z])}
const trigger={kind:'shared',field:1,equals:true},driver={kind:'track'}
const row={id:'vault-r3-moving-deck',entity:2781,execution:'native',kind:'platform',at:origin,euler,enabled:true,
  boxes:[{x:0,y:-.115,z:0,hx:3,hy:.115,hz:3,rot}],track,trigger,driver,
  ...lowerMoverMotion({track,trigger,driver},{at:origin,euler})}
const movers=parseMovers([row]), signal='calibration_vault_lift'
const keep=g=>g.role!=='deck'&&(g.role!=='bridge'||/\| (Cedar amber|Honey endgrain|Red cedar|Weathered timber(?: color details)?)$/.test(g.name))
const geometry=parts.filter(keep)
const content={identity:{seed:25},sim:{scripts:[],bindings:[],scriptTickDivisor:1},state:{shared:[],player:[]}}
function run(offset,enable=true,trace=false){
  const yaw=-Math.PI/2
  const host=new SimHost({version:SIM_API_VERSION,id:'e10c-vault-native-lift',seed:25,
    ground:{size:500,height:-50},player:{at:{x:181.3,y:-44.34,z:z+offset},yaw,speed:4.3},
    entities:[],quests:[],weapon:{id:'fixture-disabled',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world,owned=new Map()
  try{
    for(const g of geometry){
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),
        new Uint32Array(g.triangles)).setCollisionGroups(groups('WORLD')))
      owned.set(c.handle,g.role)
    }
    const runtime=new MoverScriptDriver(movers,host).install(host,
      {content,assets:new Map(),rules:{fields:{},archetypes:[],events:[],maxEntities:32}},
      {id:'e10c.rehearsal.lift',joined:true,drive:true,
        activation:{shared:n=>n===1?host.flags.has(signal):undefined}})
    const state=()=>{
      const g=p.motor.result.groundCollider
      const owner=g?tagOf(g)?.owner:undefined
      return {tick:host.state.tick,feet:p.position.toArray(),y:runtime.pose(row.id).position.y,
        floor:owner===row.id||owner?.id===row.id?'movingDeck':g?owned.get(g.handle)??null:null,grounded:p.fall.grounded}
    }
    const step=(walk=0)=>host.step(new Map([[p.id,{moveX:walk,moveZ:0,yaw}]]))
    for(let i=0;i<50;i++)step()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const boardFrames=[], ascFrames=[], exitFrames=[]
    let boardAir=0, ascentAir=0, ascentOther=0, exitAir=0,maxFootDelta=0
    for(let i=0;i<290&&p.position.x<195.55;i++){
      step(1)
      const s=state()
      boardAir+=Number(!s.grounded)
      if(trace&&i%4===0)boardFrames.push(s)
    }
    for(let i=0;i<6;i++)step()
    const boarded=state()
    assert(boarded.floor==='movingDeck'&&boardAir===0&&boarded.grounded,boarded)
    if(enable)host.flags.set(signal)
    let topTick=null,prevY=boarded.y
    for(let i=1;i<=175;i++){
      step()
      const s=state()
      assert(s.y>=prevY&&s.y<=y+rise);prevY=s.y
      if(s.y===y+rise&&topTick===null)topTick=i
      if(!s.grounded)ascentAir++
      if(s.floor!=='movingDeck')ascentOther++
      maxFootDelta=Math.max(maxFootDelta,Math.abs(s.feet[1]-s.y))
      if(trace&&i%5===0)ascFrames.push(s)
    }
    const afterRide=state()
    for(let i=0;i<160&&p.position.x<201.90&&p.position.y>-47.5;i++){
      step(1)
      const s=state()
      if(!s.grounded)exitAir++
      if(trace&&i%4===0)exitFrames.push(s)
    }
    return {offset,enable,boarded,afterRide,topTick,boardAir,ascentAir,ascentOther,maxFootDelta,exitAir,final:state(),
      ...(trace?{boardFrames,ascFrames,exitFrames}:{})}
  }finally{host.dispose()}
}
const cases=[-.45,-.225,0,.225,.45].map(o=>run(o))
const center=run(0,true,true), control=run(0,false,true)
assert.deepEqual(center,run(0,true,true))
const summary={scope:'Native 4 m platform track connected to the tested room 3 crossing; shared call is a test signal. Exit stops on upper landing before closed door.',
  engine:'0.1.44',format:'0.43.0',collisionHash:createHash('sha256').update(raw).digest('hex'),row,cases,center,control}
writeFileSync(join(out,'lift-walk.json'),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify({cases,control:{...control,boardFrames:undefined,ascFrames:undefined,exitFrames:undefined}}))
assert(cases.every(c=>c.topTick>=149&&c.topTick<=151&&c.ascentAir===0&&c.ascentOther===0&&c.maxFootDelta<.075
  &&c.exitAir===0&&c.final.floor==='upper'&&c.final.feet[0]>=201.9&&c.final.grounded))
assert(control.topTick===null&&control.final.floor!=='upper'&&control.final.feet[1]<-44)
