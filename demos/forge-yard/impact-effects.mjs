import * as T from 'three';
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const TRAIL_COUNT=9,POOL=24;
// This is an art anchor for the simulation's confirmed hit, not geometry collision.
export function surfaceCue(player,rival,weakHeight){
 const dx=player.x-rival.x,dz=player.z-rival.z,r=Math.max(.12,rival.r);
 const d=Math.hypot(dx,dz),[ux,uz]=d>.0001?[dx/d,dz/d]:[0,1];
 const h=Number.isFinite(weakHeight)?weakHeight:rival.height*.59;
 return {at:[rival.x+ux*r*.83,clamp(h,.18,rival.height*.68),rival.z+uz*r*.83],outer:[ux,0,uz]};
}
export function createImpactEffects(scene){
 const group=new T.Group();group.name='Bounded style trails and impact cues';scene.add(group);
 const vertexCount=(TRAIL_COUNT-1)*6,pg=new T.BufferGeometry();
 const positions=new Float32Array(vertexCount*3),colors=new Float32Array(vertexCount*4);
 const pa=new T.BufferAttribute(positions,3).setUsage(T.DynamicDrawUsage),ca=new T.BufferAttribute(colors,4).setUsage(T.DynamicDrawUsage);
 pg.setAttribute('position',pa);pg.setAttribute('color',ca);pg.setDrawRange(0,0);
 const ribbon=new T.Mesh(pg,new T.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:.57,depthWrite:false,side:T.DoubleSide,toneMapped:false}));
 ribbon.frustumCulled=false;ribbon.renderOrder=5;group.add(ribbon);
 const sparkMat=new T.MeshBasicMaterial({transparent:true,opacity:.77,depthWrite:false,blending:T.AdditiveBlending,toneMapped:false});
 const sparks=new T.InstancedMesh(new T.BoxGeometry(.036,1,.026),sparkMat,POOL);sparks.count=0;sparks.frustumCulled=false;sparks.renderOrder=6;group.add(sparks);
 const seal=new T.Mesh(new T.RingGeometry(.66,1,24,1,.16,Math.PI*1.72),
  new T.MeshBasicMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,toneMapped:false}));
 seal.visible=false;seal.renderOrder=6;group.add(seal);
 const trail=[],particles=[],rgb=new T.Color(),o=new T.Object3D(),n=new T.Vector3(),h=new T.Vector3(),v=new T.Vector3(),axis=new T.Vector3(0,1,0);
 let stamp=0,sealAge=1,serial=0;
 function clear(){
  trail.length=0;particles.length=0;seal.visible=false;sealAge=1;sparks.count=0;
  pg.setDrawRange(0,0);stamp=0;
 }
 function hit(point,outer,style,blocked){
  const t=[-outer[2],0,outer[0]],tint=blocked?0x8bd9f2:style==='chop'?0xff9f58:0xffc27d;
  serial++;
  const q=blocked?7:11,life=blocked?.20:.255;
  for(let j=0;j<q;j++){
   const a=(serial*.67+j*2.39996)%Math.PI*2,toSide=Math.cos(a),rise=.31+Math.abs(Math.sin(a))*.92;
   const tangent=style==='sweep'?1.04:style==='chop'?.60:.36,force=1.11+(j%4)*.32;
   const nudge=(j%3-.5)*.023;
   const speed=[(outer[0]*.55+t[0]*toSide*tangent)*force,rise*force,(outer[2]*.55+t[2]*toSide*tangent)*force];
   if(particles.length===POOL)particles.shift();
   particles.push({at:[point[0]+nudge,point[1]+nudge,point[2]],speed,age:0,max:life-.013*(j%4),tint});
  }
  seal.position.set(...point);seal.position.x+=outer[0]*.11;seal.position.z+=outer[2]*.11;
  seal.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),n.set(...outer));
  seal.material.color.setHex(tint);sealAge=0;seal.visible=true;
 }
 function trailSample(dt,grip,tip,lit,style){
  stamp+=dt;
  while(trail.length&&trail[0].expires<stamp)trail.shift();
  if(lit&&grip&&tip){
   h.copy(tip).lerp(grip,.29);
   if(trail.length===TRAIL_COUNT)trail.shift();
   trail.push({h:h.clone(),t:tip.clone(),expires:stamp+.115});
  }
  rgb.setHex(style==='sweep'?0x77d9c9:style==='chop'?0xa6d6c7:0x8bc3f5);
  let i=0;
  const write=(p,a)=>{p.toArray(positions,i*3);colors.set([rgb.r,rgb.g,rgb.b,a],i++*4);};
  for(let j=1;j<trail.length;j++){
   const a=trail[j-1],b=trail[j],alpha=x=>clamp((x.expires-stamp)/.115,0,1);
   write(a.h,alpha(a)*.13);write(a.t,alpha(a)*.54);write(b.t,alpha(b)*.54);
   write(a.h,alpha(a)*.13);write(b.t,alpha(b)*.54);write(b.h,alpha(b)*.13);
  }
  pg.setDrawRange(0,i);if(i){pa.needsUpdate=true;ca.needsUpdate=true;}
  return i/6;
 }
 function stepParticles(dt){
  let i=0;
  for(let j=particles.length-1;j>=0;j--){
   const p=particles[j];p.age+=dt;
   if(p.age>=p.max){particles.splice(j,1);continue;}
   const age=p.age,energy=1-age/p.max;
   v.set(...p.speed);v.y-=2.1*age;
   o.position.set(p.at[0]+p.speed[0]*age,p.at[1]+p.speed[1]*age-1.05*age*age,p.at[2]+p.speed[2]*age);
   o.scale.set(Math.min(1.0,energy+.26),(.082+v.length()*.073)*energy,Math.min(1.0,energy+.26));
   o.quaternion.setFromUnitVectors(axis,v.normalize());o.updateMatrix();
   sparks.setMatrixAt(i,o.matrix);sparks.setColorAt(i++,rgb.setHex(p.tint).multiplyScalar(energy*.90));
  }
  sparks.count=i;
  if(i){sparks.instanceMatrix.needsUpdate=true;sparks.instanceColor.needsUpdate=true;}
  if(seal.visible){
   sealAge+=dt;seal.visible=sealAge<.181;
   seal.scale.setScalar(.092+sealAge*1.14);seal.material.opacity=.75*(1-sealAge/.181);
  }
  return i;
 }
 return {clear,hit,trailSample,stepParticles,age:()=>sealAge};
}
