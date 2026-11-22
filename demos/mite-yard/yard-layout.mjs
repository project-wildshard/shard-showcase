// East E01 dock court from study 24, adapted to the small calibration yard.
// Visual anchors and conservative axis-aligned collision share these positions.
export const DOCK=Object.freeze({x:3.25,z:-5.45,width:1.99,depth:1.99})
export const STACK=Object.freeze({x:6,z:-5,width:2.4,depth:2})
export const CRATES=Object.freeze([
 [-.565,0,0],[.565,0,0],[-.56,.864,0],
].map(([x,y,z])=>Object.freeze([STACK.x+x,y,STACK.z+z])))

// The recovered Yard 01 sign faces +Z. Only the two measured feet collide.
export const GANTRY=Object.freeze({x:0,z:-10})
export const GANTRY_FEET=Object.freeze([-2.92,2.92].map(x=>Object.freeze([
 GANTRY.x+x,GANTRY.z,.91,.93,
])))
export const GANTRY_FALLBACK_OMIT=Object.freeze(['Worn zinc fasteners','Carbon gasket'])

// Runtime-only wall-mounted sign. It reuses the original gantry's one stencil
// mesh; the recovered standalone asset remains intact for other scenes.
export const GANTRY_PLAQUE=Object.freeze({height:2.18,front:-.57,width:1.78,faceHeight:.35,glyphScale:2.11})
