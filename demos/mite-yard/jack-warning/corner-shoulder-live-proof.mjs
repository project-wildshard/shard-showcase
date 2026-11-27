import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const [nativePath,lookPath]=process.argv.slice(2);
if(!nativePath||!lookPath)throw Error('Usage: node corner-shoulder-live-proof.mjs NATIVE_OUTPUT LOOK_OUTPUT');
const load=p=>JSON.parse(readFileSync(join(p,'proof.json'),'utf8')).left;
const native=load(nativePath), manual=load(lookPath);
const dist=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
const offset=r=>r.position.map((x,i)=>x-r.native[i]);
const lookStart=manual.liveShoulder.findIndex(r=>r.look);
assert(lookStart>0,'Native look was not detected');
const observed=manual.liveShoulder.slice(lookStart);
assert(observed.every(r=>r.yielded));
assert(observed.some(r=>!r.look));
assert.equal(observed.at(-1).weight,0);
assert(observed[0].weight<manual.liveShoulder[lookStart-1].weight);
assert(observed.some(r=>dist(r.basis,manual.liveShoulder[lookStart-1].basis)>.01),'No native camera turn');
assert(manual.pointerEvents.some(e=>e.frame===manual.attack.frame+12&&e.trusted&&e.element==='CANVAS'));
assert.equal(native.contact.frame,manual.contact.frame);
assert.equal(native.contact.action,'sword1');
assert.equal(native.contact.hp,native.start.hp);
assert(native.liveShoulder.every(r=>!r.blocked&&!r.look&&!r.yielded));
assert(native.liveShoulder.every((r,i)=>!i||r.frame===native.liveShoulder[i-1].frame+1));
const hit=native.liveShoulder.find(r=>r.frame===native.contact.frame);
assert(hit.applied&&hit.weight>.9);
assert.equal(native.liveShoulder.at(-1).weight,0);
const speeds=native.liveShoulder.slice(1).map((r,i)=>dist(offset(r),offset(native.liveShoulder[i])));
assert(Math.max(...speeds)<.08);
const images=native.liveImages.map(([stock,composed])=>{
 assert.equal(stock.frame,composed.frame);
 assert(dist(stock.core,composed.core)<1e-6);
 return {frame:stock.frame,stockSpanPx:dist(stock.base,stock.tip),composedSpanPx:dist(composed.base,composed.tip),
  positionDelta:dist(stock.camera,composed.camera),coreDeltaPx:dist(stock.core,composed.core)};
});
assert.deepEqual(images.map(r=>r.frame-native.attack.frame),[6,11,19,36]);
assert(images[1].composedSpanPx>images[1].stockSpanPx);
console.log(JSON.stringify({referenceCommit:'3afcd880b397e9703e906a7e66b42e8447e59519',
 viewport:[402,874],simHz:60,tap:native.attack.frame,damage:native.contact.frame,
 contactHeroHp:native.contact.hp,contactJackHp:[native.start.enemyHp,native.contact.enemyHp],
 drawSampleCount:native.liveShoulder.length,returnToStockFrame:native.liveShoulder.find(r=>r.frame>hit.frame&&!r.applied).frame,
 maxAddedStepMeters:Math.max(...speeds),contactWeight:hit.weight,images,
 manualLook:{start:observed[0].frame,lastHeld:observed.findLast(r=>r.look).frame,
  stockBy:observed.find(r=>!r.weight).frame,staysReleased:observed.every(r=>r.yielded)}},null,2));
