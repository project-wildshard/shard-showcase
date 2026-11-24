// Decode the exact packed Tinker Rook without modifying the donor.
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {MeshoptDecoder} from 'meshoptimizer';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const [src,output]=process.argv.slice(2);
const input=await readFile(src);
assert.equal(createHash('sha256').update(input).digest('hex'),'41a9d103fba6aea871d9f499da8c57678181a1783635477fe3927e1796626cba');
await MeshoptDecoder.ready;
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const doc=await io.read(src);
const root=doc.getRoot();
assert.equal(root.listSkins()[0].listJoints().length,21);
assert.equal(root.listAnimations().length,1);
root.listExtensionsUsed().filter(x=>x.extensionName==='EXT_meshopt_compression').forEach(x=>x.dispose());
await io.write(output,doc);
