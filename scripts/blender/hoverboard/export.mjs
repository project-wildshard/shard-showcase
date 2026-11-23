/** Convert the exact native model to static glTF without changing the game. Requires Node 24. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { createRequire, registerHooks, stripTypeScriptTypes } from 'node:module';
import { join, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , enginePath, outputPath] = process.argv;
assert(enginePath && outputPath, 'Usage: node export.mjs ENGINE_PACKAGE_DIR OUTPUT_DIR');
const engine = pathToFileURL(resolve(enginePath) + sep).href;
const read = file => readFileSync(new URL(file, engine));
const version = JSON.parse(read('package.json')).version;
const commit = 'f61079f816be881c405796b597e5523fdd9061df';
const source = 'src/client/engine/render/hoverboardGeometry.ts';
const digest = createHash('sha256').update(read(source)).digest('hex');
assert.equal(version, '0.1.44');
assert.equal(digest, '26be39578e361c00c2ec2b000cf16b888b73e4ca67ab9cc24674f48fa3bb80fd');
const req = createRequire(new URL('package.json', engine));
const three = await import(new URL('./three.module.js', pathToFileURL(req.resolve('three'))));
assert.equal(three.REVISION, '186');

// Node cannot strip TypeScript under node_modules itself. Apply that conversion only to the pinned package.
registerHooks({
  resolve(specifier, context, next) {
    return next(context.parentURL?.startsWith(engine) && specifier.startsWith('.') &&
      !/\.[a-z]+$/i.test(specifier) ? specifier + '.ts' : specifier, context);
  },
  load(uri, context, next) {
    if (uri.startsWith(engine) && uri.endsWith('.ts')) {
      return { format: 'module', shortCircuit: true,
        source: stripTypeScriptTypes(readFileSync(new URL(uri), 'utf8')) };
    }
    return next(uri, context);
  },
});
const { buildHoverboard } = await import(new URL(source, engine));
const original = new three.Group();
buildHoverboard(original);
const [board, halo] = original.children;
const geometry = board.geometry;
assert.equal(original.children.length, 2);
assert.equal(geometry.index, null);
assert.equal(geometry.attributes.position.count, 3696);
assert.equal(halo.geometry.index.count, 144);

const parts = [
  ['Dark deck', 524, 0x1a1d24, .55, .35, 0, 0],
  ['Matte grip', 140, 0x2b303a, .95, .05, 0, 0],
  ['Cyan rim, inlay and nose lamp', 376, 0x0a1a22, .40, 0, 1, 2.2],
  ['Repulsors', 192, 0x0d2a36, .30, .20, 2, 3],
];
const filename = 'wsc-prop-032-hoverboard.glb';
const doc = {
  asset: { version: '2.0', generator: 'Wildshard native hoverboard static exporter',
    extras: { engine: version, commit, source, sourceSha256: digest, three: '0.186.0',
      restLiftM: .061, nose: '-Z', omitted: '48 live additive halo triangles and pulse' } },
  extensionsUsed: ['KHR_materials_emissive_strength'],
  scene: 0, scenes: [{ nodes: [0] }], nodes: [{ name: 'Hoverboard', mesh: 0 }],
  meshes: [{ name: 'Native geometry, static material groups', primitives: [] }],
  materials: [], buffers: [], bufferViews: [], accessors: [],
};
const segments = [];
let head = 0;
function floats(values, width, isPos = false) {
  const buffer = Buffer.alloc(values.length * 4);
  const lo = Array(width).fill(Infinity), hi = Array(width).fill(-Infinity);
  values.forEach((f, i) => {
    buffer.writeFloatLE(f, i * 4);
    const k = i % width;
    lo[k] = Math.min(lo[k], f);
    hi[k] = Math.max(hi[k], f);
  });
  const bufferView = doc.bufferViews.push({ buffer: 0, byteOffset: head, byteLength: buffer.length, target: 34962 }) - 1;
  segments.push(buffer);
  head += buffer.length;
  return doc.accessors.push({ bufferView, componentType: 5126, count: values.length / width,
    type: width === 3 ? 'VEC3' : 'VEC2', ...(isPos ? { min: lo, max: hi } : {}) }) - 1;
}
let start = 0;
for (const [name, tris, hex, roughness, metallic, id, emissive] of parts) {
  const count = tris * 3, end = start + count;
  const color = new three.Color(hex).toArray();
  const data = (name, stride) => geometry.attributes[name].array.slice(start * stride, end * stride);
  const props = data('aBoard', 3);
  const colors = data('color', 3);
  for (let i = 0; i < props.length; i += 3) {
    assert(Math.abs(props[i] - roughness) < 1e-6 && Math.abs(props[i+1] - metallic) < 1e-6 && props[i+2] === id);
    assert(color.every((c, k) => Math.abs(c - colors[i+k]) < 1e-6));
  }
  const position = data('position', 3);
  for (let i = 1; i < position.length; i += 3) position[i] += .061;
  const material = { name, pbrMetallicRoughness: { baseColorFactor: [...color, 1],
    metallicFactor: metallic, roughnessFactor: roughness } };
  if (emissive) {
    material.emissiveFactor = new three.Color(0x8fe3ff).toArray();
    material.extensions = { KHR_materials_emissive_strength: { emissiveStrength: emissive } };
  }
  const slot = doc.materials.push(material) - 1;
  doc.meshes[0].primitives.push({ material: slot, mode: 4, attributes: {
    POSITION: floats(position, 3, true), NORMAL: floats(data('normal', 3), 3), TEXCOORD_0: floats(data('uv', 2).map((x,i) => i % 2 ? 1-x : x), 2),
  } });
  start = end;
}
assert.equal(start, geometry.attributes.position.count);
const jsonBuffer = Buffer.from(JSON.stringify({ ...doc, buffers: [{ byteLength: head }] }));
const aligned = Buffer.concat([jsonBuffer, Buffer.alloc((4-jsonBuffer.length%4)%4, 32)]);
const header = Buffer.alloc(28);
header.write('glTF', 0); header.writeUInt32LE(2, 4); header.writeUInt32LE(28+aligned.length+head, 8);
header.writeUInt32LE(aligned.length, 12); header.write('JSON', 16);
header.writeUInt32LE(head, 20); header.write('BIN\0', 24);
const blob = Buffer.concat([header.subarray(0,20), aligned, header.subarray(20), ...segments]);
mkdirSync(outputPath, { recursive: true });
writeFileSync(join(outputPath,filename), blob);
console.log(filename, blob.length, 'bytes, native 1,232 solid triangles');
