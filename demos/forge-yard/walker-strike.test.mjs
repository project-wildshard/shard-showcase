import {test} from 'node:test';
import assert from 'node:assert/strict';
import {WEAPONS,create,spawn,press,select,tick} from './arena.mjs';
import {RELEASE_POSE,SIGNATURE_STRIKES,walkerStrikePhase,walkerStrike} from './walker-strike.mjs';
test('every weapon drives the same authored release pose on the simulation release tick',()=>{
 for(const [i,weapon] of WEAPONS.entries()){
  const s=create([{id:'test',attack:'windmill',radius:.55,hp:1000,reach:1.75,pace:0,windup:2,recover:1}]);
  const rival=spawn(s,0,{x:0,z:4.7});
  select(s,i);assert(press(s,'attack'));
  for(let t=0;t<80&&!s.player.slash?.done;t++)tick(s,1/60);
  const slash=s.player.slash;assert(slash?.done&&slash.releaseAt===slash.time);
  assert(weapon.wind<=slash.releaseAt&&slash.releaseAt<=weapon.wind+1/60+1e-9);
  assert.equal(walkerStrikePhase(slash.releaseAt,slash.releaseAt,weapon.cycle),RELEASE_POSE);
  assert.equal(walkerStrikePhase(0,slash.releaseAt,weapon.cycle),0);
  assert(walkerStrikePhase(slash.releaseAt-.004,slash.releaseAt,weapon.cycle)<RELEASE_POSE);
  assert(walkerStrikePhase(slash.releaseAt+.004,slash.releaseAt,weapon.cycle)>RELEASE_POSE);
  assert.equal(walkerStrikePhase(weapon.cycle+.1,slash.releaseAt,weapon.cycle),1);
  assert.equal(rival.hp-weapon.power,rival.life);
 }
 assert.equal(new Set(WEAPONS.map(walkerStrike)).size,6);
 assert.equal(Object.values(SIGNATURE_STRIKES).length,3);
});
