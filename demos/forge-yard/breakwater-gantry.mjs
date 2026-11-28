import * as T from 'three';

export const GANTRY_Z=-12.55;
export const GANTRY_HEIGHT_SCALE=.57;
const GANTRY_OFFSET_X=-1.42;
export const GANTRY_PERIOD=18;
const ease=t=>t*t*(3-2*t);
// Haul out and back, easing through the load and unload dwell phases.
export function gantryPose(t){
 const p=((t%GANTRY_PERIOD)+GANTRY_PERIOD)%GANTRY_PERIOD/GANTRY_PERIOD;
 const run=p<.14?0:p<.44?ease((p-.14)/.30):p<.64?1:p<.94?1-ease((p-.64)/.30):0;
 const lift=p<.14?ease(p/.14):p<.44?1:p<.54?1-ease((p-.44)/.10):p<.64?ease((p-.54)/.10):p<.94?1:1-ease((p-.94)/.06);
 return {x:-7.4+5.6*run,drop:1.36-.96*lift,tilt:.046*Math.sin(p*Math.PI*4)*Math.sin(Math.PI*run)};
}
export function createBreakwaterGantry(scene){
 const root=new T.Group();root.position.set(GANTRY_OFFSET_X,0,GANTRY_Z);root.scale.y=GANTRY_HEIGHT_SCALE;root.name='Breakwater gantry and cargo cradle';scene.add(root);
 const carriage=new T.Group(),sling=new T.Group();
 carriage.position.y=4.46;root.add(carriage);carriage.add(sling);
 const box=new T.BoxGeometry(),tube=new T.CylinderGeometry(1,1,1,8);
 const steel=(color,metalness=.54,roughness=.48)=>new T.MeshStandardMaterial({color,metalness,roughness});
 const skins={
  iron:steel(0x22373d),salt:steel(0x818d88,.13,.77),copper:steel(0x8b5842),
  ochre:steel(0x9c592e,.39,.56),silver:steel(0x879c9e,.64,.37),blue:steel(0x395d60,.38,.54),
  mint:new T.MeshBasicMaterial({color:0x66bbba}),amber:new T.MeshBasicMaterial({color:0xffc587})
 };
 const temp=new T.Object3D(),up=new T.Vector3(0,1,0),a=new T.Vector3(),b=new T.Vector3(),delta=new T.Vector3();
 let batches=0,triangles=0,instances=0;
 function layer(parent,f){
  const bank=new Map();
  function put(geo,skin,x,y,z,sx,sy,sz,q){
   const key=geo.id+':'+skin;if(!bank.has(key))bank.set(key,{geo,mat:skins[skin],m:[]});
   temp.position.set(x,y,z);temp.scale.set(sx,sy,sz);
   if(q)temp.quaternion.copy(q);else temp.quaternion.identity();
   temp.updateMatrix();bank.get(key).m.push(temp.matrix.clone());
  }
  const block=(m,x,y,z,sx,sy,sz)=>put(box,m,x,y,z,sx,sy,sz);
  const ring=(m,x,y,z,r,h)=>put(tube,m,x,y,z,r,h,r);
  const brace=(m,v,w,thick)=>{
   a.fromArray(v);b.fromArray(w);delta.subVectors(b,a);const length=delta.length();
   const mid=a.addScaledVector(delta,.5);
   put(box,m,mid.x,mid.y,mid.z,thick,length,thick,temp.quaternion.setFromUnitVectors(up,delta.normalize()));
  };
  f(block,ring,brace);
  for(const {geo,mat,m} of bank.values()){
   const o=new T.InstancedMesh(geo,mat,m.length);parent.add(o);
   m.forEach((matrix,n)=>o.setMatrixAt(n,matrix));o.instanceMatrix.needsUpdate=true;o.computeBoundingSphere();
   batches++;instances+=m.length;triangles+=geo.index.count/3*m.length;
  }
 }
 layer(root,(B,R,S)=>{
  for(const x of [-9.0,1.1]){
   R('salt',x,-.48,0,1.16,1.26);R('copper',x,.115,0,.91,.19);
   for(const z of [-.83,.83]){
    R('iron',x,.22,z,.34,.25);
    S('iron',[x,.20,z],[x,4.61,z*.51],.31);
    S('copper',[x,.48,z],[x,3.79,-z*.56],.15);
    B('silver',x,4.51,z*.50,.45,.36,.32);
   }
   B('ochre',x,3.69,0,.49,.14,1.47);
  }
  for(const z of [-.50,.50]){
   B('iron',-4,4.59,z,10.78,.28,.21);B('copper',-4,5.25,z,10.72,.22,.19);
   B('silver',-4,4.75,z,10.68,.055,.08);
   for(let i=0;i<10;i++){
    const x=-9+i;
    S(i%2?'iron':'ochre',[x,4.69,z],[x+1,5.21,z],.103);
    B('iron',x,4.92,z,.11,.61,.11);
    B('silver',x,4.80,z+Math.sign(z)*.10,.095,.060,.032);
   }
  }
  for(let i=0;i<9;i++)B('iron',-8.5+i,5.26,0,.094,.108,1.09);
  for(const x of [-9.22,.57])for(const z of [-.49,.49])B('amber',x,4.52,z,.23,.11,.15);
  // Maintenance cabin and glazed window on the walkway's inner side.
  B('blue',-.36,3.78,.02,1.07,.95,1.14);
  B('iron',-.36,4.28,.02,1.22,.13,1.23);
  B('mint',-.34,3.93,.599,.71,.26,.02);
  for(const x of [-.55,-.12])B('iron',x,3.93,.617,.035,.31,.026);
  B('silver',-.36,3.22,.05,1.46,.105,1.40);
  for(const x of [-.99,.29])B('ochre',x,3.42,.759,.085,.49,.084);
  B('iron',-.35,3.65,.767,1.36,.044,.058);
 });
 layer(carriage,(B,R)=>{
  B('ochre',0,0,0,.83,.23,1.16);B('iron',0,-.16,0,.58,.19,.65);
  for(const x of [-.26,.26])for(const z of [-.48,.48])R('silver',x,.18,z,.12,.13);
 });
 layer(sling,(B)=>{
  B('ochre',0,-.37,0,1.37,.73,.78);
  for(const x of [-.54,-.27,0,.27,.54])B('copper',x,-.37,.40,.088,.65,.055);
  for(const y of [-.69,-.065])B('iron',0,y,0,1.45,.099,.83);
  for(const x of [-.67,.67])B('silver',x,-.37,.416,.043,.65,.052);
  B('amber',0,-.195,.433,.16,.073,.020);
 });
 const cable=new T.InstancedMesh(box,skins.iron,2);
 const cableMatrix=new T.Matrix4();carriage.add(cable);
 batches++;instances+=2;triangles+=24;
 return {batches,instances,triangles,step(t){
  const v=gantryPose(t);carriage.position.x=v.x;
  sling.position.y=-v.drop;sling.rotation.z=v.tilt;
  for(let i=0;i<2;i++){
   const x=i?.41:-.41;
   a.set(x*.65,-.15,0);
   b.set(x*Math.cos(v.tilt),-v.drop+x*Math.sin(v.tilt),0);
   delta.subVectors(b,a);
   const length=delta.length();a.addScaledVector(delta,.5);
   cableMatrix.compose(a,temp.quaternion.setFromUnitVectors(up,delta.normalize()),temp.scale.set(.035,length,.035));
   cable.setMatrixAt(i,cableMatrix);
  }
  cable.instanceMatrix.needsUpdate=true;cable.frustumCulled=false;
  return {...v,x:v.x+GANTRY_OFFSET_X};
 }};
}
