const pitch=24*Math.PI/180, yaw=Math.atan2(3.35,7.15);
const sx=Math.sin(yaw),cz=Math.cos(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
export const DUEL_CAMERA_AXIS=[sx*cp,sp,cz*cp];
export const DUEL_CAMERA_FOV=46;
const tan=Math.tan(DUEL_CAMERA_FOV*Math.PI/360);

// Solve the distance from a fixed-angle camera to fit conservative actor bounds.
export function duelDistance(look,aspect,actors){
 let desired=6.35;
 for(const {x,z,radius,height} of actors){
  for(let ix of [-radius,radius])for(let iz of [-radius,radius])for(let h of [.02,height+.20]){
   const dx=x+ix-look.x,dy=h-look.y,dz=z+iz-look.z;
   const along=dx*sx+dz*cz,depth=along*cp+dy*sp;
   const horizontal=dx*cz-dz*sx,vertical=dy*cp-along*sp;
   desired=Math.max(desired,depth+Math.abs(horizontal)/(.86*tan*aspect),depth+Math.abs(vertical)/(.70*tan));
  }
 }
 return desired;
}
