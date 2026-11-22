// East 01 freight shutter. The sealed door is set back beyond the rear
// collision edge; only its original fence strip is replaced in the browser yard.
export const LOADING_BAY=Object.freeze({halfWidth:3,doorHalfWidth:1.79})
export const BAY_FINISHES=Object.freeze({
 frame:0x4b5d5d, lip:0x89928a, reveal:0x202f31, shadow:0x293a3c,
 orange:0xb8652f, edge:0xd29b5c, scuff:0x65574a, concrete:0x696f62,
 slat0:0x536569, slat1:0x475d61, slat2:0x4d6266, seam:0x32494c,
 zinc:0x98988b, gasket:0x222f30, hazard:0xbe8d4a, marker:0xb97239,
})

export function createLoadingBay(){
 const parts=[]
 const box=(finish,w,h,d,x,y,z,segments=[1,1])=>parts.push({finish,size:[w,h,d],position:[x,y,z],segments})
 // Slats sit behind the reveal, not on top of the flanking corrugation.
 // Subdivide tall backing faces so the Canvas painter sorts local depth.
 box('shadow',6.01,2.65,.18,0,1.325,-11.91,[3,6])
 box('gasket',3.70,2.39,.09,0,1.20,-11.63,[3,6])
 for(let i=0;i<12;i++){
  const y=.173+i*.161
  box(['slat1','slat1','slat0','slat2','slat1','slat2','slat2','slat1','slat0','slat2','slat2','slat1'][i],
   3.58,.150,.075,0,y,-11.192)
  box('seam',3.57,.019,.022,0,y-.058,-11.146)
 }
 box('frame',3.56,.08,.094,0,.054,-11.162)
 box('concrete',3.99,.065,.188,0,.0325,-11.088)
 box('frame',4.15,.35,.63,0,2.204,-10.994)
 box('lip',4.23,.034,.646,0,2.402,-10.978)
 box('reveal',3.65,.13,.53,0,2.005,-11.058)
 for(const side of [-1,1]){
  const x=side
  box('frame',.23,2.14,.66,x*1.86,1.07,-11.001)
  box('reveal',.06,1.94,.49,x*1.748,.99,-10.985)
  box('orange',.24,2.48,.34,x*2.09,1.24,-10.823)
  box('edge',.025,2.19,.025,x*1.995,1.31,-10.642)
  box('shadow',.71,2.57,.24,x*2.61,1.285,-11.305,[1,6])
  box('frame',.55,2.48,.095,x*2.61,1.26,-10.939,[1,6])
  box('concrete',.42,.23,.34,x*2.09,.115,-10.78)
  box('scuff',.25,.35,.025,x*2.09,.41,-10.642)
  box('zinc',.06,.06,.028,x*2.09,2.317,-10.635)
  for(let i=0;i<3;i++)box('hazard',.14,.044,.009,x*2.09,.3+i*.085,-10.622)
 }
 // Only one service panel: no repeated control lights behind the enemy.
 box('gasket',.26,.38,.095,2.475,1.05,-10.823)
 box('frame',.20,.30,.034,2.475,1.055,-10.766)
 box('marker',.085,.048,.012,2.475,1.13,-10.745)
 box('zinc',.055,.032,.012,2.475,.974,-10.745)
 // Steel fascia wraps above the door, with two shallow stepped crowns.
 box('frame',5.98,.28,.30,0,2.508,-11.039)
 box('shadow',4.72,.22,.20,0,2.715,-11.155)
 box('lip',4.82,.038,.228,0,2.844,-11.141)
 for(const x of [-1.65,-.84,.84,1.65])box('zinc',.052,.052,.025,x,2.479,-10.869)
 return parts
}
