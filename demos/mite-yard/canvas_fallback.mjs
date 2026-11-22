import {Vector3} from 'three'

// Small painter's algorithm for devices without WebGL. It renders the same animated Three scene.
export function canvasRenderer(canvas){
 const ctx=canvas.getContext('2d',{alpha:false})
 if(!ctx)throw new Error('No usable canvas renderer')
 const shadowMap={}
 let ratio=1
 function setSize(w,h){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 const temp=new Vector3(),a=new Vector3(),b=new Vector3()
 const eye=new Vector3(),center=new Vector3(),half=new Vector3()
 const light=new Vector3(-8,14,8).normalize()
 const css=(m,normal,distance,cameraPosition,fog)=>{
  if(m.isMeshBasicMaterial)return m.color.getStyle()
  const sun=Math.max(0,normal.dot(light))
  const sky=.30+.17*Math.max(0,normal.y)
  const metal=m.metalness??0
  let shine=0
  if(sun>0&&metal>.10){
   half.subVectors(cameraPosition,center).normalize().add(light).normalize()
   const lobe=Math.max(0,normal.dot(half))**(6+26*(1-(m.roughness??.6)))
   shine=lobe*metal*sun*.32
  }
  const color=m.color.clone()
  color.r=color.r*(sky*.82+sun*.58)+shine*(.38+color.r*.8)
  color.g=color.g*(sky*.98+sun*.43)+shine*(.34+color.g*.8)
  color.b=color.b*(sky*1.19+sun*.29)+shine*(.29+color.b*.8)
  const t=m.emissive
  if(t){color.r+=t.r*m.emissiveIntensity*.34;color.g+=t.g*m.emissiveIntensity*.34;color.b+=t.b*m.emissiveIntensity*.34}
  if(fog&&distance>fog.near)color.lerp(fog.color,Math.min(1,(distance-fog.near)/(fog.far-fog.near)))
  return color.getStyle()
 }
 function render(scene,camera){
  scene.updateMatrixWorld(true);camera.updateMatrixWorld(true)
  eye.setFromMatrixPosition(camera.matrixWorld)
  const w=canvas.width,h=canvas.height
  ctx.fillStyle=scene.background.getStyle();ctx.fillRect(0,0,w,h)
  const list=[],near=.06,inv=camera.matrixWorldInverse,proj=camera.projectionMatrix.elements
  const edge=(p,q)=>{
   const t=(-near-p.z)/(q.z-p.z)
   return new Vector3(p.x+(q.x-p.x)*t,p.y+(q.y-p.y)*t,-near)
  }
  const cut=(vs)=>{
   const buf=[]
   for(let j=0;j<vs.length;j++){
    const p=vs[j],q=vs[(j+1)%vs.length],f=p.z<=-near,g=q.z<=-near
    if(f)buf.push(p);if(f!==g)buf.push(edge(p,q))
   }
   return buf
  }
  scene.traverseVisible(o=>{
   if(!o.isMesh)return
   const geom=o.geometry,ps=geom.getAttribute('position'),idx=geom.index
   if(!ps)return
   if(o.isSkinnedMesh)o.skeleton.update()
   const world=[],local=[]
   for(let i=0;i<ps.count;i++){
    temp.fromBufferAttribute(ps,i)
    if(o.isSkinnedMesh)o.applyBoneTransform(i,temp)
    const v=temp.clone().applyMatrix4(o.matrixWorld)
    world.push(v);local.push(v.clone().applyMatrix4(inv))
   }
   for(let i=0;i<(idx?.count??ps.count);i+=3){
    const ids=[i,i+1,i+2].map(j=>idx?idx.getX(j):j)
    const vs=ids.map(j=>local[j])
    if(vs.every(v=>v.z>-near))continue
    const clipped=vs.every(v=>v.z<=-near)?vs:cut(vs)
    if(clipped.length<3)continue
    const screen=clipped.map(p=>[w*(.5-p.x*proj[0]/p.z*.5),h*(.5+p.y*proj[5]/p.z*.5)])
    if([0,1].some(d=>screen.every(p=>p[d]<0)||screen.every(p=>p[d]>(d===0?w:h))))continue
    let m=o.material
    if(Array.isArray(m))m=m[geom.groups.find(g=>i>=g.start&&i<g.start+g.count)?.materialIndex??0]
    if(!m?.color)continue
    const normal=a.subVectors(world[ids[1]],world[ids[0]]).cross(b.subVectors(world[ids[2]],world[ids[0]])).normalize()
    const depth=clipped.reduce((t,p)=>t+p.z,0)/clipped.length
    center.copy(world[ids[0]]).add(world[ids[1]]).add(world[ids[2]]).multiplyScalar(1/3)
    list.push([o.userData.paintLayer!==undefined?-1e9+o.userData.paintLayer:depth,screen,css(m,normal,-depth,eye,scene.fog),m.transparent?m.opacity:1])
   }
  })
  list.sort((p,q)=>p[0]-q[0])
  for(const [_,v,style,alpha] of list){
   ctx.globalAlpha=alpha
   ctx.fillStyle=style;ctx.strokeStyle=style;ctx.lineWidth=.61
   ctx.beginPath();ctx.moveTo(...v[0]);for(let i=1;i<v.length;i++)ctx.lineTo(...v[i]);ctx.closePath();ctx.fill();if(alpha===1)ctx.stroke()
  }
  ctx.globalAlpha=1
 }
 return {shadowMap,render,setSize,getPixelRatio:()=>ratio,setPixelRatio:r=>{ratio=Math.min(1,r)}}
}
