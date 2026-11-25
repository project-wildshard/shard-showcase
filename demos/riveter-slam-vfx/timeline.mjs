// Reusable visual-only effect. The caller owns the clock and gameplay.
// A normalized one-metre mesh is scaled by the caller's chosen max radius.
const warn = 1;
const waveDemoSeconds = .46;
export function sampleSlamCue(t, maxRadius, travel = waveDemoSeconds) {
  if (![t, maxRadius, travel].every(Number.isFinite) || maxRadius <= 0 || travel <= 0)
    throw new RangeError('Expected finite time and positive radius / travel duration');
  if (t < 0 || t >= warn + travel) return {state:'off', radius:0, opacity:0};
  if (t < warn) return {state:'warning', radius:maxRadius, opacity:.76 + .24*t/warn};
  const u = (t-warn)/travel;
  return {state:'wave', radius:maxRadius*(.10+.90*u), opacity:1-u**4};
}

export function bindSlamMesh(root) {
  const meshes=[];
  root.traverse(node=>{if(node.isMesh) meshes.push(node)});
  const [mesh]=meshes;
  if (meshes.length!==1 || !mesh.material.isMeshBasicMaterial || mesh.geometry.getAttribute('color')?.itemSize!==4)
    throw new TypeError('Expected a one-draw unlit RGBA ring');
  mesh.material=mesh.material.clone();
  Object.assign(mesh.material,{transparent:true,depthTest:true,depthWrite:false,forceSinglePass:true,toneMapped:false});
  return mesh;
}
