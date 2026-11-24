import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const file = process.argv[2] ??
  'public/assets/wildshard-art/wsc-kit-006-patrol-floor-sweep.glb';
const bytes = await readFile(file);
const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const gltf = await new GLTFLoader().parseAsync(buffer, '');
const parts = [];
gltf.scene.traverse(obj => { if (obj.isMesh) parts.push(obj); });
assert.equal(parts.length, 1);
const [{ geometry, material }] = parts;
assert.equal(geometry.index.count / 3, 312);
assert.equal(geometry.attributes.color.itemSize, 4);
assert.ok(material.isMeshBasicMaterial && material.transparent &&
  material.vertexColors && !material.depthWrite);
geometry.computeBoundingBox();
const { min, max } = geometry.boundingBox;
assert.ok(Math.abs(min.y - .017) < 1e-6 && Math.abs(max.y - .017) < 1e-6);
assert.ok(Math.abs(min.z + 5.8) < 1e-5 && max.z < 0);
const color = geometry.attributes.color;
const alpha = Array.from({ length: color.count }, (_, i) => color.getW(i));
assert.equal(Math.min(...alpha), 0);
assert.ok(Math.max(...alpha) > .6 && Math.max(...alpha) < .76);
assert.ok(bytes.length < 12000 && !gltf.animations.length);
console.log(`${bytes.length} bytes, 312 triangles, RGBA normal alpha blend, Y-up floor offset verified`);
