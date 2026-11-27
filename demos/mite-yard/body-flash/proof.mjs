import assert from 'node:assert/strict';
import {confirmSwordPulse,pulseWeight} from './pulse.mjs';
// Source-based continuous-clock envelope; initial sample before same-tick
// updates. Discrete engine ticks, next-frame ordering and post are not modeled.
const p=confirmSwordPulse({weapon:'sword',source:'melee',damageDealt:1,at:0,hitId:1});
const scale=.04, rate=7;
const r=x=>+x.toFixed(6);
const cases=[0,.055,.11].map(stop=>({
  stopMs:stop*1000,
  samples:[0,1,2,3,4,5,6,8,9,12,15].map(frame=>{
    const t=frame/60, sim=Math.min(t,stop)*scale+Math.max(0,t-stop);
    const original=Math.max(0,1-rate*sim), candidate=pulseWeight(p,t);
    return {frame,wallMs:r(t*1000),simMs:r(sim*1000),original:r(original),
      candidate:r(candidate),retainedOriginal:r(1-original),retainedCandidate:r(1-candidate)};
  })
}));
const heavy=cases[2].samples.find(f=>f.frame===6);
assert.ok(heavy.original>.97 && heavy.candidate===0);
assert.equal(cases[2].samples[0].retainedCandidate,.78);
const reference={
  commit:'3afcd880b397e9703e906a7e66b42e8447e59519',
  capture:'tools/golden/scenes.js (09)', ordinaryThirdSword:'src/data/moves.ts:66',
  bodySetterAndDecay:'src/systems/mobs.ts:266,313,630–639',
  outgoingMix:'src/gfx/material.ts:373', hitStopClock:'src/game.ts:451–456',
};
process.stdout.write(JSON.stringify({reference,
  scope:'Body-only linear white mix model, idealized timing, not Fable runtime or measured display luminance.',
  retention:'Difference between two actor radiance values is multiplied by 1 - wash before tone mapping.',
  hz:60,hitStopScale:scale,simDecayPerSecond:rate,cases
},null,2)+'\n');
