// Run from the repository root with the project's pinned Three.js installed.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {AdditiveBlending, Box3, DoubleSide, Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

/** Applies the E7b display blending to this standalone mesh only, emits no light. */
export function configureNightShiftBeam(root) {
  const visible = [];
  root.traverse(node => {
    if (node.isMesh) visible.push(node);
  });
  const [mesh] = visible;
  if (visible.length !== 1 || mesh.geometry.getAttribute('color')?.itemSize !== 4
      || !mesh.material.isMeshBasicMaterial) throw new Error('Expected one unlit RGBA beam mesh');
  const fx = mesh.material.clone();
  fx.blending = AdditiveBlending;
  fx.transparent = true;
  fx.depthWrite = false;
  fx.depthTest = true;
  fx.side = DoubleSide;
  fx.forceSinglePass = true;
  fx.toneMapped = false;
  mesh.material = fx;
  return mesh;
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  const receipt = JSON.parse(readFileSync(new URL('./layouts/e7b-night-shift-vfx.json', import.meta.url)));
  const assets = new URL('../public/assets/wildshard-art/', import.meta.url);
  for (const [type, name] of [['beam', 'e7b-headlamp-beam'], ['chevron', 'e7b-hi-vis-chevron']]) {
    const file = fileURLToPath(new URL(name + '.glb', assets));
    const bytes = readFileSync(file);
    const exact = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const pkg = await new GLTFLoader().parseAsync(exact, '');
    const spec = receipt[type];
    assert.equal(bytes.byteLength, spec.bytes);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), spec.sha256);
    assert.equal(pkg.animations.length, 0);
    let tris = 0;
    pkg.scene.traverse(o => {
      assert.ok(!o.isLight);
      if (o.isMesh) tris += o.geometry.index.count / 3;
    });
    assert.equal(tris, spec.triangles);
    if (type === 'beam') {
      const mesh = configureNightShiftBeam(pkg.scene);
      const dimensions = new Box3().setFromObject(pkg.scene);
      assert.ok(Math.abs(dimensions.min.z + spec.length_m) < 0.0001);
      assert.ok(Math.abs(dimensions.max.z) < 0.0001);
      assert.ok(dimensions.getSize(new Vector3()).x > .8);
      assert.equal(mesh.material.blending, AdditiveBlending);
      assert.ok(mesh.material.depthTest && !mesh.material.depthWrite && !mesh.material.toneMapped);
      const alpha = mesh.geometry.getAttribute('color');
      let peak = 0;
      for (let i=0; i<alpha.count; i++) {
        peak = Math.max(peak, alpha.getW(i));
        if (mesh.geometry.attributes.position.getZ(i) < -2.7) assert.equal(alpha.getW(i), 0);
      }
      assert.equal(peak, .25);
    }
    console.log(name, tris, 'triangles,', bytes.length, 'bytes, zero lights.');
  }
}
