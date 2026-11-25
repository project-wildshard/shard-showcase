import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { AnimationMixer, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const out = process.argv[2];
const stage = JSON.parse(await readFile(join(out, 'lookout-breeze-staging.json')));
const specs = JSON.parse(await readFile(join(out, 'lookout-breeze-assets.json')));
const report = {};
async function load(path) {
  const b = await readFile(path);
  const loader = new GLTFLoader();
  return loader.parseAsync(b.buffer.slice(b.byteOffset, b.byteOffset+b.byteLength),'');
}
const v = new Vector3();
for (const name of ['fern', 'verge']) {
  const file = `w11-lookout-${name}`;
  const rest = await load(new URL(`../../../public/assets/wildshard-art/${file}.glb`, import.meta.url));
  const live = await load(join(out,`${file}-breeze.glb`));
  const a = rest.scene.children[0], b = live.scene.children[0];
  assert.ok(a.isMesh && b.isMesh);
  assert.equal(live.animations.length, 1);
  for (const k of ['position', 'normal', 'color'])
    assert.deepEqual(a.geometry.attributes[k].array, b.geometry.attributes[k].array);
  assert.deepEqual(a.geometry.index.array,b.geometry.index.array);
  assert.equal(a.material.side,b.material.side);
  assert.equal(a.material.roughness,b.material.roughness);
  const [clip] = live.animations, [track] = clip.tracks;
  const m = new AnimationMixer(live.scene);
  m.clipAction(clip).play();
  assert.ok(Math.abs(clip.duration-specs[name].period_s)<1e-6);
  assert.equal(track.times.length, specs[name].keys);
  assert.deepEqual([...track.values.slice(-4)], [0,0,0,0]);
  assert.deepEqual([...track.values.slice(0,4)], [0,0,0,0]);
  const p = a.geometry.attributes.position;
  let maxMove = 0, minPath = Infinity, checked = 0;
  for (let i=0; i<track.times.length; i++) {
    const t = track.times[i];
    m.setTime(t);
    assert.ok(b.morphTargetInfluences.every(x => x >= 0 && x <= 1));
    for (let j=0; j<p.count; j++) {
      b.getVertexPosition(j, v);
      const delta = Math.hypot(v.x-p.getX(j),v.z-p.getZ(j));
      assert.equal(v.y, p.getY(j));
      if (p.getY(j) <= .045) assert.equal(delta, 0);
      maxMove = Math.max(maxMove, delta);
      for (const { xyz, yaw, scale } of stage.filter(s => s.name===name)) {
        const x = xyz[0] + scale*(v.x*Math.cos(yaw)+v.z*Math.sin(yaw));
        // X interpolates linearly between keys and cannot switch sides across the strip.
        assert.equal(Math.sign(x),Math.sign(xyz[0]));
        minPath = Math.min(minPath,Math.abs(x)-1);
        checked++;
      }
    }
  }
  m.setTime(0.37);
  const first = [...b.morphTargetInfluences];
  m.setTime(clip.duration+0.37);
  assert.ok(b.morphTargetInfluences.every((w,i)=>Math.abs(w-first[i])<1e-6));
  assert.ok(maxMove > .024 && maxMove < specs[name].width_extension_bound_m + 1e-6);
  assert.ok(minPath > .02);
  report[name] = { ...specs[name], max_move_m: +maxMove.toFixed(6),
                   exact_swept_path_margin_m: +minPath.toFixed(6), world_vertex_knots: checked };
}
await writeFile(join(out,'lookout-breeze-proof.json'),JSON.stringify({
  scope:'Optional Blender staging and headless Three AnimationMixer, no shipped terrain placement or performance result.',
  stage, variants:report
},null,2)+'\n');
console.log(report);
