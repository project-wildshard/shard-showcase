// East 01 artist-editable floor polygons, in metres, shared by Three and Blender.
// Each convex patch is CCW in the authored X/Z plane, not a collision surface.
const slab=[0xbfa782,0xb69b79,0xbba383,0xc0aa8c,0xb39e83,0xc4ad89]
const repairs=[0x98876e,0xa89478,0xb29e80]
const paint=0xe7ac3d
export function createApron(){
 const rows=[]
 let seed=0xe0104
 const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}
 const tint=()=>slab[Math.floor(rand()*slab.length)]
 const poly=(style,color,y,points)=>rows.push({style,color,y,points})
 const rect=(style,color,y,x,z,w,d)=>poly(style,color,y,[
  [x-w/2,z-d/2],[x+w/2,z-d/2],[x+w/2,z+d/2],[x-w/2,z+d/2],
 ])
 // Small dark joints expose the base from one slab to the next.
 rect('joint',0x766452,-.005,0,0,18,22)
 for(let j=0;j<8;j++)for(let i=0;i<6;i++){
  const x=-7.5+3*i,z=-9.625+2.75*j
  rect('slab',tint(),0,x,z,2.977,2.726)
  if(rand()>.36){
   const a=x+(rand()-.5)*2.15,b=z+(rand()-.5)*1.85
   const w=.10+rand()*.31,d=.08+rand()*.24
   poly('repair',repairs[Math.floor(rand()*repairs.length)],.002,[
    [a-w,b-d*.27],[a-w*.22,b-d],[a+w*.81,b-d*.74],
    [a+w,b+d*.23],[a+w*.11,b+d],[a-w*.76,b+d*.75],
   ])
  }
 }
 // Weathered service lane, with a straight core and clearly painted edges.
 for(let z=-8;z<9;z+=1.5)for(const x of [-2.9,2.9]){
  rect('paint',paint,.003,x,z,.069,.60)
  rect('paint-worn',0xc38f3d,.003,x+.004,z+.367,.059,.103)
 }
 // Two route arrows stay outside the combat lane and don't imply a blockade.
 for(const [x,z] of [[-4.02,5.26],[4.15,-1.02]]){
  rect('paint',paint,.003,x,z,.17,.75)
  poly('paint',paint,.003,[[x-.29,z-.374],[x,z-.86],[x+.29,z-.374]])
 }
 // Narrow grated channel at the west perimeter. It does not cross a path.
 rect('metal',0x354649,.004,-7.72,.15,.35,5.4)
 for(let i=0;i<18;i++)rect('metal',0x6d7a73,.005,-7.72,-2.4+i*.3,.31,.055)
 return rows
}
