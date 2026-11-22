import assert from 'node:assert/strict'
import test from 'node:test'
import {BAY_FINISHES,LOADING_BAY,createLoadingBay} from './yard-loading-bay.mjs'
import {createRearCladding} from './yard-cladding.mjs'

test('the closed loading bay fits the opening without entering the fight lane',()=>{
 const parts=createLoadingBay()
 assert.deepEqual(parts,createLoadingBay())
 assert(parts.reduce((n,{segments:[x,y]})=>n+4*(x*y+x+y),0)<1170)
 for(const {finish,size:[w,h,d],position:[x,y,z]} of parts){
  assert(Object.hasOwn(BAY_FINISHES,finish))
  assert(w>0&&h>0&&d>0&&y-h*.5>=-.001)
  assert(Math.abs(x)+w*.5<=LOADING_BAY.halfWidth+.01)
  assert(z+d*.5<-10.60)
 }
 const slats=parts.filter(p=>p.finish.startsWith('slat'))
 assert.equal(slats.length,12)
 assert(slats.every(p=>p.size[0]===LOADING_BAY.doorHalfWidth*2))
 assert(parts.find(p=>p.finish==='frame'&&p.size[2]>.6))
 const sidePanels=createRearCladding([3,4,5])
 assert.equal(sidePanels.length,120)
 assert(sidePanels.every(p=>p.points.every(([x])=>Math.abs(x)>=LOADING_BAY.halfWidth-.05)))
})
