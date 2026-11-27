import assert from 'node:assert/strict';
import {readFileSync,statSync} from 'node:fs';
import {join} from 'node:path';

const [root]=process.argv.slice(2);
if(!root)throw Error('Usage: node corner-finish-proof.mjs FINISH_REPLAY_DIR');
const r=JSON.parse(readFileSync(join(root,'proof.json'),'utf8')).left;
const {events,samples,start}=r.finish;
const contents=['before','strike','collapse','breakup'].map(k=>statSync(join(root,'finish-'+k+'.png')).size);
assert(contents.every(n=>n>10000));
const die=samples.find(x=>x.state==='dead'), collapse=samples.find(x=>x.action==='death'&&x.poseT>=.48);
const remove=samples.find(x=>!x.inList);
assert.equal(start.hp,8);
assert.equal(r.contact.action,'sword1');
assert.equal(die.frame,r.contact.frame);
assert.equal(die.hp,0);
assert.equal(die.targetable,false);
assert.equal(die.alive,false);
assert(die.inList&&die.inScene);
assert(collapse.frame>die.frame&&collapse.frame<remove.frame);
assert(!remove.inScene&&!remove.target&&!remove.targetable);
assert(samples.slice(samples.indexOf(remove)).every(s=>!s.inScene&&!s.inList&&!s.target&&!s.targetable));
assert(samples.every(s=>s.heroHp===r.start.hp));
const before=samples.findLast(s=>s.frame<die.frame);
assert(before.hp>0&&before.hp<12&&before.inScene);
const picks={};
for(const key of ['kill','kill-xp','scrip-drop','breakup','remove']){
 const filtered=events.filter(e=>e.kind===key);
 assert.equal(filtered.length,1,key);
 picks[key]=filtered[0];
}
for(const key of ['kill','kill-xp','scrip-drop'])assert.equal(picks[key].frame,die.frame,key);
for(const key of ['breakup','remove'])assert.equal(picks[key].frame,remove.frame,key);
assert.equal(die.kills,start.kills+1);
assert.equal(samples.at(-1).kills,die.kills);
assert.equal(die.level,start.level);
assert.equal(die.xp,start.xp+picks['kill-xp'].amount);
assert.equal(samples.at(-1).xp,die.xp);
assert(picks['scrip-drop'].amount>0);
const clearTarget=samples.find(s=>s.frame>=die.frame&&!s.target);
assert(clearTarget.frame<=die.frame+2);
assert(samples.some(s=>s.frame<die.frame&&s.target));
assert(r.pointerEvents.some(e=>e.name==='pointerdown'&&e.act==='attack'&&e.trusted));
console.log(JSON.stringify({referenceCommit:'3afcd880b397e9703e906a7e66b42e8447e59519',
 viewport:[402,874],fixture:'same native dock crate with enemy at 8 HP at setup',simHz:60,
 chargeBlockedFrame:r.recovery.frame,tapFrame:r.attack.frame,preLethalHp:before.hp,die,collapse,remove,
 targetClearedFrame:clearTarget.frame,followedThroughFrame:samples.at(-1).frame,events},null,2));
