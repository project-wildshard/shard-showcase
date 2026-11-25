// Inspect exact fixture exports in Three.js without a browser or engine.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {Box3,Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const read = (name) => readFileSync(new URL(name,import.meta.url));
const stamp = JSON.parse(read('./layouts/w2b-rook-forge-fit.json'));
const old = JSON.parse(read('./layouts/w2b-rook-counter-study.json'));
assert.equal(stamp.counter_sha256,old.donors.counter.sha256);
assert.equal(stamp.actor_sha256,old.actor.sha256);
assert.equal(stamp.actor_frame,old.actor.frame);
assert.deepEqual(stamp.forge_labels,['IRON','STEEL','ALLOY','TITANIUM']);
const assetPath = '../public/assets/wildshard-art/';
const digest = b => createHash('sha256').update(b).digest('hex');
assert.equal(digest(read(assetPath+old.donors.counter.file)),stamp.counter_sha256);
assert.equal(digest(read(assetPath+'wsc-actor-018-tinker-rook.glb')),stamp.actor_sha256);
for(const [key,spec] of Object.entries(stamp.exports)){
  const buf=read(assetPath+'w2b-rook-'+key+'.glb');
  assert.equal(buf.length,spec.bytes);
  assert.equal(digest(buf),spec.sha256);
  const {scene,animations}=await new GLTFLoader().parseAsync(Uint8Array.from(buf).buffer,'');
  const mesh=[];
  scene.traverse(o=>{if(o.isMesh)mesh.push(o)});
  const bounds=new Box3().setFromObject(scene);
  const size=bounds.getSize(new Vector3());
  assert.ok(Math.abs(bounds.min.y)<.0001);
  assert.ok(Math.abs(size.x-(key==='forge-tray'?.64:.46))<.0001);
  assert.ok(size.z<(key==='forge-tray'?.38:.27));
  assert.ok(animations.length===0 && mesh.every(o=>!o.isSkinnedMesh && !o.material.map));
  assert.equal(mesh.length,spec.draws);
  assert.equal(mesh.reduce((n,o)=>n+o.geometry.index.count/3,0),spec.triangles);
  assert.equal(mesh.filter(o=>o.name.startsWith('Replaceable_face')).length,key==='bench-placard'?2:0);
  console.log(key,spec.bytes,'bytes;',spec.triangles,'tris;',spec.draws,'mesh draws.');
}
