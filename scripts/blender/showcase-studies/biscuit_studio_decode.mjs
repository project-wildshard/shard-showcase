// Produce temporary Blender-readable GLBs without changing vertices or joint ordering.
// Usage: node biscuit_studio_decode.mjs <meshoptimizer ESM path> <source GLB> <studio GLB>
import {readFileSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const [, , modulePath, source, dest] = process.argv;
const {MeshoptDecoder: decoder} = await import(pathToFileURL(resolve(modulePath)));
await decoder.ready;
const blob = readFileSync(source), n = blob.readUInt32LE(12);
const doc = JSON.parse(blob.subarray(20, 20+n)), orig = blob.subarray(28+n);
const chunks = [];
let pos = 0;
for (const view of doc.bufferViews) {
    const m = view.extensions?.EXT_meshopt_compression;
    let chunk;
    if (m) {
        chunk = Buffer.alloc(m.count*m.byteStride);
        if (chunk.length !== view.byteLength) throw new Error('Bad bufferView length');
        decoder.decodeGltfBuffer(chunk, m.count, m.byteStride, orig.subarray(m.byteOffset,m.byteOffset+m.byteLength),m.mode,m.filter);
        delete view.extensions.EXT_meshopt_compression;
        if (!Object.keys(view.extensions).length) delete view.extensions;
    } else {
        if (view.buffer !== 0) throw new Error('Unexpected buffer');
        chunk = orig.subarray(view.byteOffset??0, (view.byteOffset??0)+view.byteLength);
    }
    view.buffer = 0;
    view.byteOffset = pos;
    const padding = (-chunk.length) & 3;
    chunks.push(chunk, Buffer.alloc(padding));
    pos += chunk.length + padding;
}
doc.buffers = [{byteLength:pos}];
for (const k of ['extensionsUsed', 'extensionsRequired']) {
    doc[k] = doc[k].filter(x => x !== 'EXT_meshopt_compression');
    if (!doc[k].length) delete doc[k];
}
const raw = Buffer.from(JSON.stringify(doc));
const j = Buffer.concat([raw,Buffer.alloc((-raw.length)&3,0x20)]);
const header = Buffer.alloc(20), bin = Buffer.alloc(8);
header.write('glTF'); header.writeUInt32LE(2,4); header.writeUInt32LE(j.length+pos+28,8);
header.writeUInt32LE(j.length,12); header.write('JSON',16);
bin.writeUInt32LE(pos); bin.write('BIN\0',4);
writeFileSync(dest,Buffer.concat([header,j,bin,...chunks]));
