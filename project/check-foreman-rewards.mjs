import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {Box3,Raycaster,Vector3} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
const assets=new URL('../public/assets/wildshard-art/',import.meta.url)
const proof=JSON.parse(readFileSync(new URL('./layouts/e11d-foreman-rewards-proof.json',import.meta.url)))
const pkgs=new Map()
for(const item of proof.assets){
  const data=readFileSync(new URL(item.name+'.glb',assets))
  assert.equal(data.length,item.bytes)
  assert.equal(createHash('sha256').update(data).digest('hex'),item.sha256)
  const pkg=await new GLTFLoader().parseAsync(data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength),'')
  assert.equal(pkg.animations.length,0)
  let measured=0
  pkg.scene.traverse(o=>{
    assert.ok(!o.isLight&&!o.isSkinnedMesh&&!o.isCamera)
    if(!o.isMesh)return
    const {index,attributes:{position}}=o.geometry
    const n=index?.count??position.count
    measured+=n/3
    const v=[new Vector3(),new Vector3(),new Vector3()]
    for(let i=0;i<n;i+=3){
      v.forEach((x,j)=>x.fromBufferAttribute(position,index?index.getX(i+j):i+j))
      assert.ok(v[1].sub(v[0]).cross(v[2].sub(v[0])).lengthSq()>4e-24)
    }
  })
  assert.equal(measured,item.triangles)
  const extent=new Box3().setFromObject(pkg.scene,true).getSize(new Vector3())
  assert.ok(extent.distanceTo(new Vector3(item.dimensions_m[0],item.dimensions_m[2],item.dimensions_m[1]))<2e-6)
  pkgs.set(item.name,pkg.scene)
}
const test=(scene,p,d,z)=>new Raycaster(new Vector3(...p),new Vector3(...d),0,z).intersectObject(scene,true)
const w=pkgs.get('e11d-foreman-whistle'),h=pkgs.get('e11d-foreman-hard-hat')
assert.equal(test(w,[.042,.019,-.06],[0,0,1],.12).length,0)
assert.ok(test(w,[.042,.030,-.06],[0,0,1],.12).length>0)
for(const [x,y] of [[-.056,0],[.056,0],[0,-.06],[0,.06],[.02,.071],[-.021,-.07]]){
  const a=test(h,[x,-.03,-y],[0,1,0],.22)[0]
  assert.ok(a&&a.point.y>.05)
}
for(const [x,y] of [[-.048,-.048],[.048,.048],[-.048,.048],[.048,-.048]]){
  const hit=test(h,[x,-.03,-y],[0,1,0],.18)[0]
  assert.ok(hit&&hit.point.y>.083&&hit.point.y<.113,JSON.stringify(hit?.point))
}
console.log(proof.assets.map(o=>[o.name,o.bytes,o.triangles]),'whistle loop and hat suspension verified')
