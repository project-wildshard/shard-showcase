import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { Box3, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const dir=process.argv[2] ?? 'public/assets/wildshard-art'
const spec=[
  ['w10b-riding-lap-board','Riding_lap_floor_origin','Vacant_record_plane',1492,2.27],
  ['w10b-first-ring-ahead','First_ring_arrow_floor_origin','Ahead_arrow',219,.88],
]
for (const [name,parent,piece,expected,width] of spec) {
  const b=await readFile(join(dir,name+'.glb'))
  const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')
  assert.deepEqual(gltf.scene.children.map(o=>o.name),[parent])
  assert(gltf.scene.getObjectByName(piece)?.isMesh)
  assert(!gltf.animations.length && b.length<75000)
  const bounds=new Box3().setFromObject(gltf.scene)
  assert(Math.abs(bounds.min.y)<1e-5)
  assert(Math.abs(bounds.max.x-bounds.min.x-width)<1e-5)
  let faces=0
  const [a,c,d]=Array.from({length:3},()=>new Vector3())
  gltf.scene.traverse(o=>{
    assert(!o.isCamera&&!o.isLight)
    if(!o.isMesh)return
    const {index,attributes:{position}}=o.geometry
    const count=index?.count??position.count
    for(let i=0;i<count;i+=3){
      const v=k=>index?index.getX(k):k
      a.fromBufferAttribute(position,v(i))
      c.fromBufferAttribute(position,v(i+1))
      d.fromBufferAttribute(position,v(i+2))
      assert(c.sub(a).cross(d.sub(a)).lengthSq()>1e-20,'Degenerate triangle in '+o.name)
      faces++
    }
  })
  assert.equal(faces,expected)
  console.log(name,b.length,faces)
}
