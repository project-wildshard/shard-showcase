// Headless reference rig/edge-arrow adapter. No shader or browser rendering.
export let fixture, THREE;
export function configure(scene, three){
  fixture=scene; THREE=three;
}
export function instantiate(name){
  if(name!=='pallet')throw new Error('Unexpected reference asset');
  const root=fixture, bones={}; let mesh;
  root.traverse(o=>{if(o.isBone)bones[o.name]=o;if(o.isSkinnedMesh)mesh=o;});
  if(!mesh||!bones.forks||!bones.eye)throw new Error('Missing Pallet skeleton');
  const material=new WorldMaterial();
  mesh.material=material;
  return {root,bones,mesh,material,tris:mesh.geometry.index.count/3};
}
export class WorldMaterial {
  rim={value:new THREE.Vector4()};
  emitMul={value:1};
  dispose(){}
}
export const T={}; export const TELL={};
export class Geo { constructor(){throw new Error('Mesh fixtures should not create primitives');} }
const unreachable=()=>{throw new Error('Fixture fired an unrelated reference effect');};
export const aimLine=unreachable, diveLine=unreachable, openHalo=unreachable,
  reticle=unreachable, column=unreachable;
