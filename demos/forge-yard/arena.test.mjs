import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {WEAPONS,create,spawn,press,select,tick,ramOpen,sweepRadius,splitMarks,seedMarks,harrowLine} from './arena.mjs';
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
const terminal=JSON.parse(readFileSync(new URL('../../art/actors/dock-terminal/manifest.json',import.meta.url))).enemyTypes;
test('the terminal rivals use shutters, three pockets, a moving beam, and a lateral strike',()=>{
 const setup=(i,z)=>{const s=create(terminal);return [s,spawn(s,i,{x:0,z})];};
 {
  const [closed,b]=setup(0,3.08);select(closed,11);press(closed,'attack');advance(closed,.17);
  assert.equal(b.life,b.maxHp-Math.ceil(WEAPONS[11].power*.45));
  const [open,k]=setup(0,4.30);advance(open,.16);assert.equal(k.state,'windup');
  select(open,11);press(open,'attack');advance(open,.17);
  assert.equal(k.life,k.maxHp-WEAPONS[11].power);
 }
 {
  const [s,b]=setup(1,3.4);advance(s,1.33);
  assert.deepEqual(s.events.filter(e=>e.type==='seed-burst').map(e=>e.index),[0,1,2]);
  assert(seedMarks(b).every(m=>Math.abs(m.x)<.01));assert.equal(s.player.hp,108);
  const [safe]=setup(1,3.4);advance(safe,.16);advance(safe,.30,[1,0]);advance(safe,.80);
  assert.equal(safe.player.hp,120,'stepping across the trail avoids all three pockets');
 }
 {
  const [s,b]=setup(2,2.70);advance(s,.82);const before=harrowLine(b);
  advance(s,.35);const after=harrowLine(b);
  assert(before[0]<-.45&&after[0]>.28);assert.equal(s.player.hp,105);
  const [safe]=setup(2,2.70);advance(safe,.20);advance(safe,.59,[0,1]);advance(safe,.47);
  assert.equal(safe.player.hp,120,'backstep stays beyond the rotating beam');
 }
 {
  const [s,b]=setup(3,3.65);advance(s,.91);
  assert(b.x>.50&&s.player.hp===120,'slide precedes impact');
  advance(s,.19);assert(s.events.some(e=>e.type==='flank-strike'));assert.equal(s.player.hp,102);
  const [safe]=setup(3,3.65);advance(safe,.22);advance(safe,.33,[-1,0]);advance(safe,.55);
  assert.equal(safe.player.hp,120,'moving away from the locked spot beats the flank');
 }
});
test('all 100 variant entries add a verified rule to their underlying enemy behavior',async()=>{
 const {roster,VARIANTS}=await import('./variants.mjs');
 const base=[...spec,...extra,...ordnance,...foundry,...terminal],v=roster(base);
 assert.equal(v.length,100);
 assert.equal(new Set(v.map(x=>x.id)).size,100);
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

test('base Ram gives one timed punish after a missed charge, never after a landed charge',()=>{
 function fight(sidestep,variant=null){
  const s=create(spec),r=spawn(s,3,{x:0,z:1.15},variant);
  advance(s,.06);
  assert.equal(r.state,'windup');
  if(sidestep)advance(s,.40,[1,0]);
  for(let i=0;i<120&&r.state!=='recover';i++)advance(s,1/60);
  assert.equal(r.state,'recover');return [s,r];
 }
 const [s,r]=fight(true);
 assert(ramOpen(r));assert.equal(s.player.hp,120);
 select(s,7);assert(press(s,'attack'));advance(s,.38);
 assert.equal(r.life,r.maxHp-27);assert(!ramOpen(r));
 assert.deepEqual(s.events.filter(e=>e.counter).map(e=>e.damage),[27]);
 const [missed,late]=fight(true);
 advance(missed,.92);assert(!ramOpen(late));
 const [hit,closed]=fight(false);
 assert(hit.player.hp<120);assert(!ramOpen(closed));
 const [,variant]=fight(true,'rusher');assert(!ramOpen(variant));
});

test('Sentry release damages just inside its visible boundary but not outside, even for Echo tuning',()=>{
 for(const variant of [null,'echo'])for(const [offset,hp] of [[-.005,102],[.005,120]]){
  const s=create(spec),b=spawn(s,0,{x:0,z:2},variant);
  b.state='windup';b.t=b.windReady-1/60;s.player.z=b.z+sweepRadius(b)+offset;
  tick(s,1/60);assert.equal(b.state,'active');assert.equal(s.player.hp,hp);
 }
 const s=create(spec),b=spawn(s,0,{x:-3.1,z:-1.6});
 b.state='windup';b.t=b.windReady-1/60;s.player.x=-3.1;s.player.z=.4;
 assert(s.player.z-b.z<sweepRadius(b));tick(s,1/60);assert.equal(s.player.hp,120,'solid cover still blocks the sweep');
});

test('Breakwater tide warns and sweeps its marked lane once per wave; Forge Yard stays dry',()=>{
 const withTide=create(spec,{breakwater:true});
 withTide.player.x=-5.55;withTide.player.z=0;
 advance(withTide,3.9);
 assert.equal(withTide.surge.section.phase,'warn');
 assert.equal(withTide.player.hp,120);
 advance(withTide,2.25);
 assert.equal(withTide.surge.hits,1);
 assert.equal(withTide.player.hp,108);
 advance(withTide,9.45);
 assert.equal(withTide.surge.hits,2);
 assert.equal(withTide.player.hp,96);
 assert(withTide.events.every(e=>e.enemy===null&&e.style==='surge'&&e.damage===12));
 const clear=create(spec,{breakwater:true});clear.player.x=-5.55;clear.player.z=0;
 advance(clear,4.3);advance(clear,.31,[1,0]);advance(clear,2.1);
 assert.equal(clear.surge.hits,0);
 const original=create(spec);original.player.x=-5.55;original.player.z=0;advance(original,6.25);
 assert.equal(original.surge,null);assert.equal(original.player.hp,120);
 const dodge=create(spec,{breakwater:true});dodge.player.x=-5.55;dodge.player.z=-1;
 dodge.player.face=[1,0];advance(dodge,5.32);assert(press(dodge,'dodge'));advance(dodge,.85);
 assert.equal(dodge.surge.hits,0);
});
