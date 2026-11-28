import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {WEAPONS,create,spawn,press,select,tick,splitMarks} from './arena.mjs';
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
const ordnance=JSON.parse(readFileSync(new URL('../../art/actors/dock-ordnance/manifest.json',import.meta.url))).enemyTypes;
test('ordnance follows four different telegraph and damage rules',()=>{
 const setup=(i,z)=>{const s=create(ordnance);return [s,spawn(s,i,{x:0,z})];};
 {
  const [s,b]=setup(0,2.5);advance(s,1.27);
  assert.equal(s.events.filter(e=>e.type==='salvo-shot').length,3);
  assert.equal(s.player.hp,93);assert.equal(b.z,2.5,'the turret does not chase during a burst');
  const [clear]=setup(0,2.5);advance(clear,.22);advance(clear,.38,[1,0]);advance(clear,.67);
  assert.equal(clear.player.hp,120,'once aimed, the salvo does not track sideways');
 }
 {
  const [s,b]=setup(1,3.4);advance(s,1.05);
  assert(s.events.some(e=>e.type==='player-hit'&&e.style==='lunge'));
  assert(b.z>4.2,'the blade carries through the locked lane');
 }
 {
  const [s,b]=setup(2,1.1);advance(s,.88);
  assert(s.events.some(e=>e.type==='mortar-launch'));assert.equal(s.player.hp,120);
  assert.equal(b.mark.z,5.7);advance(s,.36);assert.equal(s.player.hp,98);
  const [clear]=setup(2,1.1);advance(clear,.68);advance(clear,.42,[1,0]);advance(clear,.30);
  assert.equal(clear.player.hp,120,'move after launch to leave the committed impact');
 }
 {
  const [across]=setup(3,3.95);advance(across,.40);advance(across,.26,[1,0]);advance(across,.25);
  assert.equal(across.player.hp,103,'a short sideways move stays in the transverse strip');
  const [back]=setup(3,3.95);advance(back,.40);advance(back,.26,[0,1]);advance(back,.25);
  assert.equal(back.player.hp,120,'stepping back exits the transverse strip');
 }
});
const foundry=JSON.parse(readFileSync(new URL('../../art/actors/dock-foundry/manifest.json',import.meta.url))).enemyTypes;
test('foundry types telegraph pull and release, alternating cuts, a safe seam and recoil',()=>{
 const setup=(i,z)=>{const s=create(foundry);return [s,spawn(s,i,{x:0,z})];};
 {
  const [s,b]=setup(0,3.45);
  advance(s,1.11);assert(s.player.z<5.35&&s.player.hp===120,'intake displaces before it deals damage');
  advance(s,.25);assert(s.events.some(e=>e.type==='vacuum-release'));assert.equal(s.player.hp,102);
  const [safe]=setup(0,3.45);advance(safe,.19);advance(safe,.32,[1,0]);advance(safe,1.0);
  assert.equal(safe.player.hp,120,'leaving the fixed cone avoids the release');
 }
 {
  const [s,b]=setup(1,3.95);
  advance(s,1.17);
  assert.deepEqual(s.events.filter(e=>e.type==='split-strike').map(e=>e.index),[0,1]);
  assert(s.player.hp<=107);
  assert(splitMarks(b,.54).every(m=>Math.abs(m.x)>.53));
 }
 {
  const [s]=setup(2,2.65);advance(s,1.33);
  assert.equal(s.player.hp,120,'the gap between pylons is safe');
  const [left]=setup(2,2.65);advance(left,.18);advance(left,.265,[-1,0]);advance(left,.57);
  assert.equal(left.player.hp,102,'a flank marker hits at its own timing');
 }
 {
  const [s,b]=setup(3,4.25);advance(s,1.22);
  assert.equal(s.player.hp,100);assert(b.z<3.26,'jet recoil moves winch away from the marked target');
 }
});
test('all 80 variant entries add a verified rule to their underlying enemy behavior',async()=>{
 const {roster,VARIANTS}=await import('./variants.mjs');
 const base=[...spec,...extra,...ordnance,...foundry],v=roster(base);
 assert.equal(v.length,80);
 assert.equal(new Set(v.map(x=>x.id)).size,80);
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
   b.face=[0,1];b.state='active';b.mark={x:0,z:5.7};select(s,6);press(s,'attack');advance(s,.17);
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
