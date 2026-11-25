import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {AnimationMixer} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'

const ext='KHR_materials_variants'
const ref=new URL('../../public/assets/wildshard-art/wsc-actor-001-crate-mite-rig-yard.glb',import.meta.url)
async function load(path){
  const b=readFileSync(path)
  return new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.length),'')
}
const [stock,alt]=await Promise.all([load(ref),load(process.argv[2])])
assert.deepEqual(alt.parser.json.extensions[ext].variants.map(v=>v.name),['Uncommon Steel','Rare Gold Stencil'])
assert.deepEqual(
  alt.animations.map(c=>[c.name,c.duration,c.tracks.length]),
  stock.animations.map(c=>[c.name,c.duration,c.tracks.length]))
const skins=object=>{
  const out=[]
  object.scene.traverse(m=>{if(m.isSkinnedMesh)out.push(m)})
  return out
}
const rig=skins(alt), original=skins(stock)
assert.equal(rig.length,11)
assert(rig.every(m=>m.skeleton.bones.length===7))
assert.deepEqual(rig.map(s=>s.geometry.index.count),original.map(s=>s.geometry.index.count))
const base=rig.map(m=>m.material)
const p=alt.parser, presets=[]
for(const index of [0,1]){
  const applied=[]
  for(const [i,m] of rig.entries()){
    const binding=p.associations.get(m)
    const primitive=p.json.meshes[binding.meshes].primitives[binding.primitives]
    const mapping=primitive.extensions?.[ext]?.mappings.find(x=>x.variants.includes(index))
    const prototype=mapping?await p.getDependency('material',mapping.material):base[i]
    const chosen=mapping?prototype.clone():base[i]
    assert.equal(prototype.name,preName(mapping,i))
    m.material=chosen
    if(mapping)applied.push(chosen.name)
    if(base[i].name.includes('lens'))assert.equal(chosen,base[i])
  }
  assert.equal(applied.length,4)
  presets.push(applied)
}
function preName(mapping,i){return mapping?p.json.materials[mapping.material].name:base[i].name}
rig.forEach((m,i)=>m.material=base[i])
assert(rig.every((m,i)=>m.material===base[i]))

const baseline=original[0].skeleton.bones.map(b=>b.matrixWorld.toArray())
let poseCount=0
for(const clip of stock.animations){
  const stateA=new AnimationMixer(stock.scene),stateB=new AnimationMixer(alt.scene)
  const other=alt.animations.find(x=>x.name===clip.name)
  stateA.clipAction(clip).play();stateB.clipAction(other).play()
  for(const elapsed of [.07,.23,.61]){
    for(const mix of [stateA,stateB])mix.setTime(clip.duration*elapsed)
    for(const gltf of [stock,alt])gltf.scene.updateMatrixWorld(true)
    const pose=original[0].skeleton.bones.map(b=>b.matrixWorld.toArray())
    assert.deepEqual(rig[0].skeleton.bones.map(b=>b.matrixWorld.toArray()),pose)
    assert(pose.some((b,i)=>b.some((v,j)=>Math.abs(v-baseline[i][j])>1e-6)) || clip.name==='sleep')
    poseCount++
  }
  stateA.stopAllAction();stateB.stopAllAction()
}
console.log(JSON.stringify({skinnedPrimitives:rig.length,joints:7,clipCount:stock.animations.length,
  exactAnimationSamples:poseCount,changedMaterials:presets,lensUntouched:true,canRestoreDefault:true},null,2))
