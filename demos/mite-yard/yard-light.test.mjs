import test from 'node:test'
import assert from 'node:assert/strict'
import {YARD_SUN,shadowDelta,shadowFootprint} from './yard-light.mjs'

test('directional falloff is anchored at the base and follows the shared sun',()=>{
 assert.deepEqual(shadowDelta(YARD_SUN[1]),[8,-8])
 const [x,z]=shadowDelta(.60);assert(Math.abs(x-.342857)<1e-6&&Math.abs(z+.342857)<1e-6)
 const shape=shadowFootprint(.6,.38)
 assert.equal(shape.length,16)
 assert(shape[0][0]>.68&&shape[8][0]<0,'Tail reaches away; no gap at the feet')
 assert(Math.abs(shape[2][1])<Math.abs(shape[6][1]),'Narrower at the far end')
 const larger=shadowFootprint(1.7,.38);assert(larger[0][0]>shape[0][0])
})
