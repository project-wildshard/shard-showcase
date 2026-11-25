import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync} from 'node:fs'
import {Box3,Vector3,Raycaster} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
const path=process.argv[2]??new URL('../public/assets/wildshard-art/e8b-big-pallet-pit.glb',import.meta.url)
const raw=readFileSync(path)
const {scene,animations}=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
assert.equal(animations.length,0)
const center=[96,0,-206]
scene.position.set(...center)
scene.updateMatrixWorld(true)
const b=new Box3().setFromObject(scene,true)
assert(Math.abs(b.min.x-82)<.005&&Math.abs(b.max.x-110)<.005)
assert.equal(b.min.y,0)
assert(Math.abs(b.max.y-2.90)<.0001)
let triangles=0,drawPrimitives=0
scene.traverse(o=>{if(o.isMesh){drawPrimitives++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3}})
assert.equal(drawPrimitives,14)
const ray=new Raycaster()
function first(x,y,z,dx,dy,dz,far){
  ray.set(new Vector3(x+center[0],y,z+center[2]),new Vector3(dx,dy,dz))
  ray.far=far
  return ray.intersectObject(scene,true).at(0)
}
let cleared=0
for (const side of [-1,1]) {
  for(const y of [.25,.75,1.30])for(let i=-28;i<=28;i++){
    assert(!first(i*.10,y,side*16,0,0,-side,32));cleared++
  }
}
for (const side of [-1,1])for(const z of [-3,0,3])
  assert(first(side*16,.7,z,-side,0,0,5),'Expected exterior-facing wall');
for (const side of [-1,1])for(const z of [-3,0,3])
  assert(first(0,.7,z,side,0,0,16),'Expected interior face or pillar');
for (const x of [-3,0,3])for(let z=-10;z<=10;z++)
  assert(Math.abs(first(x,5,z,0,-1,0,6).point.y-.05)<1e-5)
for (const [x,z] of [[-6.8,-.6],[6.8,.6]])
  assert(Math.abs(first(x,5,z,0,-1,0,6).point.y-2.9)<1e-5)
const openEnds=[-1,1].map(side=>{
  let lo=2.8,hi=3.75
  assert(!first(lo,.75,side*16,0,0,-side,5))
  assert(first(hi,.75,side*16,0,0,-side,5))
  for(let j=0;j<24;j++){
    const mid=(lo+hi)/2
    if(first(mid,.75,side*16,0,0,-side,5))hi=mid
    else lo=mid
  }
  return 2*lo
})
assert(openEnds.every(n=>n>5.82&&n<6.07),JSON.stringify(openEnds))
const data={center,cleared,arrivalWidthAt75cmM:openEnds,drawPrimitives,triangles,bytes:raw.length,
  sha256:createHash('sha256').update(raw).digest('hex')}
console.log(JSON.stringify(data,null,2))
