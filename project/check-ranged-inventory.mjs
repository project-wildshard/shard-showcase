// Smoke-test the exact inventory files in Three.js. Run from the repository root.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {Box3, Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const assetsRoot = new URL('../public/assets/wildshard-art/', import.meta.url);
const receipt = JSON.parse(readFileSync(new URL('./layouts/west-ranged-inventory.json', import.meta.url)));
for (const [id, slug] of [['WSC-GEAR-003', 'bow'], ['WSC-GEAR-004', 'crossbow']]) {
  const spec = receipt.assets[id];
  const blob = readFileSync(new URL(id.toLowerCase() + '-' + slug + '.glb', assetsRoot));
  assert.equal(blob.byteLength, spec.bytes);
  assert.ok(spec.bytes < 65_536);
  assert.equal(createHash('sha256').update(blob).digest('hex'), spec.sha256);

  const data = blob.buffer.slice(blob.byteOffset, blob.byteOffset + blob.byteLength);
  const result = await new GLTFLoader().parseAsync(data, '');
  const dims = new Box3().setFromObject(result.scene).getSize(new Vector3()).toArray();
  const [x, y, z] = spec.blender_dimensions;
  assert.ok([x, z, y].every((v, i) => Math.abs(v - dims[i]) < .0001), id);
  const primitiveTris = [];
  result.scene.traverse(obj => {
    if (!obj.isMesh) return;
    assert.ok(!obj.isSkinnedMesh);
    primitiveTris.push(obj.geometry.index.count / 3);
  });
  assert.equal(primitiveTris.length, spec.primitives);
  assert.equal(primitiveTris.reduce((a, b) => a + b, 0), spec.triangles);
  assert.equal(result.animations.length, 0);
  console.log(id, 'static Three.js reimport passed;', spec.bytes, 'B;', spec.triangles, 'triangles.');
}
