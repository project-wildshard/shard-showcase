import test from 'node:test'
import assert from 'node:assert/strict'
import {CONCRETE_METERS,CONCRETE_SIZE,concretePixels} from './concrete-surface.mjs'

test('concrete aggregate is deterministic, compact, and low contrast',()=>{
 const color=concretePixels(),shade=concretePixels(true)
 assert.equal(color.length,CONCRETE_SIZE**2*4)
 assert.deepEqual(color,concretePixels())
 let total=0,strong=0
 for(let i=0;i<color.length;i+=4){
  assert.equal(color[i+3],255)
  assert(Math.abs(color[i]+shade[i+3]-255)<=1,'Both renderers use the same wear amounts')
  assert(color[i]>=182&&color[i]<=254)
  if(color[i]<207)strong++
  total+=color[i]
 }
 assert(total/(color.length/4)>226)
 assert(strong>20&&strong<CONCRETE_SIZE**2*.1)
 assert(CONCRETE_METERS>1)
})

test('grain scan line matches exact projected metric coordinates',async()=>{
 const {floorScanline}=await import('./concrete-surface.mjs')
 const eye={w:402,h:874,fx:3.4,fy:1.57,yaw:0,pitch:0,x:0,y:1.62,z:0}
 assert.equal(floorScanline(eye,437),null,'horizon')
 assert.equal(floorScanline(eye,455),null,'beyond grain cutoff')
 const scale=CONCRETE_SIZE/CONCRETE_METERS,y=700,a=floorScanline(eye,y)
 const depth=eye.y*eye.fy/(2*y/eye.h-1)
 assert(Math.abs(a.v+depth*scale)<1e-8)
 assert(Math.abs(a.u+eye.w/2*a.du)<1e-8)
 const moved=floorScanline({...eye,x:CONCRETE_METERS},y)
 assert(Math.abs(moved.u-a.u-CONCRETE_SIZE)<1e-8)
 assert(a.opacity>floorScanline(eye,550).opacity)
 const rotated=floorScanline({...eye,yaw:Math.PI/2},y)
 assert(Math.abs(rotated.dv-a.du)<1e-8)
})
