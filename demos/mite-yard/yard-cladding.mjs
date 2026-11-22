// Rear loading court: 9 replaceable 2-metre bays, four pressed corrugations
// per bay. Tones are authored as baked surface variation, not extra lights.
const enamel=[0x345156,0x3d5558,0x39575b,0x3b5659,0x39575a,0x3f5757,0x415758,0x3b5354,0x3b565a]
const low=.08,high=2.64
// A compact trapezoidal cross section, open at the back against the shell.
const profile=[[0,-10.856],[.078,-10.856],[.134,-10.716],[.325,-10.716],[.39,-10.856],[.48,-10.856]]
function tint(color,k){
 const c=n=>Math.round(((color>>n)&255)*k)
 return (c(16)<<16)|(c(8)<<8)|c(0)
}
export function createRearCladding(){
 const quads=[]
 for(let bay=0;bay<9;bay++){
  const start=-8.972+bay*2
  for(let rib=0;rib<4;rib++)for(let s=0;s<profile.length-1;s++){
   const [a,z]=profile[s],[b,w]=profile[s+1],x=start+rib*.486
   const k=[.86,.94,1,.89,.83][s]
   const color=enamel[bay],top=tint(color,k),bottom=tint(color,k*.57)
   quads.push({top,bottom,points:[[x+a,low,z],[x+b,low,w],[x+b,high,w],[x+a,high,z]]})
  }
 }
 return quads
}
