import {Vector3} from 'three'

// Small painter's algorithm for devices without WebGL. It renders the same animated Three scene.
export function canvasRenderer(canvas){
 const ctx=canvas.getContext('2d',{alpha:false})
 if(!ctx)throw new Error('No usable canvas renderer')
 const shadowMap={}
 let ratio=1
 function setSize(w,h){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 const temp=new Vector3(),a=new Vector3(),b=new Vector3(),light=new Vector3(-.42,.8,.47).normalize()
 const css=(color,k,out)=>{
  const s=color.clone().multiplyScalar(k)
  const t=out?.emissive
  if(t){s.r+=t.r*out.emissiveIntensity*.34;s.g+=t.g*out.emissiveIntensity*.34;s.b+=t.b*out.emissiveIntensity*.34}
  return s.getStyle()
 }
 function render(scene,camera){
  scene.updateMatrixWorld(true);camera.updateMatrixWorld(true)
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
    const power=.57+.42*Math.max(0,normal.dot(light))
    list.push([o.userData.paintLayer!==undefined?-1e9+o.userData.paintLayer:clipped.reduce((t,p)=>t+p.z,0)/clipped.length,screen,css(m.color,power,m),m.transparent?m.opacity:1])
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
