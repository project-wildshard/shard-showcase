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
  const held=step({...x,override:true,lookDeg:0});
  assert.equal(held.turn,a.turn);
  assert(held.widen<a.widen);
  const drag=step({...x,override:true,lookDeg:sign*.4});
  assert(Math.abs(drag.turn-held.turn)<=.1+1e-8);
  assert(Math.sign(sign*.4+drag.turn-held.turn)===sign);
  let prev=drag;
  for(let i=0;i<10;i++){
    const next=step(x);
    assert(Math.abs(next.turn)<=Math.abs(prev.turn)&&next.widen<=prev.widen);
    prev=next;
  }
  assert.deepEqual(step({...x,hardStop:true}),{turn:0,widen:0});
}
const step=counterLens();
assert.deepEqual(step({...scene,anchors:[...scene.anchors,[0,0,.5,false]]}),{turn:0,widen:0});
assert.deepEqual(step({...scene,engaged:false}),{turn:0,widen:0});
console.log('mirrored turn, rate caps, override, release guard, behind-camera and disengagement checks passed');
