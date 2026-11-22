import test from 'node:test'
import assert from 'node:assert/strict'
import {createRearCladding} from './yard-cladding.mjs'

test('rear has shallow outward-facing corrugation in nine stable bays',()=>{
 const quads=createRearCladding()
 assert.equal(quads.length,180)
 assert(quads.length*2<50*12,'Fewer face triangles than the replaced solid ribs')
 assert.deepEqual(quads,createRearCladding())
 for(const {top,bottom,points:[a,b,c,d]} of quads){
  assert(b[0]>a[0]&&c[1]>b[1],'Front normal faces the court')
  for(const [x,y,z] of [a,b,c,d]){
   assert(Math.abs(x)<=9&&y>.07&&y<2.65)
   assert(z>-11&&z<=-10.71,'Keep portal and collision clear')
  }
  assert(top>bottom&&top!==0xffffff,'Subtle top wash, no white focal stripe')
 }
})
