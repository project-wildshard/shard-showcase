import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const root=dirname(req.resolve('@wildshard/engine/package.json'))
const format=req.resolve('@wildshard/format/worldTargets')
assert.equal(JSON.parse(readFileSync(join(root,'package.json'))).version,'0.1.44')
assert.equal(JSON.parse(readFileSync(join(dirname(format),'../../package.json'))).version,'0.43.0')
const mod=p=>import(pathToFileURL(join(root,p)).href)
await mod('scripts/sim-node-loader.mjs')
const {SimHost}=await mod('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await mod('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await mod('src/shared/engine/physics/rapier.ts')
const {groups}=await mod('src/shared/engine/physics/groups.ts')
const {WorldTargetHost}=await mod('src/shared/game/shardfile/worldTargets.ts')
const {installNativeMelee,bindNativeLoadout}=await mod('src/server/game/plugin/simulation.ts')
const {parseWorldTargets,worldTargetRules}=await import(pathToFileURL(format).href)
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const [geometryFile,out]=process.argv.slice(2)
assert(geometryFile&&out)
const raw=readFileSync(geometryFile)
const {fixtures,parts}=JSON.parse(raw)
const geometrySha256=createHash('sha256').update(raw).digest('hex')
const specs=[
  {id:'weapon.yardSwordBench',reach:2.25,shape:'cone',size:.45,contact:'yard.slice',landing:.16},
  {id:'weapon.yardSpearBench',reach:2.6,shape:'lane',size:.035,contact:'yard.thrust',landing:.20},
]
const slots=['sword','spear']
const rowFlag=id=>'yard.hit.'+id
const contacts=specs.map(s=>[{
  lane:'primary',heavy:false,cooldown:.42,shape:s.shape,reach:s.reach,size:s.size,
  height:0,allowance:0,lands:[s.landing],show:.39,reports:false,
  hits:[{source:'owner',damage:0,tags:[],moveId:s.contact,copyVectors:false,copyTags:false,reactions:[]}],
}])
const input=parseWorldTargets({spots:[],targets:fixtures.map(({id,at})=>{
  const i=id.startsWith('sword')?0:1, s=specs[i]
  return {id,weapon:s.id,at,radius:i===0?0:.405,needs:{none:[rowFlag(id)]},
    scan:i===0?{kind:'cone',reach:s.reach,halfAngle:s.size,selection:'all'}:{kind:'ray',selection:'nearest'},
    rules:[{move:s.contact,contact:0,caught:'if-applied',effects:[{kind:'flag',id:rowFlag(id)}]}]}
})})
const content={items:{rows:specs.map((s,i)=>({kind:'weapon',id:s.id,contacts:contacts[i]}))},
  quests:{flags:fixtures.map(x=>rowFlag(x.id))}}
assert.deepEqual(worldTargetRules(input,content),[])

function replay(withControls) {
  const host=new SimHost({version:SIM_API_VERSION,id:'w3a-six-target-yard-bench',seed:25,
    ground:{size:500,height:0},player:{at:{x:-30,y:.23,z:80},yaw:Math.PI,speed:4.3},
    entities:[],quests:[],weapon:{id:'w3a-unused-simple-weapon',damage:0}},{rapier:R,ground:false})
  const player=host.players.get('actor.player')
  const world=host.physics.world
  try {
    for (const c of parts) world.createCollider(R.ColliderDesc.trimesh(
      new Float32Array(c.vertices),new Uint32Array(c.triangles)).setCollisionGroups(groups('WORLD')))
    let wanted=0, stream=[], pitch=0, frames=[], attempts=[], samples=[], airTicks=0, routeMetres=0
    const loadout=bindNativeLoadout(host,{slots:[0,1],initial:0,lower:0,raise:0},{
      owned:()=>true,step:{id:'yardBench.loadout',phase:'beforeBodies',pick:()=>wanted},
    })
    const dispatcher=new WorldTargetHost(input,{flags:host.flags,interactions:new Map(),hints:{show(){}}})
    for(const [i,s] of specs.entries()){
      const native={step:'yardBench.'+slots[i],input:{attack:1,aimActor:'yardBench.aim',scripts:[]},
        mode:'timed',eye:1.54,pitchLimit:1.42,zeroAim:'refuse',body:'none',liveTargetsOnly:true,
        commandsAfterCool:true,actions:[{action:1,move:0,aim:'selected',hook:null}],
        continuation:{encoding:'object',fields:['primary','time','heavy','landed','target','world','direction']
          .map(source=>({key:source,source}))}}
      const melee=installNativeMelee(host,{id:s.id,contacts:contacts[i]},native,{
        inputCommands:()=>stream,enabled:()=>loadout.live(i),
      })
      melee.family.bindWorldTargets(dispatcher)
    }
    const flags=()=>host.flags.all
    const tick=(moveX=0,moveZ=0,yaw=player.yaw,swing=false)=>{
      const before=player.position.clone()
      stream=swing?[{kind:'player',swing:true,pitch}]:[]
      host.step(new Map([[player.id,{moveX,moveZ,yaw}]]))
      if(host.state.tick>40){
        if(!player.fall.grounded)airTicks++
        routeMetres+=Math.hypot(player.position.x-before.x,player.position.z-before.z)
      }
      if(host.state.tick%6===0)frames.push([host.state.tick,...player.position.toArray(),wanted,flags().length])
    }
    const idle=(ticks,yaw)=>{for(let n=0;n<ticks;n++)tick(0,0,yaw)}
    const walk=(x,z)=>{
      for(let n=0;n<440;n++){
        const dx=x-player.position.x,dz=z-player.position.z,d=Math.hypot(dx,dz)
        if(d<.065)return
        const speed=Math.min(1,d*60/4.3)
        tick(dx/d*speed,dz/d*speed,Math.atan2(-dx,-dz))
      }
      throw new Error('Blocked route '+JSON.stringify([x,z,player.position.toArray()]))
    }
    const swing=(target,name,kind)=>{
      const [x,y,z]=target
      const dx=x-player.position.x,dz=z-player.position.z
      const yaw=Math.atan2(-dx,-dz)
      pitch=Math.atan2(y-player.position.y-1.54,Math.hypot(dx,dz))
      idle(28,yaw)
      const start=host.state.tick, before=flags().length
      tick(0,0,yaw,true)
      let landedAt=null
      for(let k=0;k<25;k++){
        if(flags().length!==before&&landedAt===null)landedAt=host.state.tick
        tick(0,0,yaw)
      }
      attempts.push({name,kind,slot:slots[wanted],gained:flags().length-before,
        orderedFlags:[...flags()],swingTick:start+1,landingTick:landedAt,origin:player.position.toArray(),aim:target})
      return flags().length-before
    }
    idle(55,Math.PI)
    assert(player.fall.grounded)
    const started=host.state.tick
    for(const [i,f] of fixtures.entries()){
      const [x,y,z]=f.at
      // Walk between rows along an unobstructed central service aisle, not
      // straight through a target's fitted foot or native terrain.
      if(i===3){walk(-33,84.20);walk(-33,101.8);wanted=1}
      const stop=z-(i<3?1.42:1.96)
      const approach=i===0?x-1.0:i===2?x-1.38:x
      walk(approach,stop);idle(6,Math.PI)
      samples.push({id:f.id,feet:player.position.toArray(),grounded:player.fall.grounded})
      if(withControls&&i===0){
        assert.equal(swing([x+2.6,y,z],f.id,'off-axis'),0)
        wanted=1
        assert.equal(swing(f.at,f.id,'wrong weapon'),0)
        wanted=0
      }
      if(withControls&&i===3) assert.equal(swing([x+.58,y,z],f.id,'outside bore'),0)
      assert.equal(swing(f.at,f.id,'center'),1)
      if(withControls&&i===0) assert.equal(swing(f.at,f.id,'duplicate'),0)
    }
    assert.deepEqual(flags(),fixtures.map(f=>rowFlag(f.id)))
    assert.equal(airTicks,0)
    return {started,finished:host.state.tick,routeMetres,airTicks,attempts,samples,frames}
  }finally{host.dispose()}
}
const run=replay(false), checks=replay(true)
assert.deepEqual(run,replay(false))
assert.deepEqual(checks,replay(true))
assert(run.attempts.every((a,i)=>a.gained===1&&a.landingTick-a.swingTick===(i<3?9:12)),run.attempts)
writeFileSync(out,JSON.stringify({engine:'0.1.44',format:'0.43.0',geometrySha256,
  colliderMeshes:parts.length,triangles:parts.reduce((a,c)=>a+c.triangles.length/3,0),
  terrain:'bounded reimport geometry, stock capsule; no synthetic support or teleports',fixtures,
  repeatExactly:true,negativeControls:checks.attempts.filter(a=>a.kind!=='center'),...run},null,2)+'\n')
console.log(JSON.stringify({triangles:parts.reduce((a,c)=>a+c.triangles.length/3,0),attempts:run.attempts.map(({name,kind,gained})=>[name,kind,gained]),air:run.airTicks,ticks:run.finished-run.started}))
