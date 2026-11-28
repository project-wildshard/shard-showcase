// Cosmetic alignment around the authored weapon grip. Never used by the hit test.
import {Quaternion,Vector3,MathUtils} from 'three';
const {clamp,smoothstep}=MathUtils;
export function beaconThrustWeight(time,wind,cycle){
 return smoothstep(time,0,wind*.88)*(1-smoothstep(time,wind+.045,Math.max(wind+.055,cycle-.055)));
}
export function createThrustAlignment(){
 const g=new Vector3(),b=new Vector3(),v=new Vector3(),want=new Vector3(),aligned=new Vector3();
 const delta=new Quaternion(),turn=new Quaternion(),identity=new Quaternion();
 return (mount,base,hand,grip,tip,target,weight)=>{
  mount.position.set(0,0,0);mount.quaternion.copy(base);
  if(weight<=0)return null;
  hand.worldToLocal(grip.getWorldPosition(g));
  hand.worldToLocal(tip.getWorldPosition(b));
  hand.worldToLocal(want.copy(target)).sub(g);
  v.copy(b).sub(g);
  if(v.lengthSq()<1e-7||want.lengthSq()<1e-7)return null;
  v.normalize();want.normalize();
  const before=MathUtils.radToDeg(v.angleTo(want));
  delta.setFromUnitVectors(v,want);turn.copy(identity).slerp(delta,clamp(weight,0,1));
  mount.quaternion.premultiply(turn);
  hand.worldToLocal(grip.getWorldPosition(aligned));
  mount.position.copy(g).sub(aligned);
  hand.worldToLocal(grip.getWorldPosition(aligned));
  return {before,after:MathUtils.radToDeg(v.applyQuaternion(turn).angleTo(want)),gripSlip:g.distanceTo(aligned)};
 };
}
