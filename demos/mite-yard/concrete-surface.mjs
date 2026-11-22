// Rebuildable washed aggregate. Shared source for WebGL UVs and the
// Canvas2D floor projection; nothing to download, unpack, or bake.
export const CONCRETE_SIZE=128
export const CONCRETE_METERS=1.65
function hash(x,y,seed){
 let n=Math.imul(x+seed,0x45d9f3b)^Math.imul(y-seed,0x119de1f3)
 n=Math.imul(n^(n>>>16),0x45d9f3b)
 return ((n^(n>>>16))>>>0)/4294967296
}
function field(x,y,cells,seed){
 const u=x*cells/CONCRETE_SIZE,v=y*cells/CONCRETE_SIZE,a=Math.floor(u),b=Math.floor(v)
 const t=u-a,s=v-b,k=t*t*(3-2*t),q=s*s*(3-2*s)
 const sample=(i,j)=>hash(i%cells,j%cells,seed)
 return (sample(a,b)*(1-k)+sample(a+1,b)*k)*(1-q)+(sample(a,b+1)*(1-k)+sample(a+1,b+1)*k)*q
}
export function concretePixels(shadeOnly=false){
 const pixels=new Uint8ClampedArray(CONCRETE_SIZE*CONCRETE_SIZE*4)
 for(let y=0;y<CONCRETE_SIZE;y++)for(let x=0;x<CONCRETE_SIZE;x++){
  const grain=hash(x,y,205),sand=field(x,y,58,79),mottle=field(x,y,9,557)
  const pits=grain>.91?(grain-.91)*1.23:0
  const wear=.014+.061*mottle+.056*sand+.052*grain+pits
  const i=(y*CONCRETE_SIZE+x)*4
  pixels[i]=pixels[i+1]=pixels[i+2]=shadeOnly?0:255*(1-wear)
  pixels[i+3]=shadeOnly?255*wear:255
 }
 return pixels
}

// For the software view, take exact floor intersections at the centers of a
// half-resolution raster's texels. Each unrolled scan line has constant depth.
export function floorScanline(view,row){
 const {w,h,fx,fy,yaw,pitch,x,y,z}=view
 const tilt=(2*row/h-1)/fy
 const sin=Math.sin(pitch),cos=Math.cos(pitch),slope=tilt*cos-sin
 if(slope<=0)return null
 const depth=y/slope
 if(depth>=14)return null
 const ahead=depth*(cos-tilt*sin),scale=CONCRETE_SIZE/CONCRETE_METERS
 const c=Math.cos(yaw),s=Math.sin(yaw),step=depth*2*scale/(w*fx)
 return {u:(x+s*ahead)*scale-step*c*w/2,v:(z-c*ahead)*scale-step*s*w/2,
  du:c*step,dv:s*step,opacity:Math.min(1,(14-depth)/8)}
}
