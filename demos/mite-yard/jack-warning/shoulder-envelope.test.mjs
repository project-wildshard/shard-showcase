import assert from 'node:assert/strict';
import {test} from 'node:test';
import {makeShoulderEnvelope} from './shoulder-envelope.mjs';
test('framing rises through the first cut, returns smoothly, and does not move before the tap',()=>{
 const f=makeShoulderEnvelope();
 let last=0;
 const seen=Array.from({length:45},(_,i)=>{
  const x=f({age:(i-1)/60,engaged:true,third:true});
  assert(Math.abs(x.weight-last)<=7/60+1e-10);
  last=x.weight;return last;
 });
 assert.equal(seen[0],0);
 assert(seen[12]>.9);
 assert.equal(seen.at(-1),0);
});
test('manual look yields permanently for the tap; first person clears instantly',()=>{
 const f=makeShoulderEnvelope();
 for(let i=0;i<12;i++)f({age:i/60,engaged:true,third:true});
 const first=f({age:.2,engaged:true,look:true,third:true});
 assert(first.yielded&&first.weight<1);
 for(let i=0;i<10;i++)f({age:.2+i/60,engaged:true,third:true});
 assert.deepEqual(f({age:.22,engaged:true,third:true}),{weight:0,yielded:true});
 const g=makeShoulderEnvelope();
 for(let i=0;i<12;i++)g({age:i/60,engaged:true,third:true});
 assert.deepEqual(g({age:.3,engaged:true,third:false}),{weight:0,yielded:true});
});
