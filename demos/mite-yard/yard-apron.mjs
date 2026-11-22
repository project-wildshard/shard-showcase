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
 // Keep a separate seed: tuning wear does not reshuffle original slab tones.
 seed=0x837f092
 // Break old vehicle marks into stretches. Starts and stops are offset per
 // wheel so the abandoned lane does not look freshly road-striped.
 const rubber=[0xa58b6e,0xab9072,0xb1997a]
 for(const wheel of [-1.18,1.18])for(let i=0;i<24;i++){
  const z=-8.9+i*.74+(rand()-.5)*.36
  if(rand()<.23)continue
  const x=wheel+.10*Math.sin(z*.35)+(rand()-.5)*.06
  const w=.042+rand()*.054,l=.22+rand()*.48
  poly('rubber',rubber[Math.floor(rand()*3)],.0014,[
   [x-w,z-l*.51],[x+w*.12,z-l],[x+w,z+l*.36],[x-w*.2,z+l],
  ])
 }
 // Spalled aggregate collects along expansion joints. Orient these pieces
 // with the lane, rather than introducing a repeating grunge tile.
 const chips=[0xac967a,0xa79074,0xc7b191,0xad997f]
 for(let j=0;j<7;j++)for(let i=0;i<6;i++)for(let k=0;k<3;k++){
  const z=-8.25+2.75*j+(rand()-.5)*.38
  const x=-7.5+3*i+(rand()-.5)*2.61
  const w=.027+rand()*.091,l=.021+rand()*.058
  poly('aggregate',chips[Math.floor(rand()*4)],.0019,[
   [x-w,z-l*.42],[x+w*.36,z-l],[x+w,z+l*.32],[x-w*.28,z+l],
  ])
 }
 // Irregular older fluid stains below stationary equipment, away from
 // the active bite lane and around the west loading spur.
 for(const [x,z,w,l] of [[-2.13,1.8,.44,.64],[2.24,4.25,.38,.53],[-2.62,-2.63,.54,.76],[1.81,-5.81,.31,.47]]){
  for(const [k,y,c] of [[1,.00121,0xad9679],[.67,.00124,0xa58a6b]]){
   const a=w*k,b=l*k
   poly('fluid',c,y,[[x-a,z-b*.37],[x-a*.36,z-b],[x+a*.48,z-b*.8],[x+a,z-b*.05],[x+a*.53,z+b*.78],[x-a*.23,z+b],[x-a*.83,z+b*.56]])
  }
 }
 // Fine branching spalls across a few slabs. Lines are intentionally broken
 // and stop short of the high-contrast combat tells.
 for(const [x0,z0] of [[-1.64,1.41],[.66,-1.88],[-.58,5.43],[1.8,-5.21],[-3.6,3.55],[3.4,.79]]){
  let x=x0,z=z0
  for(let i=0;i<6;i++){
   const dx=.058+rand()*.108,dz=.035+(rand()-.38)*.15
   const w=.006+rand()*.009
   poly('spall',i===4?0xb29a7b:0x947d65,.00185,[
    [x-w,z-.005],[x+w,z-.005],[x+dx+w,z+dz+.036],[x+dx-w,z+dz+.036],
   ])
   x+=dx+.012;z+=dz+.047
  }
 }
 return rows
}
