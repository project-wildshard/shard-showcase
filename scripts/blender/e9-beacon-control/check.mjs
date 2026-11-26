import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { resolve, join, dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const root=process.env.WSC_NODE_PROJECT
const req=createRequire(root ? join(resolve(root),'package.json') : import.meta.url)
const three=dirname(req.resolve('three'))
const { AnimationMixer, LoopOnce, Vector3, Quaternion }=await import(pathToFileURL(join(three,'three.module.js')))
const { GLTFLoader }=await import(pathToFileURL(join(three,'../examples/jsm/loaders/GLTFLoader.js')))
const [asset, receipt]=process.argv.slice(2)
assert(asset&&receipt,'Pass GLB and proof JSON paths')
const bytes=readFileSync(asset), proof=JSON.parse(readFileSync(receipt))
assert.equal(createHash('sha256').update(bytes).digest('hex'),proof.sha256)
const gltf=await new GLTFLoader().parseAsync(Uint8Array.from(bytes).buffer,'')
assert.equal(gltf.animations.length,1)
const [clip]=gltf.animations
assert.equal(clip.name,proof.clip)
assert(Math.abs(clip.duration-proof.seconds)<1e-5)
const scene=gltf.scene
const pivot=scene.getObjectByName('BeaconControlPivot')
const housing=scene.getObjectByName('BeaconControlHousing')
const lens=scene.getObjectByName('BeaconControlStatusLens')
const grip=scene.getObjectByName('BeaconControlHandle')
assert(pivot&&housing&&lens&&grip&&grip.parent===pivot)
assert.equal(clip.tracks.length,1)
assert.equal(clip.tracks[0].name,pivot.name+'.quaternion')
const mixer=new AnimationMixer(scene), action=mixer.clipAction(clip)
action.setLoop(LoopOnce,1);action.clampWhenFinished=true
action.play();mixer.setTime(0);scene.updateMatrixWorld(true)
const q0=pivot.getWorldQuaternion(new Quaternion()), p0=pivot.getWorldPosition(new Vector3())
const wall=housing.matrixWorld.clone(), fixed=lens.matrixWorld.clone()
let old=0
for(let i=0;i<=128;i++){
  mixer.setTime(clip.duration*i/128);scene.updateMatrixWorld(true)
  assert(pivot.getWorldPosition(new Vector3()).distanceTo(p0)<1e-8)
  assert(housing.matrixWorld.equals(wall)&&lens.matrixWorld.equals(fixed))
  const d=q0.angleTo(pivot.getWorldQuaternion(new Quaternion()))
  assert(d>=old-1e-7)
  old=d
}
assert(Math.abs(old*180/Math.PI-proof.degrees)<.005)
console.log(`GLTFLoader: 129 monotonic poses, stationary pivot/housing/status lens, ${proof.degrees}° in ${proof.seconds}s`)
