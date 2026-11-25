import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { Box3 } from 'three'

const dir = process.argv[2]
const asset = new URL('../../../public/assets/wildshard-art/', import.meta.url)
const base = 'wsc-gear-001-sword.glb'
const variants = ['e8e-sword-warden-finish.glb','e8e-sword-hot-mess-finish.glb']
async function load(file) {
  const r = await readFile(file)
  const gltf = await new GLTFLoader().parseAsync(r.buffer.slice(r.byteOffset,r.byteOffset+r.byteLength),'')
  assert.equal(gltf.scene.children.length,1)
  assert.equal(gltf.animations.length,0)
  const pivot = gltf.scene.children[0]
  const pieces = new Map()
  pivot.traverse(o=>{if(o.isMesh) pieces.set(o.material.name,{geometry:o.geometry,material:o.material})})
  const { min,max } = new Box3().setFromObject(pivot)
  return { pivot, pieces, min, max }
}
const donor = await load(new URL(base,asset))
assert.equal(donor.pieces.size,7)
for(const name of variants){
  const v=await load(dir?dir+'/'+name:new URL(name,asset))
  assert.equal(v.pivot.userData.name,donor.pivot.userData.name)
  assert.deepEqual(v.pivot.position,donor.pivot.position)
  assert.deepEqual(v.pivot.rotation.toArray(),donor.pivot.rotation.toArray())
  assert.deepEqual(v.pivot.scale,donor.pivot.scale)
  assert.deepEqual(v.min,donor.min)
  assert.deepEqual(v.max,donor.max)
  assert.deepEqual([...v.pieces.keys()],[...donor.pieces.keys()])
  let count=0, changed=0
  for(const [n,ref] of donor.pieces) {
    const p=v.pieces.get(n)
    assert.deepEqual(p.geometry.index.array,ref.geometry.index.array)
    for(const a of Object.keys(ref.geometry.attributes)){
      assert.deepEqual(p.geometry.attributes[a].array,ref.geometry.attributes[a].array)
    }
    count+=p.geometry.index.count/3
    const props=m=>[m.color.toArray(),m.emissive.toArray(),m.roughness,m.metalness]
    const diff=JSON.stringify(props(p.material))!==JSON.stringify(props(ref.material))
    assert.equal(diff,!/leather/.test(n))
    if(diff)changed++
  }
  assert.equal(changed,5);assert.equal(count,660)
}
console.log(JSON.stringify({sameBounds:true,samePivot:true,piecesEach:7,trianglesEach:660,changedNamedMaterialsEach:5,untouchedWrapsEach:2}))
