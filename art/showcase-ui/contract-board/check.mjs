import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {describe,demoRows,previews} from './states.mjs';
const [active,...future]=demoRows;
assert.equal(active.need,20);
assert.equal(active.level,1);
for (const [k,s] of Object.entries(previews)) {
  const svg=await readFile(join(process.argv[2],`e1f-contract-${k}.svg`),'utf8');
  assert.match(svg,/width="402" height="874" viewBox="0 0 402 874"/);
  assert.equal(describe(active,s).count,k==='progress'?8:20);
  for (const row of future) {
    const got=describe(row,s);
    assert.equal(got.locked,true);
    assert.equal(got.rewards,undefined);
    assert.ok(svg.includes('Opens at LV '+row.level));
  }
  assert.equal(svg.includes('Wall trophy  ·  Pest Control'),k!=='repeat');
  assert.equal(svg.includes('FIRST CLAIM READY'),k==='first');
  assert.equal(svg.includes('REPEAT READY'),k==='repeat');
  assert.ok(!svg.includes('Scrip and parts'));
}
assert.deepEqual(describe(active,previews.repeat).rewards,['20 Scrip']);
assert.deepEqual(describe(active,previews.first).rewards,['20 Scrip','Wall trophy','Pest Control']);
console.log('3 portrait states: first/repeat reward separation, LV6/LV12 locked, 402×874 SVGs');
function luma(hex) {
  const s=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255);
  return s.map(x=>x<.04045?x/12.92:((x+.055)/1.055)**2.4)
          .reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);
}
for(const [ink,ground] of [['#242922','#93948f'],['#222b28','#93948f'],
  ['#3b3025','#e7d4ac'],['#fff3d8','#304937'],['#f6d8a0','#754e36']]) {
  const a=luma(ink),b=luma(ground);
  assert.ok((Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5);
}
console.log('5 ink/background pairs meet 4.5:1 at the specified gradient stops');
