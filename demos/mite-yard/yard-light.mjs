// One local sun vector for WebGL, the software lighting, and low-cost
// projected ground shadows. World coordinates are +Y up.
export const YARD_SUN=Object.freeze([-8,14,8])
export function shadowDelta(height){
 const [x,y,z]=YARD_SUN
 return [-x*height/y,-z*height/y]
}
export function shadowFootprint(height,radius){
 const [x,z]=shadowDelta(height),length=Math.hypot(x,z)
 // The widest point remains near the caster. The far end of the silhouette
 // narrows to look like a projection, not a second contact disk.
 return Array.from({length:16},(_,i)=>{
  const a=i*Math.PI/8,c=Math.cos(a),s=Math.sin(a)
  return [length*.40+c*(radius*.78+length*.57),s*radius*(1-.19*c)]
 })
}
