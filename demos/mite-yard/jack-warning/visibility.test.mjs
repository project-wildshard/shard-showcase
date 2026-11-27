import assert from 'node:assert/strict';
import test from 'node:test';
import {jackWarning as warn} from './visibility.mjs';
const current={tick:88,currentTick:88,windup:true,threatReachesPlayer:true,
  nativeArrow:false,bodyVisible:false,laneVisible:false,tested:true};
test('separate HUD route when both visual channels are lost',()=>{
  assert.equal(warn(current),'hidden-charge');
});
test('no duplicates while any existing channel is readable',()=>{
  assert.equal(warn({...current,nativeArrow:true}),'native-edge');
  assert.equal(warn({...current,bodyVisible:true}),null);
  assert.equal(warn({...current,laneVisible:true}),null);
});
test('unknown or stale ray data, blocked lane and non-wind-up never add a new warning',()=>{
  for(const c of [{tested:false},{tick:87},{tick:NaN},{windup:false},{threatReachesPlayer:false},
    {threatReachesPlayer:undefined},{bodyVisible:undefined},{laneVisible:undefined}]){
    assert.equal(warn({...current,...c}),null);
  }
});
