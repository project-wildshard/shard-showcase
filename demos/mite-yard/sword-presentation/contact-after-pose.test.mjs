import test from 'node:test';
import assert from 'node:assert/strict';
import {pickSwordContactPose as pick} from './contact-after-pose.mjs';
const hit={id:'duel/J1/4',target:'J1',tick:104,source:'melee',weapon:'sword',
  weaponEpoch:3,damageDealt:24,action:'sword3',actionT:.425};
const sample={tick:104,weaponEpoch:3,action:'sword3',actionT:.425,
  base:[.2,.9,.3],tip:[.5,1.1,1.1]};
test('read the rendered blade after the hit phase, then snapshot it',()=>{
  const e=pick(hit,sample);
  assert.notEqual(e.tip,sample.tip);
  assert.deepEqual(e,{id:hit.id,tip:sample.tip,base:sample.base});
});
test('previous tick or phase, pose skipped, canceled action, weapon swap',()=>{
  for(const c of [{tick:103},{tick:105},{actionT:.4},{action:null},{weaponEpoch:4},
    {tip:sample.base},{tip:[NaN,0,0]},{actionT:NaN}]) assert.equal(pick(hit,{...sample,...c}),null);
  assert.equal(pick(hit,null),null);
});
test('no contact glow for a whiff, immune strike, false match or repeated event',()=>{
  for(const c of [{damageDealt:0},{damageDealt:-1},{damageDealt:Infinity},{source:'skill'},
    {weapon:'spear'},{id:null},{weaponEpoch:null},{actionT:NaN}]) assert.equal(pick({...hit,...c},sample),null);
  assert.equal(pick(null,sample),null);
  assert.equal(pick(hit,sample,hit.id),null);
});
