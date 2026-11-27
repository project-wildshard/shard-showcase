// Three r186 visual adapter. It never moves meshes, colliders, or bodies.
export const periodM=1.32
export const placements=Object.freeze([
  {x:-84,y:.10,z:-103,yaw:0,worldSpeed:-3},
  {x:-90,y:.10,z:-103,yaw:Math.PI,worldSpeed:4},
  {x:-96,y:.10,z:-103,yaw:0,worldSpeed:-5},
].map(Object.freeze))
const fract=x=>x-Math.floor(x)
export function phase(localSpeed,seconds){
  if(!Number.isFinite(localSpeed)||!Number.isFinite(seconds))throw new RangeError('Finite speed and time required')
  return fract(-localSpeed*seconds/periodM)
}
export function treadTile(){
  const result=new Uint8Array(128*4)
  // One rounded broad highlight per repeat. No flash, emission, image or mip.
  for(let i=0;i<128;i++){
    const u=(i+.5)/128, crest=((1+Math.cos(2*Math.PI*(u-.41)))/2)**1.65
    const shade=Math.round(138+102*crest)
    result.set([shade,shade,shade,255],i*4)
  }
  return result
}
export function attachTread(THREE,root){
  const parts=[]
  root.traverse(m=>{
    if(m.isMesh&&/^Rubber tread 0[012]$/.test(m.material?.name))parts.push(m)
  })
  if(parts.length!==3)throw new Error('Expected the three original rubber tread primitives')
  const map=new THREE.DataTexture(treadTile(),128,1,THREE.RGBAFormat)
  map.wrapS=THREE.RepeatWrapping
  map.minFilter=map.magFilter=THREE.LinearFilter
  map.colorSpace=THREE.NoColorSpace
  map.needsUpdate=true
  const keep=[]
  for(const m of parts){
    const geometry=m.geometry.clone(), material=m.material.clone()
    const p=geometry.attributes.position,uv=new Float32Array(p.count*2)
    for(let i=0;i<p.count;i++){uv[2*i]=p.getX(i)/periodM;uv[2*i+1]=.5}
    geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2))
    keep.push([m,m.geometry,m.material])
    material.map=map
    m.geometry=geometry
    m.material=material
  }
  return {
    setTime(seconds,localSpeed){
      map.offset.x=phase(localSpeed,seconds)
      return map.offset.x
    },
    dispose(){
      for(const [m,g,mat] of keep){m.geometry.dispose();m.material.dispose();m.geometry=g;m.material=mat}
      map.dispose()
    },
  }
}
