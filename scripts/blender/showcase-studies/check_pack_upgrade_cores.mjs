import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Box3, DoubleSide, Raycaster, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const dir = new URL('../../../public/assets/wildshard-art/', import.meta.url);
const file = process.argv[2] ?? new URL('w2a-pack-upgrade-cores.glb', dir);
const raw = await readFile(file);
const data = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
const { scene, animations } = await new GLTFLoader().parseAsync(data, '');
const names = ['Hydraulic Heart', 'Plate Core', "Foreman's Capacitor"];
assert.equal(scene.children.length,names.length);
assert.deepEqual(scene.children.map(n=>n.userData.name), names);
assert.equal(animations.length,0);
let tris=0;
for (const part of scene.children) {
  part.position.set(0,0,0);
  part.updateMatrixWorld(true);
  const bounds=new Box3().setFromObject(part);
  assert.ok(Math.abs(bounds.min.x+bounds.max.x)<.00002);
  assert.ok(Math.abs(bounds.min.y)<.00002);
  assert.ok(Math.abs(bounds.min.z+bounds.max.z)<.00002);
  part.traverse(o=>{
    if (!o.isMesh) return;
    const p=o.geometry.getAttribute('position'),idx=o.geometry.index;
    assert.ok(p.array.every(Number.isFinite) && idx.array.every(i=>i<p.count));
    tris+=idx.count/3;
    o.material.side=DoubleSide;
  });
}
const plate=scene.children[1];
const vertical=(x,z)=>new Raycaster(new Vector3(x,1,z), new Vector3(0,-1,0),0,2)
  .intersectObject(plate,true).length;
let clear=0,touch=0;
for (const x of [-.036,-.018,0,.018,.036]) {
  for (const z of [-.04,-.02,0,.02,.04]) {
    assert.equal(vertical(x,z),0);
    clear++;
  }
}
for (const x of [-.14,-.12,.12,.14]) {
  for (const z of [-.04,-.02,0,.02,.04]) {
    assert.ok(vertical(x,z)>0);
    touch++;
  }
}
console.log(JSON.stringify({ bytes:raw.length, triangles:tris,names,
  plateApertureClearRays:clear,plateFlanksHitRays:touch },null,2));
