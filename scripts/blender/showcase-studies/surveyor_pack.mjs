// Usage: node surveyor_pack.mjs <node_modules> <rebuild directory>
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {stat} from 'node:fs/promises';
const [, , modules,out]=process.argv;
const pkg=n=>import(pathToFileURL(join(resolve(modules),'@gltf-transform',n,'dist/index.js')));
const [{NodeIO},{ALL_EXTENSIONS,EXTMeshoptCompression},{weld,reorder},{MeshoptEncoder,MeshoptDecoder}]=await Promise.all([
  pkg('core'),pkg('extensions'),pkg('functions'),import(pathToFileURL(join(resolve(modules),'meshoptimizer','index.js')))
]);
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder
});
const raw=join(out,'wsc-actor-017-surveyor.glb'),packed=join(out,'wsc-actor-017-surveyor-packed.glb');
const doc=await io.read(raw);
// Preserve float local mesh coordinates and inverse binds; reorder and losslessly encode.
await doc.transform(weld(),reorder({encoder:MeshoptEncoder,target:'size'}));
doc.createExtension(EXTMeshoptCompression).setRequired(true);
await io.write(packed,doc);
if ((await stat(packed)).size>=180000) throw new Error('Packed Surveyor exceeds inventory budget.');
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
await io.write(join(out,'surveyor-decoded-for-blender.glb'),re);
console.log('Packed and compared decoded skin, geometry and animation:',(await stat(packed)).size,'bytes');
