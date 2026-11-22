import test from 'node:test'
import assert from 'node:assert/strict'
import {createTouchLook} from './touch-look.mjs'
const event=(pointerId,clientX=10,clientY=20,pointerType='touch')=>({pointerId,clientX,clientY,pointerType})
test('a second touch cannot steer the camera or terminate its active drag',()=>{
 const look=createTouchLook()
 assert.equal(look.begin(event(1)),true)
 assert.equal(look.begin(event(2,180,100)),false)
 assert.equal(look.move(event(2,190,100)),undefined)
 look.end(event(2))
 assert.deepEqual(look.move(event(1,12,25)),[2,5])
 look.end(event(1))
 assert.equal(look.move(event(1,20,30)),undefined)
})
test('capture loss or blur lets a fresh touch begin with no camera jump',()=>{
 const look=createTouchLook()
 assert.equal(look.begin(event(8,0,0,'mouse')),false)
 assert.equal(look.begin(event(8)),true)
 look.end(event(8))
 assert.equal(look.begin(event(9,200,250)),true)
 look.clear()
 assert.equal(look.begin(event(10,50,55)),true)
 assert.deepEqual(look.move(event(10,56,55)),[6,0])
})
