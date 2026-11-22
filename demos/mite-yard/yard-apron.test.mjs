import test from 'node:test'
import assert from 'node:assert/strict'
import {createApron} from './yard-apron.mjs'
test('East 01 apron geometry is deterministic, flat and within budget',()=>{
 const a=createApron()
 assert.deepEqual(a,createApron())
 assert.equal(a.filter(p=>p.style==='slab').length,48)
 const tris=a.reduce((n,p)=>n+p.points.length-2,0)
 assert(tris<=400)
 for(const {points,y} of a){
  assert(Math.abs(y)<=.005)
  for(const [x,z] of points)assert(Math.abs(x)<=9&&Math.abs(z)<=11)
  for(let i=0;i<points.length;i++){
   const [a,b,c]=[i,i+1,i+2].map(k=>points[k%points.length])
   assert((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])>0,'Patch must be convex and CCW')
  }
 }
})
