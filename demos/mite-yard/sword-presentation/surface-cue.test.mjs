import test from 'node:test';
import assert from 'node:assert/strict';
import {chooseSwordCue as cue} from './surface-cue.mjs';
const hit={id:'duel/wing/4',targetId:'J1',tick:104,source:'melee',weapon:'sword',
  weaponEpoch:3,damageDealt:24,action:'sword3',actionT:.425};
const pose={tick:104,weaponEpoch:3,action:'sword3',actionT:.425,base:[.2,.9,.3],tip:[.5,1.1,1.1]};
const sample={targetId:'J1',hitId:hit.id,weaponEpoch:3,tick:104,gapM:.05,point:[.5,1.08,1.07],normal:[0,0,-1]};
test('use a nearby surface on this hit and retain measured blade',()=>{
  const c=cue(hit,pose,sample);
  assert.equal(c.mode,'surface-glint');
  assert.deepEqual(c.point,sample.point);
  assert.notEqual(c.point,sample.point);
  assert.deepEqual(c.blade.tip,pose.tip);
});
test('gap or stale receipt retains normal hit feedback but not a fake point',()=>{
  for(const bad of [{gapM:.060001},{gapM:NaN},{gapM:-.01},{targetId:'J2'},{hitId:'different'},
    {weaponEpoch:4},{tick:103},{point:[1,2,Infinity]},{normal:[0,0,0]}]){
    assert.deepEqual(cue(hit,pose,{...sample,...bad}),{id:hit.id,mode:'existing-hit-feedback'});
  }
  assert.equal(cue(hit,pose,null).mode,'existing-hit-feedback');
});
test('miss, immune, no computed pose or repeated hit has no new cue',()=>{
  assert.equal(cue({...hit,damageDealt:0},pose,sample),null);
  assert.equal(cue(hit,{...pose,tick:103},sample),null);
  assert.equal(cue(hit,pose,sample,hit.id),null);
});
