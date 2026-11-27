// A scoped geometry-only adapter for the reference rig. It reuses exact
// bones/bind data, omitting production material/shadow/LOD and visible meshes.
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {createRequire} from 'node:module';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
export async function readRigs(root,load,THREE,threeDir){
  const [{GLTFLoader},{clone},{NodeIO},{KHRDracoMeshCompression}]=await Promise.all(
    ['three/addons/loaders/GLTFLoader.js','three/addons/utils/SkeletonUtils.js',
      '@gltf-transform/core','@gltf-transform/extensions'].map(load)
  );
  const d=join(threeDir,'examples/jsm/libs/draco/gltf'), scratch=mkdtempSync(join(tmpdir(),'wsc-draco-'));
  let decoder;
  try {
    const wrapper=join(scratch,'draco.cjs');
    writeFileSync(wrapper,readFileSync(join(d,'draco_wasm_wrapper.js')));
    decoder=await createRequire(import.meta.url)(wrapper)({wasmBinary:readFileSync(join(d,'draco_decoder.wasm'))});
  } finally { rmSync(scratch,{recursive:true,force:true}); }
  const io=new NodeIO().registerExtensions([KHRDracoMeshCompression]).registerDependencies({'draco3d.decoder':decoder});
  const unpack=async n=>{
    const doc=await io.read(join(root,'public/models',n+'.glb'));
    doc.getRoot().listExtensionsUsed().filter(e=>e.extensionName==='KHR_draco_mesh_compression').forEach(e=>e.dispose());
    const b=await io.writeBinary(doc);
    return (await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'')).scene;
  };
  const assets=Object.fromEntries(await Promise.all(['rook','swords'].map(async n=>[n,await unpack(n)])));
  const modelSource=readFileSync(join(root,'src/gfx/models.ts'),'utf8');
  const slots=/export const SLOTS = \[([\s\S]*?)\] as const/.exec(modelSource);
  if(!slots)throw new Error('Missing palette slot names');
  return {
    SLOTS:[...slots[1].matchAll(/'([^']+)'/g)].map(m=>m[1]),
    T:{FLAT:0},GU:{uWind:{value:new THREE.Vector4()},uNearFade:{value:new THREE.Vector2()}},
    WorldMaterial:class extends THREE.MeshStandardMaterial {
      rim={value:new THREE.Vector4()};
      flash={value:new THREE.Vector4()};
    },
    hasModel:name=>Object.hasOwn(assets,name),
    instantiate(name){
      const root=clone(assets[name]), bones={};let mesh;
      root.traverse(o=>{if(o.isBone)bones[o.name]=o;if(o.isSkinnedMesh)mesh=o;});
      mesh.material=new adapter.WorldMaterial();
      const geometry=mesh.geometry;
      const slot=geometry.getAttribute('_slot');
      if(slot)geometry.setAttribute('aSlot',slot);
      return {root,mesh,bones,material:mesh.material,tris:geometry.index.count/3,low:()=>geometry};
    },
  };
}
export let adapter;
export async function configure(...args){adapter=await readRigs(...args);}
export let SLOTS,T,GU,WorldMaterial,hasModel,instantiate;
export function bindAdapter(){({SLOTS,T,GU,WorldMaterial,hasModel,instantiate}=adapter);}
