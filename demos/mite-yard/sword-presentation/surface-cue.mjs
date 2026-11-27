import {pickSwordContactPose} from './contact-after-pose.mjs';

// Appearance-only gate. Distance is from the same-tick blade sweep to the
// matching target's displayed surface, not the damage capsule.
export const MAX_SURFACE_GAP = .06;
const vec3=v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite);

export function chooseSwordCue(hit, pose, surface, lastRenderedId=null) {
  const blade=pickSwordContactPose(hit,pose,lastRenderedId);
  if(!blade || hit.targetId==null) return null;
  const samePair=surface?.targetId===hit.targetId && surface.tick===hit.tick &&
    surface.hitId===hit.id && surface.weaponEpoch===hit.weaponEpoch;
  if(!samePair || !Number.isFinite(surface.gapM) ||
      surface.gapM<0 || surface.gapM>MAX_SURFACE_GAP ||
      !vec3(surface.point) || !vec3(surface.normal) ||
      Math.hypot(...surface.normal)<1e-4) {
    // Keep normal hit readability (damage/audio/reaction). Don't fabricate a
    // metal glint at the enemy's center or change whether the hit dealt damage.
    return {id:blade.id,mode:'existing-hit-feedback'};
  }
  return {id:blade.id,mode:'surface-glint',point:[...surface.point],normal:[...surface.normal],blade};
}
