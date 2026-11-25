// Verify the exact GLBs and archive-chute envelope in Three.js.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {DoubleSide, Matrix4, Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const receipt = JSON.parse(readFileSync(new URL('./layouts/w10a-chute-verge-proof.json',import.meta.url)));
const basis = new Vector3();
const mount = new Matrix4();
let verge = Infinity, checked = 0;
for (const [key, spec] of Object.entries(receipt.exports)) {
  const path = new URL(`../public/assets/wildshard-art/w10a-verge-${key}.glb`,import.meta.url);
  const buf = readFileSync(path);
  assert.equal(buf.length,spec.bytes);
  assert.equal(createHash('sha256').update(buf).digest('hex'),spec.sha256);
  const {scene,animations} = await new GLTFLoader().parseAsync(Uint8Array.from(buf).buffer,'');
  scene.updateMatrixWorld(true);
  assert.equal(animations.length,0);
  const placements = receipt.placements.filter(v => v.prototype === key);
  assert.equal(placements.length,key==='stubble'?32:14);
  let tris=0,draws=0;
  scene.traverse(mesh => {
    if (!mesh.isMesh) return;
    assert.ok(!mesh.isSkinnedMesh && !mesh.material.map);
    assert.equal(mesh.material.side,DoubleSide);
    tris += mesh.geometry.index.count/3;
    draws++;
    const attr = mesh.geometry.attributes.position;
    for (const {world_three_xyz_m:[x,y,z],yaw_radians:yaw,scale:s} of placements) {
      mount.makeRotationY(yaw).multiplyScalar(s);
      mount.elements[15]=1;
      mount.setPosition(x,y,z);
      for (let i=0; i<attr.count; i++) {
        basis.fromBufferAttribute(attr,i).applyMatrix4(mesh.matrixWorld).applyMatrix4(mount);
        assert.ok(Number.isFinite(basis.x+basis.y+basis.z));
        verge=Math.min(verge,Math.abs(basis.x-receipt.threshold_three_xz_m[0])-6);
        assert.ok(basis.y>=-.019 && basis.y<=.95);
        checked++;
      }
    }
  });
  assert.equal(tris,spec.triangles);
  assert.equal(draws,spec.draws);
  console.log(key, spec.bytes,'bytes;',tris,'triangles across',draws,'materials.');
}
assert.equal(checked,receipt.sampled_reimported_vertices);
assert.ok(Math.abs(verge-receipt.min_lateral_margin_from_lane_m)<.00011);
console.log(checked,'placed vertices checked; minimum chute gap',verge.toFixed(4),'m.');
