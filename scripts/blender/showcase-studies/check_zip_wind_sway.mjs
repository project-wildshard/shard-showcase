import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { AnimationMixer, LoopOnce, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
const fallback=new URL('../../../public/assets/wildshard-art/w11a-west-zip-sway.glb',import.meta.url)
const raw=await readFile(process.argv[2]??fallback)
const load=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
assert.equal(load.animations.length,1)
const [clip]=load.animations
assert.ok(Math.abs(clip.duration-5)<.00001)
assert.equal(clip.tracks.length,1)
const [m]=load.scene.children
assert.ok(m.isMesh && m.geometry.morphAttributes.position.length===2)
assert.equal(m.geometry.morphTargetsRelative,true)
const a=new Vector3(-212,45,-34), b=new Vector3(-115,14,-16.5)
const axis=new Vector3().subVectors(b,a), lateral=new Vector3(axis.z,0,-axis.x).normalize()
const expected=Array.from({length:97},(_,i)=>{
  const t=i/96; return a.clone().addScaledVector(axis,t).add(new Vector3(0,-4*1.2*t*(1-t),0))
})
const x=m.geometry.getAttribute('position'), buckets=Array.from({length:97},()=>new Map())
m.updateMatrixWorld(true)
for(let i=0;i<x.count;i++){
  const w=new Vector3().fromBufferAttribute(x,i).applyMatrix4(m.matrixWorld)
  let id=-1,dist=Infinity
  for(let j=0;j<97;j++){
    const n=expected[j].distanceToSquared(w)
    if(n<dist){id=j;dist=n}
  }
  assert.ok(Math.abs(Math.sqrt(dist)-.065)<.00004)
  buckets[id].set(w.toArray().map(v=>v.toFixed(5)).join('/'),i)
}
assert.ok(buckets.every(x=>x.size===8))
const mixer=new AnimationMixer(m)
const action=mixer.clipAction(clip).setLoop(LoopOnce,1)
action.clampWhenFinished=true
function shape(t){
  action.reset().play()
  mixer.setTime(t)
  const p=new Vector3(), d=new Vector3()
  return buckets.map(indices=>{
    const c=new Vector3()
    for(const i of indices.values()){
      p.fromBufferAttribute(x,i)
      for(const [j,key] of m.geometry.morphAttributes.position.entries()){
        d.fromBufferAttribute(key,i)
        p.addScaledVector(d,m.morphTargetInfluences[j])
      }
      c.add(p.applyMatrix4(m.matrixWorld))
    }
    return c.multiplyScalar(1/8)
  })
}
const probes=[0,1.25,2.5,3.75,5].map(t=>shape(t))
assert.ok(Math.max(...probes[0].map((p,j)=>p.distanceTo(expected[j])))<.00002)
assert.ok(Math.max(...probes[0].map((p,j)=>p.distanceTo(probes[4][j])))<.00001)
let maxAnchor=0,maxSleeve=0,maxSide=0,maxDip=0
for(let i=0;i<=240;i++){
  const frame=shape(i/48)
  for(const j of [0,96])maxAnchor=Math.max(maxAnchor,probes[0][j].distanceTo(frame[j]))
  for(const j of [1,2,3,4,5,91,92,93,94,95]) maxSleeve=Math.max(maxSleeve,probes[0][j].distanceTo(frame[j]))
  const mid=frame[48].sub(probes[0][48])
  maxSide=Math.max(maxSide,Math.abs(mid.dot(lateral)))
  maxDip=Math.max(maxDip,-mid.y)
}
assert.ok(maxAnchor<.00001 && maxSleeve<.00001)
assert.ok(Math.abs(maxSide-.38)<.0001 && Math.abs(maxDip-.076)<.0001,[maxSide,maxDip])
assert.ok(probes[1][48].clone().sub(probes[3][48]).length()>.759)
console.log(JSON.stringify({duration:clip.duration,steps:241,lockedEndpointDriftMeters:maxAnchor,
  sleeveDriftMeters:maxSleeve,peakSwayMeters:maxSide,peakDipMeters:maxDip,
  startEndEqual:true,rings:buckets.length},null,2))
