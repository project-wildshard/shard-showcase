import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [art,geo,out]=process.argv.slice(2)
const receipt=JSON.parse(readFileSync(art)), bytes=readFileSync(geo), models=JSON.parse(bytes)
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(engine)).version,'0.1.44')
const at=p=>import(pathToFileURL(join(dirname(engine),p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const {createHeadlessPromptPicker,eyeReaches}=await at('src/shared/game/quest/interactionRows.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')))
const [px,py,pz]=receipt.promptLocalXYZ
const atRock=Boolean(receipt.rock)
const prompt={id:atRock?'w9.rock.cache':'w9.oval.cache',act:1,position:{x:px,y:py,z:pz},radius:2.5,sight:{slack:.125}}
const round=n=>+n.toFixed(6)
function run(x,z,n,screen){
 const sim=new SimHost({version:SIM_API_VERSION,id:atRock?'w9-rock-cache-witness':'w9-oval-cache-witness',seed:67,ground:{size:500,height:0},
  player:{at:{x,y:.03,z},yaw:0,speed:4.3},entities:[],quests:[],weapon:{id:'disabled',damage:0}},
 {rapier:R,ground:false})
 try {
  const w=sim.physics.world
  const add=d=>w.createCollider(d.setCollisionGroups(groups('WORLD')))
  add(R.ColliderDesc.cuboid(9,.5,12).setTranslation(0,-.5,0))
  for(const a of ['chest',...(screen?['screen']:[])]){
    const [v,f]=models[a]
    const idx=new Uint32Array(f.flat())
    add(R.ColliderDesc.trimesh(new Float32Array(v.flat()),idx))
  }
  const player=sim.players.get('actor.player'),picker=createHeadlessPromptPicker(sim)
  for(let i=0;i<25;i++)sim.step()
  const pick=()=>picker.pick([prompt],player.position)?.id===prompt.id
  const before=pick()
  const command=new Map([[player.id,{moveX:0,moveZ:-1,yaw:0}]])
  let airborne=0
  for(let i=0;i<n;i++){sim.step(command);airborne+=!player.fall.grounded}
  assert.equal(airborne,0)
  const reached={screen,start:[x,z],ticks:n,promptBefore:before,promptAfter:pick(),
    withinRange:eyeReaches(player.position,{...prompt.position,radius:prompt.radius}),
    airborne,feet:player.position.toArray().map(round)}
  if(atRock){
    const retreat=new Map([[player.id,{moveX:0,moveZ:1,yaw:0}]])
    let returnAir=0
    for(let i=0;i<60;i++){sim.step(retreat);returnAir+=!player.fall.grounded}
    assert.equal(returnAir,0)
    assert.ok(!pick() && player.position.z>=4.9)
    reached.retreat={ticks:60,promptAfter:pick(),airborne:returnAir,feet:player.position.toArray().map(round)}
  }
  return reached
 }finally{sim.dispose()}
}
const approaches=[-.6,0,.6].map(x=>run(x,4.9,46,true))
assert(approaches.every(r=>!r.promptBefore&&r.promptAfter&&r.withinRange&&r.feet[2]>1.55),approaches)
const stockPlayer={approaches}
if(!atRock){
 const screened=run(2.08,-.38,0,true),clear=run(...screened.start,0,false)
 assert(screened.withinRange&&clear.withinRange&&!screened.promptAfter&&clear.promptAfter,JSON.stringify({screened,clear}))
 Object.assign(stockPlayer,{screened,clear})
}
writeFileSync(out,JSON.stringify({...receipt,engine:'0.1.44',geometrySha256:createHash('sha256').update(bytes).digest('hex'),
 promptRadius:2.5,stockPlayer},null,2)+'\n')
console.table(approaches)
