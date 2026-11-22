import * as T from 'three'
import {SWORD_SWING,armorInView,clamp} from './combat.mjs'
const material=(color,roughness,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness})
const poly=(v,indices,mats,groups)=>{
 const g=new T.BufferGeometry()
 const bins=mats.map(()=>[])
 for(let i=0;i<groups.length;i++)bins[groups[i]].push(...indices[i])
 g.setAttribute('position',new T.Float32BufferAttribute(v.flat(),3));g.setIndex(bins.flat())
 const flat=g.toNonIndexed();g.dispose();flat.computeVertexNormals()
 let base=0
 for(let i=0;i<bins.length;i++){
  const count=bins[i].length
  if(count)flat.addGroup(base,count,i)
  base+=count
 }
 return new T.Mesh(flat,mats)
}
function mesh(group,g,m,x=0,y=0,z=0){
 const o=new T.Mesh(g,m);o.position.set(x,y,z);group.add(o);return o
}
function capsule(group,m,a,b,r){
 const A=new T.Vector3(...a),B=new T.Vector3(...b),axis=B.clone().sub(A)
 const o=mesh(group,new T.CapsuleGeometry(r,axis.length(),3,8),m)
 o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),axis.normalize());o.position.copy(A).lerp(B,.5)
 return o
}
function rings(group,rows,segments,m,dz=1){
 const v=[],i=[]
 for(const [y,r] of rows)for(let j=0;j<segments;j++){
  const a=j/segments*Math.PI*2;v.push([Math.cos(a)*r,y,Math.sin(a)*r*dz])
 }
 for(let y=0;y<rows.length-1;y++)for(let x=0;x<segments;x++){
  const a=y*segments+x,b=y*segments+(x+1)%segments
  i.push(a,a+segments,b,b,a+segments,b+segments)
 }
 const g=new T.BufferGeometry()
 g.setAttribute('position',new T.Float32BufferAttribute(v.flat(),3));g.setIndex(i)
 g.computeVertexNormals();return mesh(group,g,m)
}
function blade(group,materials){
 // Cold steel, four longitudinal grind rails and a recessed fuller.
 // Rows are strike/draw marks on a forged tool, not a paint pattern.
 const cols=[[-1,0],[-.915,.004],[-.77,.009],[-.62,.010],
  [-.39,.011],[-.28,.011],[-.20,.005],[.20,.005],[.28,.011],
  [.39,.011],[.62,.010],[.77,.009],[.915,.004],[1,0]]
 // y, half-width, center offset, fuller depth, steel variation cycle.
 const rows=[
  [.105,.040,0,0,0],[.147,.051,0,.86,0],[.181,.0495,0,.89,0],
  [.231,.0478,.0003,.92,0],[.237,.0475,.0003,.93,2],[.296,.0457,.0008,.95,0],
  [.357,.0435,.0011,.97,0],[.397,.042,.0014,.98,0],[.403,.0416,.0014,.99,2],
  [.455,.0391,.0019,1,0],[.49,.037,.002,1,0],[.55,.032,.004,0,0],[.64,.002,.012,0,0],
 ]
 const v=[],faces=[],groups=[]
 for(const sign of [1,-1]){
  const start=v.length
  for(const [y,w,l,groove] of rows)for(let k=0;k<cols.length;k++){
   const [x,d]=cols[k],height=k===6||k===7?.011+(.005-.011)*groove:d
   v.push([x*w+l,y,sign*(.0015+height*(1-y*.46))])
  }
  for(let j=0;j<rows.length-1;j++)for(let k=0;k<cols.length-1;k++){
   const a=start+j*cols.length+k,b=a+cols.length
   faces.push(sign===1?[a,a+1,b,b,a+1,b+1]:[a,b,a+1,b,b+1,a+1])
   const mark=rows[j+1][4]===2?2:0,side=sign===1?0:1
   let band=1
   if(k===0||k===12)band=j===7&&k===side*12?6:0
   else if(k===1||k===11)band=mark===2&&(k===1)!==Boolean(side)?4:3
   else if(k===6&&j>0&&j<10)band=2
   else if(k===5||k===7)band=4
   else if(k===2||k===10)band=5
   else if(mark===2&&(k+side)%3===0)band=6
   groups.push(band)
  }
 }
 const stride=cols.length,back=rows.length*stride
 for(let j=0;j<rows.length-1;j++){
  const a=j*stride,b=a+stride
  faces.push([a,a+back,b,b,a+back,b+back]);groups.push(0)
  const c=a+stride-1,d=b+stride-1
  faces.push([c,d,c+back,d,d+back,c+back]);groups.push(0)
 }
 const o=poly(v,faces,materials,groups);o.name='Forged stepped fuller and steel cutting bevel';group.add(o)
}
export function createViewmodel(){
 const root=new T.Group();root.name='Iron work sword and travel gauntlet'
 const sword=new T.Group();root.add(sword)
 const glove=material(0x664936,.77),seam=material(0x291d16,.95)
 const bronze=material(0xc18a43,.38,.62),blackIron=material(0x38474a,.41,.75)
 const steel=material(0x8faaa9,.30,.73),edge=material(0xdbe7dc,.23,.8),fuller=material(0x385156,.49,.67)
 const grind=material(0xb2c2ba,.28,.73),heel=material(0x7e9896,.38,.66)
 const satin=material(0xa4b7b3,.34,.68),nick=material(0x697e7c,.48,.55)
 blade(sword,[edge,steel,fuller,grind,heel,satin,nick])
 rings(sword,[[-.148,.017],[-.141,.029],[-.11,.034],[-.085,.022],[-.067,.022],[.08,.025],[.091,.032],[.108,.024]],8,blackIron,.85)
 for(let i=0;i<10;i++){
  const y=-.071+i*.015
  rings(sword,[[y,.023],[y+.004,.0275],[y+.010,.025]],8,seam,.84)
 }
 for(const x of [-1,1]){
  const guard=mesh(sword,new T.SphereGeometry(.045,9,5),bronze,.054*x,.098,-.002)
  guard.scale.set(1.65,.34,.69);guard.rotation.z=.20*x
  mesh(sword,new T.SphereGeometry(.013,8,4),blackIron,.123*x,.114,-.002)
 }
 const ferrule=rings(sword,[[.078,.032],[.095,.036],[.110,.034],[.120,.025]],8,bronze,.82)
 ferrule.name='Brass ferrule'
 const arm=new T.Group();root.add(arm)
 capsule(arm,glove,[.093,-.209,.164],[.043,-.086,.066],.057)
 capsule(arm,glove,[.045,-.086,.064],[.036,-.022,.050],.050)
 capsule(arm,blackIron,[.087,-.196,.15],[.064,-.156,.117],.061)
 capsule(arm,bronze,[.071,-.168,.124],[.066,-.160,.116],.063)
 // Four rounded gauntlet fingers with a separately angled thumb crossing the grip.
 for(let i=0;i<4;i++){
  const y=.042-i*.027,r=.0128-i*.00045
  capsule(arm,glove,[.041,y,.035],[.013,y+.004,-.020],r)
  capsule(arm,i===0?glove:seam,[.013,y+.003,-.020],[-.013,y-.003,-.030],r)
  const rivet=mesh(arm,new T.SphereGeometry(.006,6,4),bronze,.034,y,.026)
  rivet.scale.set(.65,.88,.63)
 }
 capsule(arm,glove,[.037,-.041,.085],[.006,.008,.043],.020)
 capsule(arm,glove,[.006,.008,.043],[-.036,.021,.017],.018)
 return root
}

