import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { Box3, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
const dir=process.argv[2] ?? 'public/assets/wildshard-art'
const paths=['w4b-release-stand.glb','w4b-skittle-scoreboard.glb']
const report=[]
for (const name of paths) {
  const bytes=await readFile(join(dir,name))
  const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')
  assert(!gltf.animations.length)
  assert(bytes.length<80000)
  const bounds=new Box3().setFromObject(gltf.scene)
  assert(Math.abs(bounds.min.y)<1e-5)
  const size=bounds.getSize(new Vector3()).toArray()
  let triangles=0
  const [a,b,c]=Array.from({length:3},()=>new Vector3())
  gltf.scene.traverse(o=>{
    assert(!o.isCamera&&!o.isLight)
    if(!o.isMesh) return
    const {index,attributes:{position}}=o.geometry
    const count=index?.count??position.count
    for(let i=0;i<count;i+=3){
      const v=k=>index?index.getX(k):k
      a.fromBufferAttribute(position,v(i))
      b.fromBufferAttribute(position,v(i+1))
      c.fromBufferAttribute(position,v(i+2))
      assert(b.sub(a).cross(c.sub(a)).lengthSq()>1e-20,'Degenerate triangle on '+o.name)
      triangles++
    }
  })
  if(name===paths[0]){
    const arm=gltf.scene.getObjectByName('Release_arm_localX_pivot')
    const base=gltf.scene.getObjectByName('Release_stand_floor')
    assert(arm && base && arm.parent===base.parent)
    assert(Math.abs(arm.getWorldPosition(a).y-1.103)<1e-5)
    assert(size[1]>1.76&&size[1]<1.78)
  }else{
    assert(size[0]>4.30&&size[0]<4.32)
    assert(size[1]>2.92&&size[1]<2.94)
    assert(gltf.scene.getObjectByName('Skittle_scoreboard_floor'))
  }
  report.push({name,bytes:bytes.length,triangles,sizeM:size.map(v=>Number(v.toFixed(4)))})
}
console.log(JSON.stringify(report,null,2))
