import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const json=url=>JSON.parse(readFileSync(url))
const fit=json(new URL('../../project/layouts/e9-beacon-ground-control-proof.json',import.meta.url))
const config=json(new URL('./states.json',import.meta.url))
const controlFile='wsc-kit-007-storm-beacon-control.glb'
const req=createRequire(process.env.WSC_NODE_PROJECT?
  join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const p=req.resolve('@wildshard/engine/package.json')
assert.equal(json(p).version,'0.1.44')
assert.equal(json(join(dirname(req.resolve('three')),'../package.json')).version,'0.186.0')
const at=x=>import(pathToFileURL(join(dirname(p),x)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),
  'rapier_wasm3d_bg.wasm')))
const three=dirname(req.resolve('three'))
const {AnimationMixer,LoopOnce,Vector3,Raycaster,Mesh,BoxGeometry}=await import(pathToFileURL(join(three,'three.module.js')))
const {GLTFLoader}=await import(pathToFileURL(join(three,'../examples/jsm/loaders/GLTFLoader.js')))
const load=async(name,sha)=>{
  const raw=readFileSync(new URL('../../public/assets/wildshard-art/'+name,import.meta.url))
  assert.equal(createHash('sha256').update(raw).digest('hex'),sha)
  return new GLTFLoader().parseAsync(Uint8Array.from(raw).buffer,'')
}
const cases=await Promise.all(fit.placements.map(async a=>{
  const g=await load(controlFile,fit.sha256), scene=g.scene
  const charged=(await load(config.charged_insert,fit.pins[config.charged_insert])).scene
  scene.position.fromArray(a.three_xyz)
  scene.rotation.y=a.yaw_deg*Math.PI/180
  const dir=a.yaw_deg===0?1:-1
  const px=a.three_xyz[0]+(a.three_xyz[0]<170?-1:1)
  const pz=a.three_xyz[2]-dir*2
  const pedestal=new Mesh(new BoxGeometry(4,12,4))
  pedestal.position.set(px,6,pz)
  pedestal.updateMatrixWorld(true)
  charged.position.set(px,14.533658,pz)
  const lens=scene.getObjectByName(config.lens)
  assert(lens?.isMesh)
  lens.material=lens.material.clone()
  const mixer=new AnimationMixer(scene), action=mixer.clipAction(g.animations[0])
  assert.equal(g.animations[0].name,fit.clip)
  action.setLoop(LoopOnce,1)
  action.clampWhenFinished=true
  const pivot=scene.getObjectByName('BeaconControlPivot')
  const parked=pivot.quaternion.clone()
  return {a,scene,charged,dir,px,pz,pedestal,lens,pivot,parked,mixer,action}
}))
const setState=(c,state)=>{
  const e=config.states[state]
  c.lens.material.color.fromArray(e.base_linear)
  c.lens.material.emissive.fromArray(e.emission_linear)
  c.lens.material.emissiveIntensity=e.strength
  c.charged.visible=state==='lit'
}
cases.forEach(c=>setState(c,'ready'))
function eligible(c,feet){
  c.scene.updateMatrixWorld(true)
  const front=c.dir*(feet.z-c.a.three_xyz[2])
  const eye=feet.clone().add(new Vector3(0,config.eye_height_m,0))
  const delta=c.lens.getWorldPosition(new Vector3()).sub(eye)
  const length=delta.length()
  if(front<=0||length>config.reach_m||length<.001)return false
  const hit=new Raycaster(eye,delta.normalize(),0,length+.02).intersectObjects([c.pedestal,c.scene],true)[0]
  return hit?.object===c.lens
}
const sim=new SimHost({version:SIM_API_VERSION,id:'beacon-rehearsal',seed:49,
  ground:{size:500,height:0},player:{at:{x:148,y:.04,z:10},yaw:0,speed:4.3},
  entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
const player=sim.players.get('actor.player'),w=sim.physics.world
const box=(x,y,z,hx,hy,hz)=>w.createCollider(R.ColliderDesc.cuboid(hx,hy,hz).setTranslation(x,y,z).setCollisionGroups(groups('WORLD')))
box(0,-.3,0,250,.3,250)
for(const c of cases)box(c.px,6,c.pz,2,6,2)
for(const [x,z,u,v] of [[126,14,140,14],[156,14,232,14],[232,14,232,118],[126,118,232,118],[126,14,126,58],[126,74,126,118]])
  box((x+u)/2,1.3,(z+v)/2,Math.max(.30,Math.abs(u-x)/2),1.3,Math.max(.30,Math.abs(v-z)/2))
let airborne=0
const seen=new Set()
const counts=[]
const activate=(c,feet)=>{
  if(seen.has(c.a.corner)||!eligible(c,feet))return false
  seen.add(c.a.corner)
  setState(c,'lit')
  c.action.play()
  for(let i=0;i<24;i++)c.mixer.update(1/60)
  assert(c.pivot.quaternion.angleTo(c.parked)>1.91)
  assert(c.charged.visible)
  return true
}
const position=()=>new Vector3(...player.position.toArray())
function go(x,z){
  for(let n=0;n<2400;n++){
    const dx=x-player.position.x,dz=z-player.position.z,d=Math.hypot(dx,dz)
    if(d<.09)return
    sim.step(new Map([[player.id,{moveX:dx/d,moveZ:dz/d,yaw:0}]]))
    airborne+=Number(!player.fall.grounded)
  }
  assert.fail('Did not reach '+[x,z])
}
try{
  for(let i=0;i<24;i++)sim.step()
  assert(!activate(cases[0],position()))
  go(148,21)
  for(const c of cases){
    const [x,,z]=c.a.three_xyz
    go(x,z+c.dir*4)
    assert(!activate(c,position()),'far tap')
    assert(!activate(c,new Vector3(x,0,z-c.dir*1.15)),'tap through pedestal')
    go(x,z+c.dir*1.07)
    assert(activate(c,position()),'bounded tap corner '+c.a.corner)
    assert(!activate(c,position()),'repeat tap')
    counts.push(seen.size)
    assert.equal(cases.filter(x=>x.charged.visible).length,seen.size)
    go(x,z+c.dir*4)
  }
  go(130,66)
  go(122,66)
  assert.deepEqual(counts,[1,2,3,4])
  assert.equal(airborne,0)
  const report={scope:'Stock motor on original Round 5 plinth and boundary proxies; synthetic taps, no quest or live install.',
    engine:'0.1.44',three:'0.186.0',fitSha256:fit.sha256,insertSha256:fit.pins[config.charged_insert],
    entry:'north',exit:'west',corners:counts,airborne,farRejected:4,throughWallRejected:4,repeatsRejected:4,config}
  writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n')
  console.log(report)
}finally{sim.dispose()}
