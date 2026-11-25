import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { Box3, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const dir=process.argv[2] ?? 'public/assets/wildshard-art'
for (const [stem, groups] of [
  ['e5b-alarm-gate-leaf',['Alarm_leaf_floor_origin']],
  ['e5b-alarm-signal',['Alarm_signal_mount','Closed_red_lens','Clear_cyan_lens']],
]) {
  const path=join(dir,stem+'.glb')
  const bytes=await readFile(path)
  const model=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')
  assert(!model.animations.length && bytes.length<120000)
  assert.deepEqual(model.scene.children.map(c=>c.name).sort(),groups.sort())
  const bound=new Box3().setFromObject(model.scene)
  const dims=bound.getSize(new Vector3())
  if (groups.length===1) {
    assert(Math.abs(dims.x-7.98)<.0001)
    assert(Math.abs(bound.min.y)<.0001)
    assert(Math.abs(bound.max.y-3.86)<.0001)
  } else {
    const lower=new Box3().setFromObject(model.scene.getObjectByName('Clear_cyan_lens'))
    const upper=new Box3().setFromObject(model.scene.getObjectByName('Closed_red_lens'))
    assert(lower.max.y<upper.min.y,'Clear and alarm lenses must occupy separate slots')
  }
  let faces=0
  const [a,b,c]=Array.from({length:3},()=>new Vector3())
  model.scene.traverse(o=>{
    assert(!o.isCamera&&!o.isLight)
    if(!o.isMesh)return
    const {index,attributes:{position}}=o.geometry
    const count=index?.count??position.count
    for(let i=0;i<count;i+=3){
      const v=k=>index?index.getX(k):k
      a.fromBufferAttribute(position,v(i))
      b.fromBufferAttribute(position,v(i+1))
      c.fromBufferAttribute(position,v(i+2))
      assert(b.sub(a).cross(c.sub(a)).lengthSq()>1e-20,'Degenerate triangle in '+o.name)
      faces++
    }
  })
  console.log(stem,bytes.length,faces,dims.toArray())
}
