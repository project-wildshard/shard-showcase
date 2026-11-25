// Standalone visual effect. Clock, placement, ground fit and hazard decisions are caller-owned.
import * as T from 'three'

export const CAPACITY=12, DURATION=6
const stops=Object.freeze([[0,1],[.38,.94],[2.1,.78],[3.8,.49],[5.22,.18],[5.90,0],[6,0]])
export function ageToHeat(age){
  if(!Number.isFinite(age))throw new TypeError('Expected finite age in seconds')
  if(age<0||age>=DURATION)return null
  for(let i=1;i<stops.length;i++){
    const [start,a]=stops[i-1], [end,b]=stops[i]
    if(age<=end){
      const t=(age-start)/(end-start), s=t*t*(3-2*t)
      return a+(b-a)*s
    }
  }
  return 0
}
export function makeSlagBatch(root){
  root.updateMatrixWorld(true)
  const positions=[], bases=[], glow=[], v=new T.Vector3()
  const parts=[]
  root.traverse(mesh=>{
    if(!mesh.isMesh)return
    const {geometry:g,material:m}=mesh
    if(mesh.isSkinnedMesh||Array.isArray(m)||g.groups.length||
       !m.isMeshStandardMaterial||m.map||m.emissiveMap||g.morphAttributes.position||
       typeof m.emissiveIntensity!=='number')throw new TypeError('Wrong static slag donor')
    parts.push(mesh)
    const p=g.getAttribute('position'), index=g.index
    const e=m.emissive.clone().multiplyScalar(m.emissiveIntensity)
    for(let i=0;i<(index?.count??p.count);i++){
      v.fromBufferAttribute(p,index?index.getX(i):i).applyMatrix4(mesh.matrixWorld)
      positions.push(v.x,v.y,v.z)
      bases.push(m.color.r,m.color.g,m.color.b)
      glow.push(e.r,e.g,e.b)
    }
  })
  if(parts.length!==6||positions.length!==703*9)throw new TypeError('Wrong slag donor geometry')
  const g=new T.BufferGeometry().setAttribute('position',new T.Float32BufferAttribute(positions,3))
    .setAttribute('base',new T.Float32BufferAttribute(bases,3))
    .setAttribute('heatColor',new T.Float32BufferAttribute(glow,3))
  const heat=new T.InstancedBufferAttribute(new Float32Array(CAPACITY),1).setUsage(T.DynamicDrawUsage)
  g.setAttribute('heat',heat)
  const m=new T.ShaderMaterial({
    side:parts[0].material.side,
    vertexShader:`
      attribute vec3 base;
      attribute vec3 heatColor;
      attribute float heat;
      varying vec3 radiance;
      void main(){
        // Cool hotter materials to a nearly-black crust rather than leaving a bright painted ring.
        float hot=step(0.001,length(heatColor));
        vec3 crust=mix(base*.56,base*.11,hot*(1.0-heat));
        radiance=crust+heatColor*heat*.58;
        gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);
      }`,
    fragmentShader:`
      varying vec3 radiance;
      void main(){
        gl_FragColor=vec4(radiance,1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`
  })
  const mesh=new T.InstancedMesh(g,m,CAPACITY)
  mesh.name='E4 Slag · one emissive batch'
  mesh.frustumCulled=false
  mesh.instanceMatrix.setUsage(T.DynamicDrawUsage)
  mesh.count=0
  const pose=new T.Object3D()
  function update(now, entries){
    if(!Number.isFinite(now)||!Array.isArray(entries))throw new TypeError('Expected finite time and an entry list')
    if(entries.length>CAPACITY)throw new RangeError('Visual budget: at most 12 entries')
    for(const row of entries)if(!row||![row.born,row.x,row.y,row.z,row.yaw].every(Number.isFinite))
      throw new TypeError('Expected finite placement and birth time')
    const active=[]
    for(const row of entries){
      const h=ageToHeat(now-row.born)
      if(h===null)continue
      const i=active.length
      pose.position.set(row.x,row.y,row.z)
      pose.rotation.y=row.yaw
      pose.updateMatrix()
      mesh.setMatrixAt(i,pose.matrix)
      heat.setX(i,h)
      active.push(h)
    }
    mesh.count=active.length
    mesh.visible=mesh.count>0
    heat.needsUpdate=true
    mesh.instanceMatrix.needsUpdate=true
    return active
  }
  return {mesh,update,dispose(){g.dispose();m.dispose()}}
}
