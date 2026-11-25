import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { Box3, DoubleSide, FrontSide, Raycaster, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const src = process.argv[2] ?? new URL('../../../public/assets/wildshard-art/e12g-titan-retry-alcove.glb', import.meta.url)
const raw = await readFile(src)
const ab = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength)
const { scene, animations } = await new GLTFLoader().parseAsync(ab, '')
const roots = [...scene.children].sort((a,b)=>a.userData.name.localeCompare(b.userData.name))
const names = ['01 Alcove shell', '02 Inner checkpoint', '03 Exit portal', '04 Fog threshold surround']
assert.deepEqual(roots.map(o=>o.userData.name), names)
assert.equal(animations.length,0)
scene.updateMatrixWorld(true)
let triangles=0
for (const o of roots) {
  const {min,max} = new Box3().setFromObject(o)
  assert.ok(min.y>=-.45 && max.y<9.5 && Math.max(Math.abs(min.x),Math.abs(max.x))<9.6)
  o.traverse(n=>{
    if (!n.isMesh) return
    const pos=n.geometry.getAttribute('position'), id=n.geometry.index
    assert.ok(pos.array.every(Number.isFinite) && id.array.every(i=>i<pos.count))
    assert.ok(n.material.isMeshStandardMaterial && !n.material.transparent)
    n.material.side=DoubleSide
    triangles+=id.count/3
  })
}
const on=([x,y,z],[a,b,c],far,node=scene)=>new Raycaster(
  new Vector3(x,y,z),new Vector3(a,b,c),0,far).intersectObject(node,true)
let floor=0, walk=0, portal=0, rim=0
for (const x of [-1.8,-.9,0,.9,1.8]) {
  for (const z of [52,53,54,55.5,56.2,58,60,62,64,66]) {
    const p=on([x,.20,z],[0,-1,0],.36)[0]?.point
    assert.ok(p && p.y>-.004 && p.y<.05)
    floor++
  }
  for (const y of [.18,.52,1.05,1.7,2.2]) {
    assert.equal(on([x,y,51.45],[0,0,1],14.8).length,0)
    walk++
  }
}
for(const x of [-2,-1,0,1,2]) {
  for(const y of [-2,-1,0,1,2]) {
    assert.equal(on([x+4,y+4.2,66],[0,0,1],2.6,roots[2]).length,0)
    portal++
  }
}
roots[2].traverse(n=>{ if(n.isMesh) n.material.side=FrontSide })
for(let j=0;j<12;j++){
  const a=(15+30*j)*Math.PI/180
  assert.ok(on([4+3.51*Math.cos(a),4.2+3.51*Math.sin(a),66],[0,0,1],2.6,roots[2]).length)
  rim++
}
console.log(JSON.stringify({bytes:raw.length,triangles,names,floorHits:floor,approachClear:walk,
  apertureClear:portal,machinedRimHits:rim},null,2))
