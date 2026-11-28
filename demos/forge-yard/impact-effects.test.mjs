import {test} from 'node:test';
import assert from 'node:assert/strict';
import {surfaceCue} from './impact-effects.mjs';
const rival={x:2,z:-4,r:.7,height:2.2};
test('visual impact anchors follow the attacker-facing side and do not change the actors',()=>{
 const p={x:3,z:-3};
 const b={...rival};
 const cue=surfaceCue(p,b,1.35);
 assert.equal(cue.at[1],1.35);
 assert(Math.abs(Math.hypot(cue.at[0]-b.x,cue.at[2]-b.z)-b.r*.83)<1e-9);
 assert(cue.at[0]>b.x&&cue.at[2]>b.z);assert(Math.abs(Math.hypot(...cue.outer)-1)<1e-9);
 assert.deepEqual(b,rival);assert.deepEqual(p,{x:3,z:-3});
});
test('visual impact clamping is finite for overlap, a missing socket or an extreme animated position',()=>{
 const o=surfaceCue(rival,rival,NaN);
 assert(o.at.every(Number.isFinite));assert.deepEqual(o.outer,[0,0,1]);assert.equal(o.at[1],rival.height*.59);
 assert.equal(surfaceCue({x:0,z:0},rival,-5).at[1],.18);
 assert.equal(surfaceCue({x:0,z:0},rival,50).at[1],rival.height*.68);
});