const {impact,end}=SWORD_SWING
const ready=[.283,-.364,-.745,.17,-.25,-.33]
const keys=[
 [0,ready],
 [.072,[.42,-.40,-.67,.42,-.62,-.92]],
 [impact,[.16,-.36,-.76,.54,-.25,.94]],
 [.238,[-.28,-.42,-.70,.91,.24,1.70]],
 [end,ready],
]
const rightKeys=[
 [0,ready],
 [.072,[.39,-.39,-.68,.47,-.57,-1.02]],
 [impact,[.217,-.36,-.76,.70,-.18,0]],
 [.238,[-.145,-.43,-.70,.96,.10,1.25]],
 [end,ready],
]
export function portraitRightCut(player,mite,aspect){
 if(aspect>=.75||mite.phase==='die')return 0
 const dx=mite.x-player.x,dz=mite.z-player.z
 const ahead=dx*Math.sin(player.yaw)-dz*Math.cos(player.yaw)
 const x=dx*Math.cos(player.yaw)+dz*Math.sin(player.yaw)
 if(ahead<=0||x<=0||Math.hypot(x,ahead)>2.65||!armorInView(player,mite,aspect))return 0
 return clamp((Math.atan2(x,ahead)-.10)/.20,0,1)
}
export function swordPose(elapsed,rightCut=0){
 const t=clamp(elapsed,0,end)
 if(t===end)return ready.slice()
 const last=keys.findIndex(k=>k[0]>=t)
 if(last<=0)return ready.slice()
 const [a,lo]=keys[last-1],[b,hi]=keys[last]
 const q=(t-a)/(b-a),fade=q*q*(3-2*q)
 const mix=(u,v)=>u+(v-u)*fade
 return lo.map((v,i)=>{
  const original=mix(v,hi[i])
  return original+(mix(rightKeys[last-1][1][i],rightKeys[last][1][i])-original)*rightCut
 })
}
export function poseViewmodel(mesh,elapsed,clock=0,moving=false,aspect=1,rightCut=0){
 const [x,y,z,rx,ry,rz]=swordPose(elapsed,rightCut)
 const settled=elapsed<=0||elapsed>=end
 const framing=Math.min(1,aspect)
 const phone=Math.max(0,1-aspect/.86)
 mesh.scale.setScalar((.46+.54*framing)*(1-.34*phone*(settled?1:.55)))
 mesh.position.set(x*framing+(settled?Math.sin(clock*6.6)*.004:0),y*(.70+.30*framing)-phone*(settled?.20:.05)+(settled?Math.sin(clock*(moving?10:5))*(moving?.009:.004):0),z)
 mesh.rotation.set(rx,ry,rz*(.19+.81*framing*framing),'YXZ')
}

// This chooses a presentation point only after the simulation confirms
// damage. Preserve centered hits; show glancing feedback on the shoulder
// nearest the frame center if the old front-of-chassis origin is cropped.
export function swordImpactPoint(player,mite,project){
 const dx=player.x-mite.x,dz=player.z-mite.z,dist=Math.hypot(dx,dz)||1
 const nx=dx/dist,nz=dz/dist
 const origin=[mite.x+nx*.23,.44,mite.z+nz*.23]
 const {x:projectedX,z:projectedDepth}=project(origin)
 const weight=clamp((Math.abs(projectedX)-.48)/.44,0,1)
 if(!weight||projectedDepth<-1||projectedDepth>1)return origin
 const shift=-Math.sign(projectedX)*.31*weight
 const shoulder=[origin[0]+nz*shift+nx*.085*weight,origin[1]+.145*weight,origin[2]-nx*shift+nz*.085*weight]
 const edge=project(shoulder)
 return Math.abs(edge.x)<Math.abs(projectedX)&&Math.abs(edge.y)<.98?shoulder:origin
}
