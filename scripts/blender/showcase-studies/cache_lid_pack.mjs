// Usage: node cache_lid_pack.mjs <node_modules directory> <raw GLB> <output GLB>
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [, , modules,raw,out] = process.argv;
const pkg = n => import(pathToFileURL(join(resolve(modules),'@gltf-transform',n,'dist/index.js')));
const [{NodeIO},{ALL_EXTENSIONS},{weld,quantize}] = await Promise.all([pkg('core'),pkg('extensions'),pkg('functions')]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(raw);
await doc.transform(weld(),quantize({quantizePosition:16,quantizeNormal:8,pattern:/^(POSITION|NORMAL)$/}));
const nodes=doc.getRoot().listNodes();
if (!nodes.some(x=>x.getName()==='Cache_Lid') || doc.getRoot().listAnimations().length!==1) throw new Error('Lost hinge or clip');
await io.write(out,doc);
