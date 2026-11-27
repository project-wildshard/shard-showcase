import assert from 'node:assert/strict';
import {counterLens} from './counter-lens.mjs';

const scene={anchors:[[-2.7,0,-3,false],[.55,-.7,-3,true]],
  fov:58,aspect:402/874,dt:1/60,engaged:true,override:false};
for(const sign of [1,-1]) {
  const step=counterLens();
  const x={...scene,anchors:scene.anchors.map(([x,...rest])=>[x*sign,...rest])};
  let a={turn:0,widen:0};
  for(let i=0;i<20;i++) {
    const b=step(x);
    assert(Math.abs(b.turn-a.turn)<=105*scene.dt+1e-8);
    assert(Math.abs(b.widen-a.widen)<=80*scene.dt+1e-8);
    assert(Math.abs(b.turn)<=12&&b.widen<=8);
    a=b;
  }
  assert.equal(Math.sign(a.turn),sign);
  assert(a.widen>0);
  assert.deepEqual(step({...x,override:true}),{turn:0,widen:0});
  for(let i=0;i<10;i++)assert.deepEqual(step(x),{turn:0,widen:0});
}
const step=counterLens();
assert.deepEqual(step({...scene,anchors:[...scene.anchors,[0,0,.5,false]]}),{turn:0,widen:0});
assert.deepEqual(step({...scene,engaged:false}),{turn:0,widen:0});
console.log('mirrored turn, rate caps, override, release guard, behind-camera and disengagement checks passed');
