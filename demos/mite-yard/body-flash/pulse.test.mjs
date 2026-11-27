import test from 'node:test';
import assert from 'node:assert/strict';
import {confirmSwordPulse, pulseWeight, PEAK} from './pulse.mjs';
const attack={weapon:'sword',source:'melee',damageDealt:24,at:2,hitId:'hit-1'};
const p=confirmSwordPulse(attack);
test('real hit is visible, small, short and unaffected by hit-stop',()=>{
  assert.equal(pulseWeight(p,2),PEAK);
  assert.ok(Math.abs(pulseWeight(p,2.05)-.22/9)<1e-9);
  assert.equal(pulseWeight(p,2.075),0);
  assert.equal(pulseWeight(p,1.99),0);
  assert.equal(pulseWeight(p,2.1),0);
});
test('whiffs, immune hits, and non-melee effects do not arm it',()=>{
  for (const c of [{damageDealt:0},{damageDealt:-1},{damageDealt:NaN},{weapon:'spear'},
    {source:'skill'},{hitId:null},{at:Infinity}]) {
    assert.equal(confirmSwordPulse({...attack,...c}),null);
    assert.equal(confirmSwordPulse({...attack,...c},p),p);
  }
});
test('same or older event cannot reopen pulse; valid new hit replaces without stacking',()=>{
  assert.equal(confirmSwordPulse({...attack,at:2.02},p),p);
  assert.equal(confirmSwordPulse({...attack,hitId:'stale',at:1},p),p);
  const q=confirmSwordPulse({...attack,hitId:'new',at:2.03},p);
  assert.equal(pulseWeight(q,2.03),PEAK);
});
test('respect flash setting including off',()=>{
  assert.equal(pulseWeight(p,2,0),0);
  assert.equal(pulseWeight(p,2,.5),PEAK*.5);
  assert.equal(pulseWeight(p,2,2),PEAK);
  assert.equal(pulseWeight(p,2,NaN),0);
});
