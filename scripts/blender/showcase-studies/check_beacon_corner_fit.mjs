import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {Box3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const base = new URL('../../../public/assets/wildshard-art/', import.meta.url);
const root = 'wsc-kit-007-storm-beacon';
async function load(suffix) {
  const b = await readFile(new URL(root + suffix + '.glb', base));
  const {scene} = await new GLTFLoader().parseAsync(
    b.buffer.slice(b.byteOffset,b.byteOffset+b.length), ''
  );
  let triangles = 0;
  scene.traverse(o => {
    if (o.isMesh) triangles += (o.geometry.index?.count ?? o.geometry.attributes.position.count)/3;
  });
  return {bounds: new Box3().setFromObject(scene), scene, bytes: b.length, triangles};
}
const [tower, lamp, mount] = await Promise.all(['','-charged-lamp','-seat'].map(load));
const deck = mount.scene.getObjectByName('Square_metal_seat');
assert.ok(deck);
const d = new Box3().setFromObject(deck);
const near = (a, b) => assert.ok(Math.abs(a-b) < 1e-5, `${a} differs from ${b}`);
near(tower.bounds.min.y, 0);
near(mount.bounds.min.y, 0);
near(12+d.max.y+tower.bounds.max.y, 20);
near(tower.bounds.max.x, -tower.bounds.min.x);
near(tower.bounds.max.z, -tower.bounds.min.z);
assert.ok(d.max.x >= tower.bounds.max.x+.33 && d.max.z >= tower.bounds.max.z+.33);
assert.ok(12+d.max.y+lamp.bounds.min.y > 19.20 && 12+d.max.y+lamp.bounds.max.y < 19.79);
assert.deepEqual([mount.triangles, mount.bytes], [496,45096]);
console.log('Three import: seat contact, 20 m crown, lamp range, footprint, 496 triangles / 45,096 B verified.');
