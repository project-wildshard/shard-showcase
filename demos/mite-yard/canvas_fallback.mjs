import {Color,Vector3} from 'three'
import {CONCRETE_SIZE,concretePixels,floorScanline} from './concrete-surface.mjs'
import {ARENA} from './combat.mjs'

// Small painter's algorithm for devices without WebGL. It renders the same animated Three scene.
export function canvasRenderer(canvas){
 const ctx=canvas.getContext('2d',{alpha:false})
 if(!ctx)throw new Error('No usable canvas renderer')
 const shadowMap={}
 const layer=canvas.ownerDocument.createElement('canvas'),layerCtx=layer.getContext('2d')
 const texture=concretePixels(true),mask=CONCRETE_SIZE-1
 let rasterGrain,lastGrainPose
 const floor=[[-ARENA.width/2,-ARENA.depth/2],[ARENA.width/2,-ARENA.depth/2],
  [ARENA.width/2,ARENA.depth/2],[-ARENA.width/2,ARENA.depth/2]]

 let ratio=1
 function setSize(w,h){canvas.width=Math.round(w*ratio);canvas.height=Math.round(h*ratio)}
 const temp=new Vector3(),a=new Vector3(),b=new Vector3()
 const eye=new Vector3(),center=new Vector3(),half=new Vector3()
 const light=new Vector3(-8,14,8).normalize()
 const css=(m,normal,distance,cameraPosition,fog,tint)=>{
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
  if(tint)color.multiply(tint)
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
  const raster=p=>[w*(.5-p.x*proj[0]/p.z*.5),h*(.5+p.y*proj[5]/p.z*.5)]
  const drawConcrete=()=>{
   if(!layerCtx)return
   const bounds=cut(floor.map(([x,z])=>new Vector3(x,0,z).applyMatrix4(inv))).map(raster)
   if(bounds.length<3)return
   const roll=camera.rotation.z
   // Use fixed padding so dodge roll does not resize/reallocate mid-swing.
   const margin=Math.ceil(.076*Math.max(w,h)),width=Math.ceil((w+2*margin)/2),height=Math.ceil((h+2*margin)/2)
   if(!rasterGrain||layer.width!==width||layer.height!==height){
    layer.width=width;layer.height=height;rasterGrain=layerCtx.createImageData(width,height);lastGrainPose=null
   }
   const sx=(w+2*margin)/width,sy=(h+2*margin)/height,acc=rasterGrain.data
   const view={w,h,fx:proj[0],fy:proj[5],yaw:-camera.rotation.y,pitch:camera.rotation.x,x:eye.x,y:eye.y,z:eye.z}
   const pose=[w,h,view.fx,view.fy,view.yaw,view.pitch,eye.x,eye.y,eye.z]
   if(!lastGrainPose||pose.some((v,i)=>Math.abs(v-lastGrainPose[i])>.001)){
    for(let row=0,i=3;row<height;row++){
     const sample=floorScanline(view,(row+.5)*sy-margin)
     if(!sample){
      for(let j=0;j<width;j++,i+=4)acc[i]=0
      continue
     }
     const {du,dv,opacity}=sample
     let u=(sample.u+du*(sx*.5-margin))*4096,v=(sample.v+dv*(sx*.5-margin))*4096
     const us=du*sx*4096,vs=dv*sx*4096
     for(let j=0;j<width;j++,i+=4,u+=us,v+=vs){
      acc[i]=texture[((((v>>12)&mask)*CONCRETE_SIZE+((u>>12)&mask))*4)+3]*opacity
     }
    }
    layerCtx.putImageData(rasterGrain,0,0);lastGrainPose=pose
   }
   ctx.save();ctx.beginPath();ctx.moveTo(...bounds[0])
   for(let j=1;j<bounds.length;j++)ctx.lineTo(...bounds[j])
   ctx.closePath();ctx.clip()
   ctx.translate(w/2,h/2);ctx.rotate(roll);ctx.translate(-w/2,-h/2)
   ctx.globalAlpha=1
   ctx.drawImage(layer,-margin,-margin,w+2*margin,h+2*margin)
   ctx.restore()
  }
  scene.traverseVisible(o=>{
   if(!o.isMesh)return
   const geom=o.geometry,ps=geom.getAttribute('position'),idx=geom.index,colors=o.userData.verticalTint?geom.getAttribute('color'):null
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
    const screen=clipped.map(raster)
    if([0,1].some(d=>screen.every(p=>p[d]<0)||screen.every(p=>p[d]>(d===0?w:h))))continue
    let m=o.material
    if(Array.isArray(m))m=m[geom.groups.find(g=>i>=g.start&&i<g.start+g.count)?.materialIndex??0]
    if(!m?.color)continue
    const normal=a.subVectors(world[ids[1]],world[ids[0]]).cross(b.subVectors(world[ids[2]],world[ids[0]])).normalize()
    const depth=clipped.reduce((t,p)=>t+p.z,0)/clipped.length
    center.copy(world[ids[0]]).add(world[ids[1]]).add(world[ids[2]]).multiplyScalar(1/3)
    let style
    if(colors&&clipped===vs){
     // Each wall triangle has two equal tint endpoints and one on the
     // opposite edge. Project that world-space gradient across its face.
     const idsByY=[0,1,2].sort((a,b)=>world[ids[a]].y-world[ids[b]].y)
     const [low,mid,high]=idsByY
     const sa=screen[low],sb=screen[high]
     const pairLow=world[ids[mid]].y===world[ids[low]].y
     const [p,q,r]=pairLow?[sa,screen[mid],sb]:[sb,screen[mid],sa]
     const x=q[0]-p[0],y=q[1]-p[1],len=x*x+y*y
     if(len>.01){
      const t=((r[0]-p[0])*x+(r[1]-p[1])*y)/len,ax=p[0]+t*x,ay=p[1]+t*y
      if(Math.hypot(r[0]-ax,r[1]-ay)>.4){
       style=ctx.createLinearGradient(ax,ay,r[0],r[1])
       const make=j=>css(m,normal,-depth,eye,scene.fog,new Color().fromBufferAttribute(colors,ids[j]))
       style.addColorStop(0,make(pairLow?low:high));style.addColorStop(1,make(pairLow?high:low))
      }
     }
    }
    if(!style)style=css(m,normal,-depth,eye,scene.fog, colors?new Color().fromBufferAttribute(colors,ids[0]):null)
    list.push([o.userData.paintLayer!==undefined?-1e9+o.userData.paintLayer:depth,screen,style,m.transparent?m.opacity:1])
   }
  })
  list.sort((p,q)=>p[0]-q[0])
  let painted=false
  for(const [order,v,style,alpha] of list){
   // Texture the base before lane paint, spalls, occlusion, and actors.
   if(!painted&&order>-1e9){drawConcrete();painted=true}
   ctx.globalAlpha=alpha
   ctx.fillStyle=style;ctx.strokeStyle=style;ctx.lineWidth=.61
   ctx.beginPath();ctx.moveTo(...v[0]);for(let i=1;i<v.length;i++)ctx.lineTo(...v[i]);ctx.closePath();ctx.fill();if(alpha===1)ctx.stroke()
  }
  ctx.globalAlpha=1
 }
 return {shadowMap,render,setSize,getPixelRatio:()=>ratio,setPixelRatio:r=>{ratio=Math.min(1,r)}}
}
