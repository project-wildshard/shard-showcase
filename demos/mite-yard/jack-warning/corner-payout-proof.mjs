import assert from 'node:assert/strict';
import {readFileSync,statSync} from 'node:fs';
import {join} from 'node:path';

const [root]=process.argv.slice(2);
if(!root)throw Error('Usage: node corner-payout-proof.mjs PAYOUT_REPLAY_DIR');
const r=JSON.parse(readFileSync(join(root,'proof.json'),'utf8')).left;
const {events,samples,start,saved}=r.finish;
const {before,after}=r.reopened;
const drops=events.filter(e=>e.kind==='scrip-drop'), credits=events.filter(e=>e.kind==='scrip-credit');
assert.equal(drops.length,1);
assert.equal(drops[0].frame,r.contact.frame);
const drop=drops[0], atHit=samples.find(s=>s.frame===drop.frame);
assert.equal(atHit.scrip,start.scrip);
assert.equal(atHit.scripOrbs.reduce((sum,n)=>sum+n,0),drop.amount);
assert.equal(credits.length,atHit.scripOrbs.length);
assert.deepEqual(credits.map(e=>e.amount).sort(),atHit.scripOrbs.slice().sort());
assert(credits.every(e=>e.frame>drop.frame&&e.amount>0));
const end=credits.at(-1).frame, wallet=start.scrip+drop.amount;
const atPickup=samples.find(s=>s.frame===end);
assert.equal(atPickup.scrip,wallet);
assert(atPickup.scripOrbs.length===0);
assert(samples.filter(s=>s.frame>=end).every(s=>s.scrip===wallet&&s.scripOrbs.length===0));
assert(samples.filter(s=>s.frame>=end).every(s=>s.heroHp===r.start.hp));
assert(Math.hypot(...atPickup.hero.map((x,i)=>x-atHit.hero[i]))<.1);
assert(!r.pointerEvents.some(e=>e.frame>r.attack.frame+2&&e.name==='pointerdown'));
assert.equal(events.filter(e=>e.kind==='kill').length,1);
const xp=events.filter(e=>e.kind==='kill-xp');
assert.equal(xp.length,1);
const expected={scrip:wallet,xp:start.xp+xp[0].amount,palletKills:start.kills+1,level:start.level,golden:false};
assert.deepEqual(before,expected);
assert.deepEqual(after,expected);
assert.equal(saved.scrip,wallet);
assert.equal(saved.xp,expected.xp);
assert.equal(saved.palletKills,expected.palletKills);
assert(saved.frame>=end+20&&saved.playTime>5);
assert(statSync(join(root,'finish-pickup.png')).size>10000);
console.log(JSON.stringify({referenceCommit:'3afcd880b397e9703e906a7e66b42e8447e59519',
 viewport:[402,874],simHz:60,fixture:'native dock crate replay, enemy staged at 8 HP',
 nativeDamageFrame:r.contact.frame,orbValues:atHit.scripOrbs,drop,credits,zeroDuplicateCreditUntil:samples.at(-1).frame,
 wallet:[start.scrip,wallet],heroMovedAfterHit:Math.hypot(...atPickup.hero.map((x,i)=>x-atHit.hero[i])),
 saved,continue:{before,after}},null,2));
