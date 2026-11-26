import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const three=dirname(dirname(req.resolve('three')))
const {AnimationMixer,Vector3,LoopOnce}=await import(pathToFileURL(join(three,'build/three.module.js')).href)
const {GLTFLoader}=await import(pathToFileURL(join(three,'examples/jsm/loaders/GLTFLoader.js')).href)
const raw=readFileSync(process.argv[2])
const gltf=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
assert.equal(gltf.animations.length,1)
const [clip]=gltf.animations
assert.equal(clip.name,'Roof finish - acknowledge')
assert(Math.abs(clip.duration-.70)<1e-5)
const meshes=[]
gltf.scene.traverse(o=>{if(o.isMesh)meshes.push(o)})
assert.equal(meshes.length,1)
const [mesh]=meshes
const mixer=new AnimationMixer(gltf.scene)
const a=mixer.clipAction(clip)
a.clampWhenFinished=true
a.setLoop(LoopOnce,1).play()
const probe=new Vector3()
const radius=()=>{
  let outer=0
  for(let i=0;i<mesh.geometry.attributes.position.count;i++){
    mesh.getVertexPosition(i,probe)
    assert(Math.abs(probe.y)<1e-6)
    outer=Math.max(outer,Math.hypot(probe.x,probe.z))
  }
  return outer
}
const hidden=radius()
mixer.setTime(5/60)
const firstPeak=radius()
mixer.setTime(24/60)
const secondPeak=radius()
mixer.setTime(.701)
const ended=radius()
assert(Math.abs(hidden-.78)<1e-6&&Math.abs(ended-hidden)<1e-6)
assert(firstPeak>.897&&firstPeak<.899&&Math.abs(secondPeak-firstPeak)<1e-6)
console.log(JSON.stringify({duration:clip.duration,hidden,firstPeak,secondPeak,ended}))
