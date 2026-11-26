// Verify the exported weights work with the actual Three.js loader and mixer.
import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const threeRoot=dirname(dirname(req.resolve('three')))
const {AnimationMixer,Vector3}=await import(pathToFileURL(join(threeRoot,'build/three.module.js')).href)
const {GLTFLoader}=await import(pathToFileURL(join(threeRoot,'examples/jsm/loaders/GLTFLoader.js')).href)
const raw=readFileSync(process.argv[2])
const gltf=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
assert.equal(gltf.animations.length,1)
const clip=gltf.animations[0]
assert.equal(clip.name,'Avenue pennants - breeze')
assert.equal(clip.duration,3)
const fixed=[],moving=[]
gltf.scene.traverse(o=>{if(o.isMesh)(o.morphTargetInfluences?moving:fixed).push(o)})
assert.equal(fixed.length,1)
assert.equal(moving.length,4)
const snapshot=(meshes)=>meshes.map(o=>{
  const v=new Vector3()
  return Array.from({length:o.geometry.getAttribute('position').count},(_,i)=>o.getVertexPosition(i,v).clone())
})
const delta=(a,b)=>Math.max(...a.map((points,i)=>Math.max(...points.map((p,j)=>p.distanceTo(b[i][j])))))
const mixer=new AnimationMixer(gltf.scene)
mixer.clipAction(clip).play()
mixer.setTime(0)
const frames=[snapshot(moving)],anchor=snapshot(fixed)
mixer.setTime(1.5);frames.push(snapshot(moving))
assert.deepEqual(snapshot(fixed),anchor)
mixer.setTime(3);frames.push(snapshot(moving))
assert.deepEqual(snapshot(fixed),anchor)
const halfCyclePeak=delta(frames[0],frames[1])
assert(halfCyclePeak>.33&&halfCyclePeak<.37,halfCyclePeak)
assert(delta(frames[0],frames[2])<1e-7)
console.log(JSON.stringify({duration:clip.duration,staticMeshes:fixed.length,movingMeshes:moving.length,halfCyclePeakM:halfCyclePeak}))
