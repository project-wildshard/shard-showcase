import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {categories,examples,read,tabs} from './model.mjs';

assert.deepEqual(tabs,['Map','Character','Finds','Pack','Feats']);
assert.deepEqual(categories.map(r=>r.limit),[8,6,20]);
for(let gold=0;gold<=20;gold++){
  const s=read({gold});
  assert.equal(s.earned,Math.floor(gold/5));
  assert.equal(s.next,gold===20?null:gold+5-gold%5);
  assert.equal(s.remaining,gold===20?0:5-gold%5);
}
assert.throws(()=>read({caches:7}));
assert.throws(()=>read({vistas:-1}));
assert.throws(()=>read({gold:2.5}));
assert.throws(()=>read({pb:{skittles:11}}));
assert.equal(read({eastScrip:12}).collection[1].count,0);
assert.equal(read({pb:{skittles:0}}).records[1].value,'0 / 10');
assert.equal(examples.trail.records[0].value,'1:04.32');
const [out]=process.argv.slice(2);
for(const [id,s] of Object.entries(examples)){
  const svg=readFileSync(join(out,'finds-'+id+'.svg'),'utf8');
  assert(svg.includes('viewBox="0 0 402 874"'));
  for(const r of s.collection)assert(svg.includes('>'+r.count+' / '+r.limit+'</text>'));
  for(const r of s.records)assert(svg.includes('>'+(r.value??'No result yet')+'</text>'));
  assert(svg.includes('ILLUSTRATIVE SAVE'));
  assert(svg.includes('East Scrip chests are separate'));
  assert(!/<script|href="https?:/.test(svg));
}
console.log('FINDS counters, milestones, record formats and two portrait states passed.');
