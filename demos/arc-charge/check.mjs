import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {PerspectiveCamera,Vector3} from 'three'
import {DURATION,MAX_SEGMENTS,chargePieces,makeChargeCue} from './charge.mjs'
assert.equal(DURATION,.6)
const cue=makeChargeCue()
assert.equal(cue.mesh.geometry.groups.length,0)
assert.equal(cue.mesh.material.toneMapped,false)
assert.equal(cue.mesh.material.transparent,false)
const g=cue.mesh.geometry, refs=[g,g.attributes.position.array,g.attributes.color.array]
const stamp=()=>createHash('sha256').update(Buffer.from(g.attributes.position.array.buffer,0,g.drawRange.count*12))
  .update(Buffer.from(g.attributes.color.array.buffer,0,g.drawRange.count*12)).digest('hex')
let max=0
const dims=[402,874],camera=new PerspectiveCamera(62,dims[0]/dims[1],.05,100)
camera.position.set(0,0,10)
camera.lookAt(0,0,0)
camera.updateMatrixWorld()
const project=()=>Array.from({length:g.drawRange.count},(_,i)=>{
  const p=new Vector3().fromBufferAttribute(g.attributes.position,i).project(camera)
  return [(p.x/2+.5)*dims[0],(.5-p.y/2)*dims[1]]
})
const span=()=>{const p=project();return p.length?['0','1'].map(i=>Math.max(...p.map(v=>v[i]))-Math.min(...p.map(v=>v[i]))):[0,0]}
const contexts=[]
for(let i=0;i<=600;i++){
  const t=i/1000,n=cue.sample(t)
  max=Math.max(max,n)
  assert.equal(g.drawRange.count,n*24)
  assert(Array.from(g.attributes.position.array.subarray(0,n*72)).every(v=>Number.isFinite(v)&&Math.abs(v)<.6))
  assert.equal(cue.mesh.visible,n>0)
}
assert(max<=MAX_SEGMENTS&&max>40)
for(const t of [NaN,Infinity,-100,-.001,0,.6,.601,1,100])assert.equal(cue.sample(t),0)
for(const t of [.075,.315,.595]){
  const segments=cue.sample(t)
  const hash=stamp(), [width,height]=span()
  cue.sample(-4);cue.sample(.590)
  assert.equal(cue.sample(t),segments)
  assert.equal(stamp(),hash)
  assert.deepEqual([g,g.attributes.position.array,g.attributes.color.array],refs)
  const arr=(name)=>Array.from(g.attributes[name].array.slice(0,g.drawRange.count*3),v=>+v.toFixed(7))
  contexts.push({t,segments,widthPx:+width.toFixed(2),heightPx:+height.toFixed(2),positions:arr('position'),colors:arr('color')})
}
assert(contexts[2].widthPx>=55&&contexts[2].heightPx>=21)
const context=JSON.parse(readFileSync(new URL('../../project/layouts/e6-duel-cover.json',import.meta.url)))
const cover=context.half
const hash=createHash('sha256').update(readFileSync(new URL('../../public/assets/wildshard-art/e6-low-cover-return.glb',import.meta.url))).digest('hex')
assert.equal(hash,cover.sha256)
const out=process.argv[2]
assert(out)
writeFileSync(out,JSON.stringify({duration:DURATION,maxSegments:max,meshCount:1,capacity:MAX_SEGMENTS,
  viewPixels:dims,distanceM:10,verticalFov:62,context:{cover,pack:context.pack_midpoint_pair_xz[0]},
  samples:contexts.map(({positions,colors,...s})=>s),frameData:contexts})+'\n')
console.log(JSON.stringify({max,samples:contexts.map(({t,widthPx,heightPx})=>({t,widthPx,heightPx}))}))
cue.dispose()
