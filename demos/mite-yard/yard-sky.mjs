// Outdoor East 01 sky. Directional cloud cards are distant, with no camera
// translation, fog or interaction. RGB ramps are sRGB for both renderers.
export const SKY_RAMP=Object.freeze([
 [-.40,0x9bbfc4],[-.06,0xa7cbd6],[.10,0x86b9d5],[.28,0x5b9dc7],[.62,0x4888b6],[1,0x356ca0],
].map(Object.freeze))
export const CLOUDS=Object.freeze([
 // Bearing, elevation, angular span (metres per metre of distance), opacity, variant.
 [-.196,.18,.34,.59,0],[.30,.124,.39,.63,1],[.13,.292,.19,.39,2],
 [1.25,.15,.58,.62,2],[-1.61,.23,.50,.65,1],[2.66,.16,.60,.52,0],
].map(Object.freeze))
export const CLOUD_SIZE=[192,80]
const palettes=[[.15,.52,.21,.16],[.32,.46,.25,.27],[.54,.57,.31,.12],[.76,.56,.22,.14],[.87,.44,.14,.10]]
const shape=[[.19,.53,.25,.13],[.35,.48,.22,.24],[.50,.49,.22,.30],[.68,.55,.27,.14],[.85,.52,.12,.16]]
const thin=[[.14,.58,.18,.10],[.29,.50,.26,.16],[.48,.49,.29,.17],[.68,.53,.26,.12],[.86,.46,.18,.11]]
const lobes=[palettes,shape,thin]
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v))
const smooth=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}
function noise(x,y,seed){
 const ix=Math.floor(x),iy=Math.floor(y)
 const u=smooth(0,1,x-ix),v=smooth(0,1,y-iy)
 const at=(i,j)=>{
  let h=Math.imul(i+31,0x7feb352d)^Math.imul(j+37,0x846ca68b)^Math.imul(seed,0x64323127)
  h=Math.imul(h^h>>>16,0x85ebca6b);return ((h^h>>>15)>>>0)/4294967295
 }
 return (at(ix,iy)*(1-u)+at(ix+1,iy)*u)*(1-v)+(at(ix,iy+1)*(1-u)+at(ix+1,iy+1)*u)*v
}
export function cloudPixels(variant){
 const [w,h]=CLOUD_SIZE,rgba=new Uint8ClampedArray(w*h*4)
 for(let y=0,i=0;y<h;y++)for(let x=0;x<w;x++,i+=4){
  const u=(x+.5)/w,v=(y+.5)/h,seed=variant+1
  const n=noise(u*16,v*9,seed)*.23+noise(u*33,v*17,seed)*.12+noise(u*65,v*28,seed)*.052
  let field=0
  for(const [cx,cy,sx,sy] of lobes[variant]){
   const q=((u-cx)/sx)**2+((v-cy)/sy)**2
   field=Math.max(field,1-q)
  }
  const pad=smooth(.01,.10,u)*smooth(.01,.10,1-u)*smooth(.01,.12,v)*smooth(.01,.12,1-v)
  const density=smooth(.05,.66,field+n-.23)
  const lit=clamp(.94-v*.27+n*.55)
  rgba[i]=208+40*lit;rgba[i+1]=223+23*lit;rgba[i+2]=229+19*lit;rgba[i+3]=255*density*pad
 }
 return rgba
}
export function cloudDirection(bearing,elevation){
 return [Math.sin(bearing)*Math.cos(elevation),Math.sin(elevation),-Math.cos(bearing)*Math.cos(elevation)]
}
export function skyChannels(value){
 let hi=SKY_RAMP.findIndex(([y])=>value<y)
 if(hi===-1)hi=SKY_RAMP.length-1
 hi=Math.max(1,hi)
 const [bottom,a]=SKY_RAMP[hi-1],[top,b]=SKY_RAMP[hi],t=clamp((value-bottom)/(top-bottom))
 return [16,8,0].map(s=>((a>>s)&255)*(1-t)+((b>>s)&255)*t)
}
export const skyCss=value=>`rgb(${skyChannels(value).map(Math.round).join(',')})`
export function makeCloudImages(document){
 const [w,h]=CLOUD_SIZE
 return [0,1,2].map(i=>{
  const image=document.createElement('canvas');image.width=w;image.height=h
  const c=image.getContext('2d');const pixels=c.createImageData(w,h)
  pixels.data.set(cloudPixels(i));c.putImageData(pixels,0,0);return image
 })
}
