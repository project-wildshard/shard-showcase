import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const dir=resolve(process.argv[2])
const receipt=JSON.parse(readFileSync(join(dir,'geometry.json')))
const req=createRequire(process.env.WSC_NODE_PROJECT?
  join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const p=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(p)).version,'0.1.44')
const at=x=>import(pathToFileURL(join(dirname(p),x)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),
  'rapier_wasm3d_bg.wasm')))
const three=dirname(req.resolve('three'))
const {Vector3,Raycaster}=await import(pathToFileURL(join(three,'../build/three.module.js')))
const {GLTFLoader}=await import(pathToFileURL(join(three,'../examples/jsm/loaders/GLTFLoader.js')))
const assets=new URL('../../public/assets/wildshard-art/',import.meta.url)
const names=['wsc-prop-065-keycard-shed','wsc-kit-006-foreman-desk','wsc-kit-006-vault-keycard']
async function model(name){
  const file=name?new URL(name+'.glb',assets):join(dir,'e5b-keycard-shed-open.glb')
  const raw=readFileSync(file)
  assert.equal(createHash('sha256').update(raw).digest('hex'),name?receipt.source_sha256[name]:receipt.sha256)
  return (await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')).scene
}
const [closed,desk,card,open]=await Promise.all([...names,null].map(model))
desk.position.fromArray(receipt.desk_gltf_translation_m)
card.position.fromArray(receipt.card_gltf_translation_m)
// Each checked collider is the actual imported render geometry. Room placement
// and floor are local; vegetation, alarm logic and patrols are absent.
function geometry(obj){
  obj.updateMatrixWorld(true)
  const v=[],ids=[],tmp=new Vector3()
  obj.traverse(o=>{
    if(!o.isMesh)return
    const off=v.length/3,positions=o.geometry.getAttribute('position'),index=o.geometry.index
    for(let i=0;i<positions.count;i++){
      tmp.fromBufferAttribute(positions,i).applyMatrix4(o.matrixWorld);v.push(...tmp.toArray())
    }
    for(let i=0;i<(index?.count??positions.count);i++)ids.push(off+(index?.getX(i)??i))
  })
  return [new Float32Array(v),new Uint32Array(ids)]
}
const packed=[closed,open,desk].map(geometry)
assert.equal(packed[1][1].length/3,receipt.triangles)
card.updateMatrixWorld(true)
const contact=new Vector3().fromArray(receipt.card_gltf_translation_m).add(new Vector3(0,.008,0))
const round=v=>+v.toFixed(6)
function trial(offset,speed,useOpen,record=false){
  const sim=new SimHost({version:SIM_API_VERSION,id:'keycard-shed-rehearsal',seed:49,
    ground:{size:500,height:0},player:{at:{x:.75+offset,y:.039,z:3.5},yaw:0,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled',damage:0}},{rapier:R,ground:false})
  const ply=sim.players.get('actor.player'),w=sim.physics.world
  assert.equal(ply.motor.opts.radius,.38)
  const make=d=>w.createCollider(d.setCollisionGroups(groups('WORLD')))
  make(R.ColliderDesc.cuboid(12,.30,12).setTranslation(0,-.30,0))
  for(const a of [packed[useOpen?1:0],packed[2]])make(R.ColliderDesc.trimesh(...a))
  try{
    for(let i=0;i<24;i++)sim.step()
    const frames=[]
    let airborne=0
    const foot=()=>ply.position.toArray().map(round)
    function go(x,z,cap=170){
      for(let j=0;j<cap;j++){
        const dx=x-ply.position.x,dz=z-ply.position.z,len=Math.hypot(dx,dz)
        if(len<.10)return true
        sim.step(new Map([[ply.id,{moveX:speed*dx/len,moveZ:speed*dz/len,yaw:0}]]))
        airborne+=Number(!ply.fall.grounded)
        if(record&&sim.state.tick%4===0)frames.push(foot())
      }
      return false
    }
    const crossed=go(.75+offset,.52),threshold=foot()
    const approached=crossed&&go(.65,-.42)
    const atDesk=foot(),airIn=airborne
    const eye=new Vector3(atDesk[0],atDesk[1]+1.59,atDesk[2])
    const delta=contact.clone().sub(eye),len=delta.length()
    const ray=new Raycaster(eye,delta.normalize(),0,len+.03)
    const hits=ray.intersectObjects([useOpen?open:closed,desk,card],true)
    let hit=hits[0]?.object
    while(hit&&hit!==card)hit=hit.parent
    const seen=hit===card
    const back=approached&&go(.75+offset,.51)&&go(.75+offset,3.0)
    return {offset,speed,useOpen,crossed,threshold,approached,atDesk,cardRayM:round(len),
      cardVisible:seen,airIn,back,airOut:airborne-airIn,last:foot(),...(record?{frames}:{})}
  }finally{sim.dispose()}
}
const cases=[-.145,0,.145].flatMap(o=>[.62,1].map(s=>trial(o,s,true)))
const run=trial(0,1,true,true),control=trial(0,1,false,true)
assert.deepEqual(run,trial(0,1,true,true))
console.log(cases.map(c=>[c.offset,c.speed,c.cardRayM,c.cardVisible,c.airIn,c.airOut,c.back]))
assert(cases.every(t=>t.crossed&&t.approached&&t.cardVisible&&t.cardRayM<1.75&&t.airIn===0&&t.airOut===0&&t.back))
assert(!control.crossed&&control.threshold[2]>1.4&&!control.cardVisible)
const {frames:_,...c}=control
const result={scope:'Exact render meshes; scripted local approach and round trip; no pickup, stealth, patrol, unlock, install or phone test.',geometry:receipt,cases,control:c}
writeFileSync(join(dir,'walk.json'),JSON.stringify(result,null,2)+'\n')
writeFileSync(join(dir,'trace.json'),JSON.stringify({...result,run,control})+'\n')
