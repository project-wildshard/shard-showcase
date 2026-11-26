// W4b bench only: native picker + admitted latched lever row, local gate bridge.
import assert from 'node:assert/strict'
import { compileQuestTable } from '@wildshard/format/interactTable'
const p=(x,y,z)=>({x,y,z})
export const stand=p(-30,.04,200.55)
export const spot={...p(stand.x,1.64,stand.z+.15),radius:2.5}
const id='w4b.release'
const actorId='w4b.interaction'
const act=1, resetAct=2
const resetDef={id:'w4b.reset',kind:'lever',label:'Reset skittles',latch:true,reach:spot.radius,showWhen:{all:['skittles:result']}}
const def={id,kind:'lever',label:'Release four balls',latch:true,reach:spot.radius}
const go=compileQuestTable({rows:[def]},[{id,act}])
let SimHost,SIM_API_VERSION,InteractionRules,installInteractionRows,bindInteractionState,createHeadlessPromptPicker,groups
export async function init(at){
  ;({SimHost}=await at('src/server/engine/sim.ts'))
  ;({SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts'))
  ;({InteractionRules,installInteractionRows,createHeadlessPromptPicker}=await at('src/shared/game/quest/interactionRows.ts'))
  ;({bindInteractionState}=await at('src/shared/engine/world/interact/flags.ts'))
  ;({groups}=await at('src/shared/engine/physics/groups.ts'))
}
export function make(R,exercise){
  const resetMode=exercise==='replay'
  const playing=exercise==='press'||resetMode
  const sim=new SimHost({version:SIM_API_VERSION,id:'w4b-release-bench',seed:41,ground:{size:500,height:.04},
    player:{at:p(-36,.075,202.28),yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},
    {rapier:R,ground:false})
  const player=sim.players.get('actor.player')
  const rules=new InteractionRules(sim.flags,resetMode?compileQuestTable({rows:[def,resetDef]},[{id,act},{id:resetDef.id,act:resetAct}]):go)
  const row=bindInteractionState(def,sim.flags)
  const prompts=[{id,act,position:spot,get radius(){return row.promptRadius()},sight:{slack:.10}}]
  const reset=bindInteractionState(resetDef,sim.flags)
  const spots={[id]:spot}
  if(resetMode){
    prompts.push({id:resetDef.id,act:resetAct,position:spot,get radius(){return reset.promptRadius()},sight:{slack:.10}})
    spots[resetDef.id]=spot
  }
  const picker=createHeadlessPromptPicker(sim)
  let commands=[], count=0
  installInteractionRows(sim,rules,{actorId,stepId:'w4b-press',spots,prompts,commands:()=>commands,done:()=>count++})
  const grounded=()=>assert(player.fall.grounded)
  const press=(step,value)=>{commands=[{actorId,value}];step();commands=[];grounded()}
  const picked=()=>picker.pick(prompts,player.position)?.id??null
  return {
    result:()=>sim.flags.set('skittles:result'),
    earlyReset:step=>{press(step,resetAct);assert(!sim.flags.has(reset.lever));assert.equal(picked(),null)},
    reset:step=>{
      assert.equal(picked(),resetDef.id)
      press(step,resetAct)
      assert(sim.flags.has(reset.lever))
      assert.equal(picked(),null)
      sim.flags.clear('skittles:result')
      sim.flags.clear(reset.lever)
    },
    duringReset:step=>{assert.equal(picked(),null);press(step,act);assert.equal(count,2)},
    rearm:()=>sim.flags.clear(row.lever),
    replay:step=>{assert.equal(picked(),id);press(step,act);assert(sim.flags.has(row.lever))},
    sim,on:()=>sim.flags.has(row.lever), transitions:()=>count,
    setup:W=>{
      // Collision of the stand below its world interaction point; opt-in control includes opaque wall.
      const coll=desc=>W.createCollider(desc.setCollisionGroups(groups('WORLD')))
      coll(R.ColliderDesc.cuboid(.67,.51,.5).setTranslation(stand.x,stand.y+.51,stand.z))
      if(exercise==='blocked-sight')
        coll(R.ColliderDesc.cuboid(1.55,.91,.08).setTranslation(stand.x,.95,stand.z+.94))
    },
    approach:step=>{
      const feet=()=>player.position.toArray().map(x=>+x.toFixed(5))
      const move=new Map([[player.id,{moveX:1,moveZ:0,yaw:0}]])
      const fire=()=>press(step,act)
      assert.equal(picker.pick(prompts,player.position),undefined)
      const start=feet()
      fire()
      assert.equal(count,0,'A distant press cannot pull the lever')
      for(let i=0;i<86;i++){step(move);assert(player.fall.grounded)}
      const arrived=feet()
      assert(Math.abs(arrived[0]-stand.x)<.24,JSON.stringify(arrived))
      assert(Math.hypot(arrived[0]-spot.x,arrived[1]+1.68-spot.y,arrived[2]-spot.z)<spot.radius)
      const picked=picker.pick(prompts,player.position)?.id??null
      assert.equal(picked,exercise==='blocked-sight'?null:id)
      const input=exercise==='no-input'?()=>step():fire
      input()
      assert.equal(count,playing?1:0)
      input()
      assert.equal(count,playing?1:0)
      if(playing)assert.equal(picker.pick(prompts,player.position),undefined)
      return {start,arrived,picked,groundedWalkTicks:86,farPressRejected:true,
        ...(playing?{repeatPressRejected:true}:{})}
    }
  }
}
