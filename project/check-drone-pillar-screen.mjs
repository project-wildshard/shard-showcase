import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { Box3, DoubleSide, Raycaster, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const path=process.argv[2]??new URL('../public/assets/wildshard-art/e3-suspended-pillar-screen.glb',import.meta.url)
const raw=readFileSync(path)
const exported=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
const scene=exported.scene
assert.equal(exported.animations.length,0)
scene.updateMatrixWorld(true)
const box=new Box3().setFromObject(scene,true)
const xyz=v=>v.toArray().map(n=>Number(n.toFixed(5)))
assert.deepEqual(xyz(box.min),[-4.8,0,-.8])
assert.deepEqual(xyz(box.max),[4.8,7,.8])
// Round 5 placement.js (archive sha in proof); first screen preserving the
// full 8 m clear radius using the enclosing footprint, not just its pivot.
const row={x:127.00188806606545,z:-193.26727363805625,yaw:1.6358347724869582}
const pack={x:146.5,z:-225.94061227794052}
const vector=(x,y,z)=>new Vector3(x,y,z)
scene.position.set(row.x,0,row.z)
scene.rotation.y=row.yaw
scene.updateMatrixWorld(true)
const loc=scene.worldToLocal(vector(pack.x,0,pack.z))
const boundMargin=Math.hypot(Math.max(0,Math.abs(loc.x)-4.8),Math.max(0,Math.abs(loc.z)-.8))
assert(Math.abs(boundMargin-33.705182353963366)<1e-6)
let drawPrimitives=0,triangles=0,materials=new Set()
scene.traverse(o=>{
  if(!o.isMesh)return
  drawPrimitives++
  triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3
  for(const m of Array.isArray(o.material)?o.material:[o.material]){materials.add(m.name);m.side=DoubleSide}
})
const ray=new Raycaster()
const casts=([x,y,z])=>{
  const from=scene.localToWorld(vector(x,y,z))
  const to=scene.localToWorld(vector(x,y,-z))
  ray.set(from,to.sub(from).normalize())
  ray.far=8
  return ray.intersectObject(scene,true).length>0
}
assert.equal(drawPrimitives,8)
assert.equal(materials.size,8)
const levels=[.85,1.7,2.1,3,4,5,7.2]
const hitCounts=levels.map(y=>[-1,1].flatMap(s=>
  Array.from({length:33},(_,i)=>casts([(i-16)*.2,y,4*s]))).filter(Boolean).length)
assert.deepEqual(hitCounts,[0,0,0,66,66,66,0])
let sideHits=0
for(const x of [-4,4])for(const y of [.1,1.7,3,5,6.94])for(const s of [-1,1]){
  assert(casts([x,y,s*4]));sideHits++
}
const result={sha256:createHash('sha256').update(raw).digest('hex'),bytes:raw.length,triangles,
  distinctMaterials:materials.size,drawPrimitives,localBoundsThree:[xyz(box.min),xyz(box.max)],
  row,nearestPack:pack,conservativeEdgeToPackM:boundMargin,
  centerRays:{heights:levels,hitCounts,perHeight:66},bothPillarHits:sideHits}
if(process.argv[3]) process.stdout.write(JSON.stringify(result,null,2)+'\n')
else console.log('E03 static ray repeat passed:', JSON.stringify(result))
