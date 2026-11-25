import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {Box3,Group,Matrix4,Vector3} from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {ageToHeat,makeSlagBatch,DURATION,CAPACITY} from './slag.mjs'
assert(process.argv[2]&&process.argv[3],'Pass exact static donor and receipt path')
const raw=readFileSync(process.argv[2])
const sha=createHash('sha256').update(raw).digest('hex')
assert.equal(sha,'5e4ff946ef5291df0d08ff0e5d7ed8f07a3a13c60716606da410604f774487c8')
assert.equal(ageToHeat(0),1)
assert.equal(ageToHeat(5.99),0)
assert.equal(ageToHeat(6),null)
assert.equal(ageToHeat(-.001),null)
assert.throws(()=>ageToHeat(Infinity))
for(let n=1;n<600;n++)assert(ageToHeat(n/100)<=ageToHeat((n-1)/100))
const asset=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.length),'')
const checkBefore=new Box3().setFromObject(asset.scene,true)
const batch=makeSlagBatch(asset.scene),geo=batch.mesh.geometry
geo.computeBoundingBox()
assert(geo.boundingBox.min.distanceTo(checkBefore.min)<1e-6)
assert(geo.boundingBox.max.distanceTo(checkBefore.max)<1e-6)
assert.equal(geo.getAttribute('position').count,703*3)
assert.equal(geo.groups.length,0)
assert.equal(geo.getAttribute('heat').count,12)
assert(batch.mesh.isInstancedMesh&&batch.mesh.material.isShaderMaterial)
assert.throws(()=>makeSlagBatch(new Group()))
const fixed={born:22,x:0,y:.003,z:1.2,yaw:Math.PI}
const late={...fixed,born:23,x:-2,z:1.4}
assert.deepEqual(batch.update(21.999,[fixed,late]),[])
assert.equal(batch.mesh.visible,false)
assert.deepEqual(batch.update(22,[fixed,late]),[1])
assert.equal(batch.mesh.visible,true)
assert.equal(batch.mesh.count,1)
const position=new Vector3()
const activeMatrix=new Matrix4()
batch.mesh.getMatrixAt(0,activeMatrix)
position.setFromMatrixPosition(activeMatrix)
assert(position.distanceTo(new Vector3(0,.003,1.2))<1e-6)
const [a,b]=batch.update(24,[fixed,late])
assert(a<b)
assert.equal(batch.mesh.count,2)
assert(Math.abs(geo.getAttribute('heat').getX(0)-a)<1e-7)
assert(Math.abs(geo.getAttribute('heat').getX(1)-b)<1e-7)
assert.deepEqual(batch.update(28,[fixed,late]),[ageToHeat(5)])
batch.mesh.getMatrixAt(0,activeMatrix)
assert(new Vector3().setFromMatrixPosition(activeMatrix).distanceTo(new Vector3(-2,.003,1.4))<1e-6)
assert.deepEqual(batch.update(29,[fixed,late]),[])
assert.deepEqual(batch.update(30,[{...fixed,born:30}]),[1])
assert.throws(()=>batch.update(30,Array(13).fill(fixed)))
assert.throws(()=>batch.update(30,[fixed,{...late,y:NaN}]))
assert.equal(batch.mesh.count,1)
const loads=Array.from({length:CAPACITY},(_,i)=>({...fixed,x:i,born:Math.floor(i/3)+30}))
assert.equal(batch.update(34,loads).length,CAPACITY)
assert.equal(batch.mesh.count,CAPACITY)
const materialChanged=[]
asset.scene.traverse(o=>{if(o.isMesh)materialChanged.push(o.material.emissiveIntensity)})
assert.equal(materialChanged.length,6)
batch.dispose()
const proof={sha256:sha,durationSeconds:DURATION,triangleCount:703,staticGLBBytes:raw.length,
  visibleInstancesMax:CAPACITY,materialsPerBatch:1,meshGroups:0,
  checks:['exact donor bounds','independent ages','stable placement','expired slot compaction','retriggers','capacity and bad input'],
  samples:[0,.38,2.1,3.8,5.22,5.9,6].map(t=>[t,ageToHeat(t)]),
  scope:'CPU Three.js batch and timing checks, not a measured WebGL draw count or native install'}
writeFileSync(process.argv[3],JSON.stringify(proof,null,2)+'\n')
console.log(JSON.stringify(proof))
