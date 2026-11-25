import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {AnimationMixer,Box3,LoopOnce,Quaternion,Raycaster,Vector3} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
const assets=new URL('../public/assets/wildshard-art/',import.meta.url)
const receipt=JSON.parse(readFileSync(new URL('./layouts/e1d-band1-scrip-opening-proof.json',import.meta.url)))
async function get(name,sha){
  const b=readFileSync(new URL(name+'.glb',assets))
  assert.equal(createHash('sha256').update(b).digest('hex'),sha)
  return [await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),''),b.byteLength]
}
const [old]=await get('e1d-band1-scrip-chest',receipt.untouched_closed_sha256);
const [pkg,bytes]=await get('e1d-band1-scrip-opening',receipt.new_sha256)
assert.equal(bytes,receipt.bytes)
assert.equal(old.animations.length,0)
const [clip]=pkg.animations
assert.equal(pkg.animations.length,1)
assert.equal(clip.name,receipt.clip)
assert.ok(Math.abs(clip.duration-.9)<1e-6)
assert.equal(clip.tracks.length,1)
const shell=pkg.scene.getObjectByName('E1d_ScripChest_FixedShell')
const lid=pkg.scene.getObjectByName('E1d_ScripChest_Lid')
assert.ok(shell&&lid)
let tri=0
pkg.scene.traverse(o=>{
  assert.ok(!o.isLight&&!o.isSkinnedMesh&&!o.isCamera)
  if(o.isMesh)tri+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3
})
assert.equal(tri,receipt.triangles)
const mixer=new AnimationMixer(pkg.scene)
const action=mixer.clipAction(clip)
action.setLoop(LoopOnce,1);action.clampWhenFinished=true;action.play()
function sample(t){
  if(action.paused)action.paused=false
  mixer.setTime(t)
  pkg.scene.updateMatrixWorld(true)
}
sample(0)
const retained=new Box3().setFromObject(old.scene), closed=new Box3().setFromObject(pkg.scene)
assert.ok(retained.min.distanceTo(closed.min)<2e-6&&retained.max.distanceTo(closed.max)<2e-6)
const pivot=lid.getWorldPosition(new Vector3())
assert.ok(pivot.distanceTo(new Vector3(receipt.hinge_blender_m[0],receipt.hinge_blender_m[2],-receipt.hinge_blender_m[1]))<2e-6)
const q0=lid.getWorldQuaternion(new Quaternion())
let prev=0
for(let i=0;i<=216;i++){
  sample(clip.duration*i/216)
  const angle=lid.getWorldQuaternion(new Quaternion()).angleTo(q0)*180/Math.PI
  assert.ok(angle+1e-5>=prev && angle<102.01)
  assert.ok(lid.getWorldPosition(new Vector3()).distanceTo(pivot)<1e-6)
  prev=angle
}
assert.ok(Math.abs(prev-102)<.001)
const ray=new Raycaster(new Vector3(0,1.22,0),new Vector3(0,-1,0),0,1.22)
const floor=ray.intersectObject(shell,true)[0]
assert.ok(floor&&floor.point.y>.07&&floor.point.y<.16)
assert.equal(ray.intersectObject(lid,true).length,0)
console.log(bytes,'bytes,',tri,'triangles; unchanged closed extents, 217 hinge samples and unobstructed chamber.')
