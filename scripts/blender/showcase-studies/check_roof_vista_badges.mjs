import assert from 'node:assert/strict'
import {readFile} from 'node:fs/promises'
import {Box3, Vector3} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
const fallback=new URL('../../../public/assets/wildshard-art/w9b-roof-vista-badges.glb',import.meta.url)
const raw=await readFile(process.argv[2]??fallback)
const {scene,animations}=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
const parts=scene.children.sort((a,b)=>a.userData.name.localeCompare(b.userData.name))
assert.deepEqual(parts.map(o=>o.userData.name),['Vista 02 · flush badge','Vista 03 · flush badge'])
assert.equal(animations.length,0)
let tris=0
for(const o of parts){
  const box=new Box3().setFromObject(o), size=box.getSize(new Vector3())
  assert.ok(Math.abs(size.x-.57)<.00002 && Math.abs(size.z-.39)<.00002 && size.y<.063)
  assert.ok(box.min.y>=-.001 && box.min.y<.002)
  o.traverse(n=>{
    if(!n.isMesh)return
    const p=n.geometry.attributes.position, idx=n.geometry.index
    assert.ok(p.array.every(Number.isFinite) && idx.array.every(i=>i<p.count))
    tris+=idx.count/3
  })
}
console.log(JSON.stringify({badgeMeshes:parts.length,triangles:tris,bytes:raw.length,footprintMeters:[.57,.39],maximumHeightMeters:.063}))
