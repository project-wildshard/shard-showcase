import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {WEAPONS,create,spawn,press,select,tick} from './arena.mjs';
const spec=JSON.parse(readFileSync(new URL('../../art/actors/dock-enemies/manifest.json',import.meta.url))).enemyTypes;
const advance=(s,d,dir)=>{for(let i=0;i<d*60;i++)tick(s,1/60,dir);};
test('all twelve weapons equip and damage a reachable enemy once per swing',()=>{
 assert.equal(WEAPONS.length,12);
 for(let i=0;i<12;i++){
  const s=create(spec);const e=spawn(s,0,{x:0,z:4.3});
  select(s,i);assert(press(s,'attack'));advance(s,.6);
  assert.equal(e.life,e.maxHp-WEAPONS[i].power);
  assert.equal(s.events.filter(x=>x.type==='enemy-hit').length,1);
 }
});
test('four enemy attack families have distinct on-guard outcomes',()=>{
 const hits=spec.map((_,i)=>{
  const s=create(spec);
  const b=spawn(s,i,{x:0,z:i>=1?3.4:4.4});
  advance(s,2);
  assert(s.events.some(e=>e.type==='enemy-state'&&e.state==='active'));
  return s.events.find(x=>x.type==='player-hit')?.style;
 });
 assert.deepEqual(hits,['windmill','pounce','beam','charge']);
});
test('dodge is conditionally invulnerable and costs pose time',()=>{
 const s=create(spec);spawn(s,0,{x:0,z:4.4});advance(s,.65);
 assert(press(s,'dodge'));assert(!press(s,'attack'));advance(s,.23);
 assert.equal(s.player.hp,120);
});
test('melee does not hit across cover and a dead enemy cannot attack',()=>{
 const a=create(spec);a.player.x=-3.1;a.player.z=1;
 const blocked=spawn(a,0,{x:-3.1,z:-1.82});select(a,2);press(a,'attack');advance(a,.33);
 assert.equal(blocked.life,blocked.maxHp);
 const b=create(spec);const e=spawn(b,0,{x:0,z:4.45});e.life=2;press(b,'attack');advance(b,2);
 assert.equal(e.state,'defeat');assert.equal(b.player.hp,120);
});
const extra=JSON.parse(readFileSync(new URL('../../art/actors/dock-specialists/manifest.json',import.meta.url))).enemyTypes;
test('specialists hook, shove, emerge at a marked point and burst without sharing the same attack',()=>{
 for(let i=0;i<extra.length;i++){
  const s=create(extra),z=i===1?4.4:3.6,b=spawn(s,i,{x:0,z});
  advance(s,1.2);
  assert.equal(s.events.find(x=>x.type==='player-hit')?.style,extra[i].attack);
  if(i===0)assert(s.player.z<4.9,'hook pulls toward crane');
  if(i===1)assert(s.player.z>6.4,'shield shoves away');
  if(i===2)assert(b.z>5&&b.mark.z===5.7,'snare emerges at its locked mark');
  if(i===3)assert.equal(b.z,z,'buoy bursts in place');
 }
});
test('the Warden blocks a frontal cut until the shield opens',()=>{
 const s=create(extra),b=spawn(s,1,{x:0,z:3.15});
 b.face=[0,1];b.state='active';select(s,2);press(s,'attack');advance(s,.28);
 assert.equal(b.life,b.maxHp-Math.ceil(WEAPONS[2].power*.35));
 assert(s.events.some(e=>e.type==='shield'));
 const open=create(extra),w=spawn(open,1,{x:0,z:3.15});
 w.state='recover';w.face=[0,1];select(open,2);press(open,'attack');advance(open,.28);
 assert.equal(w.life,w.maxHp-WEAPONS[2].power);
});
test('all 40 variant entries add a verified rule to their underlying enemy behavior',async()=>{
 const {roster,VARIANTS}=await import('./variants.mjs');
 const base=[...spec,...extra],v=roster(base);
 assert.equal(v.length,40);
 assert.equal(new Set(v.map(x=>x.id)).size,40);
 assert(v.every(x=>x.rule&&x.attack&&x.model));
 for(const type of base){
  function fresh(z,variant){const s=create([type]);return [s,spawn(s,0,{x:0,z},variant)];}
  {
   const [s,b]=fresh(-4,'rusher'),[stock,plain]=fresh(-4);
   advance(s,.32);advance(stock,.32);
   assert(s.events.some(e=>e.type==='rush'));assert(b.z>plain.z+.20);
  }
  {
   const [s,b]=fresh(4.3,'bulwark');
   b.face=[0,1];b.state='active';select(s,6);press(s,'attack');advance(s,.17);
   assert(s.events.some(e=>e.type==='shield'));assert.equal(b.life,b.maxHp-Math.ceil(WEAPONS[6].power*.22));
  }
  {
   const [s,b]=fresh(4.35,'feinter');
   advance(s,b.windup+.30);
   assert(s.events.some(e=>e.type==='feint'));
   assert(s.events.filter(e=>e.state==='windup').length>=2);
   assert(Math.abs(b.x)>.3);
  }
  {
   const [s,b]=fresh(4.5,'echo');b.state='recover';
   advance(s,b.recover*.55+.05);
   assert(s.events.some(e=>e.type==='echo'));
   assert.equal(b.state,'windup');assert(b.windReady<b.windup);
  }
  {
   const [s,b]=fresh(4.4,'overload');
   advance(s,1.1);
   assert(s.events.some(e=>e.type==='pulse'));
   assert(s.events.some(e=>e.type==='discharge'));
   assert.equal(b.pulse,0);assert(b.pulseCooldown>0);
  }
  assert.equal(VARIANTS.length,5);
 }
});
