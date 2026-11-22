// East E01 dock court from study 24, adapted to the small calibration yard.
// Visual anchors and conservative axis-aligned collision share these positions.
export const DOCK=Object.freeze({x:3.25,z:-5.45,width:1.99,depth:1.99})
export const STACK=Object.freeze({x:6,z:-5,width:2.4,depth:2})
export const CRATES=Object.freeze([
 [-.565,0,0],[.565,0,0],[-.56,.864,0],
].map(([x,y,z])=>Object.freeze([STACK.x+x,y,STACK.z+z])))
