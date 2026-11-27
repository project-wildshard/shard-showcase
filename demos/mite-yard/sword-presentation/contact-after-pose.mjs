// Presentation fence: use actual visible sockets after one pose update on the
// confirmed hit's tick. No resampling of rig, damage, attacks, or physics.
const vec3=v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite);
export function pickSwordContactPose(hit, renderedPose, lastRenderedId=null) {
  if (hit?.weapon!=='sword' || hit?.source!=='melee' ||
      !Number.isFinite(hit.damageDealt) || hit.damageDealt<=0 ||
      hit.id==null || hit.id===lastRenderedId || hit.weaponEpoch==null ||
      !Number.isSafeInteger(hit.tick) || hit.tick<0 ||
      renderedPose?.tick!==hit.tick || renderedPose.weaponEpoch!==hit.weaponEpoch ||
      renderedPose.action!==hit.action || !Number.isFinite(hit.actionT) ||
      !Number.isFinite(renderedPose.actionT) ||
      Math.abs(renderedPose.actionT-hit.actionT)>1e-6 ||
      !vec3(renderedPose.base) || !vec3(renderedPose.tip) ||
      Math.hypot(...renderedPose.tip.map((v,i)=>v-renderedPose.base[i]))<1e-4) return null;
  return {id:hit.id,base:[...renderedPose.base],tip:[...renderedPose.tip]};
}
