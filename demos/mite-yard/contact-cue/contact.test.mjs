import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {dirname,join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {test} from 'node:test';
import {CONTACT_END,sampleContact,makeContactBatch} from './contact.mjs';
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url);
const THREE=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href);
const E={point:[.13,.8,2],normal:[0,0,1],tangent:[1,.27,.23]};
test('starts on contact, is deterministic, keeps its small core brief and resets',()=>{
  assert.deepEqual(sampleContact(-1/60,E),[]);
  assert.equal(sampleContact(0,E).length,8);
  assert.deepEqual(sampleContact(1/60,E),sampleContact(1/60,E));
  assert.equal(sampleContact(3/60,E).filter(x=>x.kind==='core').length,1);
  assert.equal(sampleContact(4/60,E).filter(x=>x.kind==='core').length,0);
  assert.deepEqual(sampleContact(CONTACT_END,E),[]);
  assert.throws(()=>sampleContact(0,{...E,tangent:[0,0,1]}),RangeError);
});
test('all spark centers move out of the surface; pulse does not touch post-processing',()=>{
  const t=sampleContact(0,E);
  assert(t[0].radius<=.04&&t[0].reach<=.102);
  for(let n=0;n<=9;n++){
    for(const s of sampleContact(n/60,E)){
      assert(s.center[2]>E.point[2]&&s.gain<=1.2);
      assert(Math.abs(Math.hypot(...s.axis)-1)<.000002);
    }
  }
  const cue=makeContactBatch(THREE);
  const o=cue.object;
  assert.equal(o.count,0);
  cue.draw(0,E);assert.equal(o.count,8);
  assert(o.material.depthTest&&o.material.toneMapped);
  assert.equal(o.material.blending,THREE.NormalBlending);
  const M=new THREE.Matrix4(), C=new THREE.Color();
  o.getMatrixAt(0,M);o.getColorAt(0,C);
  assert(M.elements.every(Number.isFinite)&&C.r>C.g&&C.g>C.b);
  cue.draw(.16,E);assert(!o.visible&&o.count===0);
  cue.draw(0,E);assert(o.visible&&o.count===8);
  cue.dispose();
});
