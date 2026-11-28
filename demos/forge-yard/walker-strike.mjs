// The Blender authoring frame for contact is 15 in every Walker attack
// (normalized over frames 1–30). Gameplay still owns hit tests and damage.
export const RELEASE_POSE=14/29;
export const SIGNATURE_STRIKES=Object.freeze({'017':'MaulDrop','022':'SlipfinRip','025':'NeedleJab'});
export const walkerStrike=w=>SIGNATURE_STRIKES[w.id]??({chop:'Chop',sweep:'Sweep',thrust:'Thrust'})[w.style];
export function walkerStrikePhase(elapsed,release,cycle){
 const progress=(n,d)=>d>0?Math.max(0,Math.min(1,n/d)):1;
 return elapsed<release?RELEASE_POSE*progress(elapsed,release)
  :RELEASE_POSE+(1-RELEASE_POSE)*progress(elapsed-release,cycle-release);
}
