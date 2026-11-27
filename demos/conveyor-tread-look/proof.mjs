import assert from 'node:assert/strict'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {attachTread,periodM,phase,placements,treadTile} from './tread.mjs'

const req=createRequire(join(resolve(process.env.WSC_NODE_PROJECT||'.'),'package.json'))
const THREE=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)
assert.equal(THREE.REVISION,'186')
const {GLTFLoader}=await import(pathToFileURL(join(dirname(req.resolve('three')),'../examples/jsm/loaders/GLTFLoader.js')))
const raw=readFileSync(new URL('../../public/assets/wildshard-art/wsc-prop-037-conveyor-module.glb',import.meta.url))
const sha=createHash('sha256').update(raw).digest('hex')
assert.equal(sha,'1d0d5e0ac6fb0fd201daef538ed3e277824a2a0f6b9677968fe2f8dbb18debdb')
const {scene}=await new GLTFLoader().parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'')
const get=scene=>{const a=[];scene.traverse(x=>{if(x.isMesh)a.push(x)});return a}
const originals=get(scene)
assert.equal(originals.length,10)
const moved=placements.map(p=>{
  const root=scene.clone(true)
  root.position.set(p.x,p.y,p.z);root.rotation.y=p.yaw
  const materials=get(root).map(x=>[x.material,x.geometry])
  const handle=attachTread(THREE,root)
  let uvCount=0, untouched=0
  get(root).forEach((x,i)=>{
    const [mat,geo]=materials[i]
    if(!mat.name.startsWith('Rubber tread')){
      assert.equal(x.material,mat);assert.equal(x.geometry,geo);untouched++;return
    }
    assert.notEqual(x.material,mat);assert.equal(mat.map,null)
    assert.deepEqual(x.geometry.attributes.position.array,geo.attributes.position.array)
    for(let j=0;j<x.geometry.attributes.uv.count;j++){
      assert(Math.abs(x.geometry.attributes.uv.getX(j)*periodM-geo.attributes.position.getX(j))<1e-6)
      assert.equal(x.geometry.attributes.uv.getY(j),.5);uvCount++
    }
  })
  assert.equal(untouched,7)
  const local=p.worldSpeed*Math.cos(p.yaw)
  const wrap=seconds=>handle.setTime(seconds,local)
  assert.equal(wrap(0),0)
  assert(Math.abs(wrap(periodM/Math.abs(local)))<1e-10)
  const dt=1/60, offset=wrap(dt)
  // Fixed phase point advances at the authored rate in world X.
  const metres=-offset*periodM*Math.cos(p.yaw)
  assert(Math.abs(metres-p.worldSpeed*dt)<1e-10)
  assert(Math.abs(wrap(32+periodM/Math.abs(local))-phase(local,32))<1e-10)
  handle.dispose()
  get(root).forEach((x,i)=>{assert.equal(x.material,materials[i][0]);assert.equal(x.geometry,materials[i][1])})
  return {worldSpeedMps:p.worldSpeed,localSpeedMps:local,phaseAfterOneTick:offset,uvVerticesChecked:uvCount,untouchedPrimitives:untouched}
})
const result={scope:'Three.js visual only; no gameplay, collision, crate motion, native integration or phone performance.',donorSha256:sha,threeRevision:THREE.REVISION,periodM,proceduralTileBytes:treadTile().length,addedTriangles:0,moved}
assert(process.argv[2],'Pass a proof output path')
writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n')
console.log(result)
