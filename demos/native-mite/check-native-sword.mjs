import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { dirname, join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const input=process.argv[2]
assert(input,'Pass the built native mite-calibration folder')
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=dirname(req.resolve('@wildshard/engine/package.json'))
assert.equal(JSON.parse(await readFile(join(engine,'package.json'),'utf8')).version,'0.1.44')
await import(pathToFileURL(join(engine,'scripts/sim-node-loader.mjs')).href)
const load=name=>import(pathToFileURL(req.resolve('@wildshard/engine/'+name)).href)
const {openWorld}=await load('host/openWorld')
const {loadHeadlessFolder}=await load('host/headlessFolder')
const {folderClosureFile}=await load('game/shardfile/shardFolder')
const {loadRapier}=await load('physics/rapier')
const {questBooks}=await load('quest/players')
const {declaredKitSlots}=await import(pathToFileURL(join(engine,'src/shared/game/shardfile/items.ts')).href)
const {creatureClipName}=await import(pathToFileURL(join(engine,'src/shared/game/shardfile/creatureClipChoice.ts')).href)
const {parseSkinFile}=await import(pathToFileURL(req.resolve('@wildshard/format/skinAssets')).href)
const product=await loadHeadlessFolder(input),shard=product.shardfile
const refs=[...shard.files.map(f=>f.hash),...shard.requires.commons.map(h=>'commons:'+h)]
const assets=new Map(await Promise.all(refs.map(async h=>[h,await folderClosureFile(product,h)])))
const look=shard.rows.looks.find(row=>row.species==='crate-mite')
assert.equal(look?.recipe,'platform.skin')
const {row}=parseSkinFile(assets.get(look.parameters.skin))
const clips=new Set(row.rig.clips)
const selection=Object.fromEntries(['crate-mite.bite','crate-mite.overclock'].map(id=>[id,creatureClipName('attack',look.animation.clipMap,clips,{id})]))
assert.deepEqual(selection,{'crate-mite.bite':'attack.bite','crate-mite.overclock':'attack.overclock'})
assert.equal(creatureClipName('die',look.animation.clipMap,clips),'die')
const rapier=await loadRapier(await readFile(req.resolve('@dimforge/rapier3d-simd/rapier_wasm3d_bg.wasm')))
const world=await openWorld({shard,assets,product,rapier},{room:true})
const host=world.host,id='actor.player',mob='crate-mite:1'
const player=host.players.get(id),actor=host.entities.get(mob)
let seq=0
const slots=[...declaredKitSlots(shard.items.rows).keys()]
const wire=(attack)=>world.step([{client:1,player:id,still:false,extra:null,acts:[],
 command:{seq:++seq,viewTick:0,steer:{keyX:0,keyY:0,stickX:0,stickY:0},yaw:0,pitch:0,buttons:0,...(attack?{attack}:{})}}])
function standAndAim(){
 player.position.set(actor.position.x,actor.position.y,actor.position.z+1.44)
 player.motor.resetAt(player.position)
 const at={x:0,y:actor.dims.bodyY*actor.scale-1.68,z:-1.44},l=Math.hypot(at.x,at.y,at.z)
 return {aim:{origin:{x:player.position.x,y:player.position.y+1.68,z:player.position.z},
  direction:{x:at.x/l,y:at.y/l,z:at.z/l}}}
}
try{
 assert(player&&actor)
 assert.equal(shard.items.loadout.primary,'weapon.sword-iron')
 assert.equal(slots[player.held],'weapon.sword-iron','Native player must actually be holding iron sword')
 const sword=shard.items.rows.find(row=>row.id==='weapon.sword-iron')
 assert(sword?.kind==='weapon')
 const hp=[actor.hp],deaths=[]
 host.events.on('actor.died',({actor:dead,req})=>{
  if(dead.id===mob)deaths.push({source:req?.source?.id,move:req?.moveId})
 },host.scope)
 standAndAim();wire()
 for(let i=0;i<3;i++){
  assert.equal(slots[player.held],sword.id)
  wire(standAndAim());hp.push(actor.hp)
  for(let j=0;j<42;j++)wire()
 }
 assert.equal(hp[0]-hp[1],sword.light.damage,'First HP loss must be the declared iron sword light damage')
 assert(hp[1]>hp[2]&&hp[2]>hp[3],'All sword strikes must damage the Mite')
 assert.equal(actor.alive,false)
 assert.deepEqual(deaths,[{source:id,move:sword.light.id}])
 const flags=questBooks(host).of(id).flags
 const credited=[...flags.all].some(flag=>flag.endsWith(mob))
 assert(credited,'Player must be credited for the Mite kill')
 console.log(JSON.stringify({held:slots[player.held],hp,death:deaths[0],killCredit:credited,selectedAttackClips:selection,ticks:host.state.tick}))
}finally{world.dispose()}
