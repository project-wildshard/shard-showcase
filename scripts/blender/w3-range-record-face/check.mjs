import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {join} from 'node:path'
import {Box3, Vector3} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'

const staging=process.argv[2]
const dir=staging??'public/assets/wildshard-art'
const receipt=JSON.parse(readFileSync(join(staging??'project/layouts','w3a-range-record-face-proof.json'),'utf8'))
const blob=readFileSync(join(dir,'w3a-range-record-face.glb'))
assert.equal(createHash('sha256').update(blob).digest('hex'),receipt.insertSha256)
assert.equal(blob.length,receipt.bytes)
const {scene,animations}=await new GLTFLoader().parseAsync(blob.buffer.slice(blob.byteOffset,blob.byteOffset+blob.byteLength),'')
assert(!animations.length)
scene.updateMatrixWorld(true)
const full=new Box3().setFromObject(scene,true)
const unset=scene.getObjectByName(receipt.unsetNode)
assert(unset?.isMesh)
const box=new Box3().setFromObject(unset,true)
assert(box.min.x>.326 && box.max.x<.735)
assert(box.min.y>.52 && box.max.y<.84)
assert(box.min.z>.340 && box.max.z<.342)
let primitives=0,triangles=0
scene.traverse(o=>{
  assert(!o.isCamera&&!o.isLight)
  if(o.isMesh){primitives++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3}
})
assert.equal(primitives,receipt.primitives)
assert.equal(triangles,receipt.triangles)
const [lo,hi]=receipt.localBoundsBlender
const convert=(p,z)=>new Vector3(p[0],p[2],-z)
assert(full.min.distanceTo(convert(lo,hi[1]))<1e-5)
assert(full.max.distanceTo(convert(hi,lo[1]))<1e-5)
console.log(blob.length,triangles,primitives,'and independent unset values match')
