import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { Box3, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const dir=process.argv[2] ?? 'public/assets/wildshard-art'
for (const [stem,expected] of [['w6b-jump-pad-vector',84],['w6b-landing-index',536]]) {
  const b=await readFile(join(dir,stem+'.glb'))
  const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')
  const bounds=new Box3().setFromObject(gltf.scene)
  assert(!gltf.animations.length && b.length<40000)
  if (expected===84) assert(Math.abs(bounds.min.y-.2535)<1e-6 && bounds.max.y-bounds.min.y<1e-6)
  else assert(bounds.min.y>=-1e-6 && bounds.max.y<=.0111 && bounds.max.x<2 && bounds.max.z<4)
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
  console.log(stem,b.length,faces)
}
