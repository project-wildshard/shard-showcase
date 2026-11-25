// Add --exact-surveyor <tracked glb> to decode a pinned donor instead of packing.
// Usage: node surveyor_pack.mjs <node_modules> <rebuild directory> [surveyor|tinker-rook|yard-boss|shift-boss]
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {stat} from 'node:fs/promises';
const [, , modules,out,role='surveyor']=process.argv;
const ids={'surveyor':'017','tinker-rook':'018','yard-boss':'015','shift-boss':'016'};
if (!(role in ids)) throw new Error('Unsupported town-bot role');
const stem='wsc-actor-'+ids[role]+'-'+role;
const pkg=n=>import(pathToFileURL(join(resolve(modules),'@gltf-transform',n,'dist/index.js')));
const [{NodeIO},{ALL_EXTENSIONS,EXTMeshoptCompression},{weld,reorder},{MeshoptEncoder,MeshoptDecoder}]=await Promise.all([
  pkg('core'),pkg('extensions'),pkg('functions'),import(pathToFileURL(join(resolve(modules),'meshoptimizer','index.js')))
]);
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder
});
if(['--exact-surveyor','--decode-tracked'].includes(process.argv[5])){
  if((process.argv[5]==='--exact-surveyor' && role!=='surveyor') || !process.argv[6]) throw new Error('Expected an exact Surveyor input file.');
  const checked=await io.read(process.argv[6]);
  checked.getRoot().listExtensionsUsed().filter(x=>x.extensionName===EXTMeshoptCompression.EXTENSION_NAME).forEach(x=>x.dispose());
  await io.write(join(out,role+'-decoded-for-blender.glb'),checked);
  process.exit(0);
}
const raw=join(out,stem+'.glb'),packed=join(out,stem+'-packed.glb');
const doc=await io.read(raw);
// Preserve float local mesh coordinates and inverse binds; reorder and losslessly encode.
await doc.transform(weld(),reorder({encoder:MeshoptEncoder,target:'size'}));
doc.createExtension(EXTMeshoptCompression).setRequired(true);
await io.write(packed,doc);
if ((await stat(packed)).size>=180000) throw new Error('Packed town bot exceeds inventory budget.');
const re=await io.read(packed);
const original=doc.getRoot(), roundtrip=re.getRoot();
function ac(a,b){
  if(!a||!b) {if(a!==b) throw new Error('Missing accessor');return;}
  const A=a.getArray(),B=b.getArray();
  if(A.length!==B.length||A.some((x,i)=>x!==B[i]))throw new Error('Changed accessor: '+a.getName());
}
const [p]=original.listMeshes()[0].listPrimitives();
const [q]=roundtrip.listMeshes()[0].listPrimitives();
for (const key of p.listSemantics()) ac(p.getAttribute(key),q.getAttribute(key));
const orientedTriangles = accessor => {
  const a=accessor.getArray(), rows=[];
  for (let i=0;i<a.length;i+=3) {
    const n=[a[i],a[i+1],a[i+2]];
    rows.push([0,1,2].map(k=>[n[k],n[(k+1)%3],n[(k+2)%3]].join("/")).sort()[0]);
  }
  return rows.sort().join('|');
};
if(orientedTriangles(p.getIndices())!==orientedTriangles(q.getIndices())) throw new Error('Topology or winding changed');
ac(original.listSkins()[0].getInverseBindMatrices(),roundtrip.listSkins()[0].getInverseBindMatrices());
if (original.listSkins()[0].listJoints().some((j,i)=>j.getName()!==roundtrip.listSkins()[0].listJoints()[i].getName())) throw new Error('Joint order changed');
const A=original.listAnimations()[0].listSamplers(),B=roundtrip.listAnimations()[0].listSamplers();
if (A.length!==B.length)throw new Error('Animation sampler count changed');
for (let i=0;i<A.length;i++) {ac(A[i].getInput(),B[i].getInput());ac(A[i].getOutput(),B[i].getOutput());}
roundtrip.listExtensionsUsed().filter(x=>x.extensionName===EXTMeshoptCompression.EXTENSION_NAME).forEach(x=>x.dispose());
await io.write(join(out,role+'-decoded-for-blender.glb'),re);
console.log('Packed and compared decoded skin, geometry and animation:',(await stat(packed)).size,'bytes');
