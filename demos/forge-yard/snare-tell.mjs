import * as T from 'three';
import {SNARE_RADIUS} from './arena.mjs';

export function snarePhase(enemy){
 if(enemy.attack!=='burrow'||enemy.life<=0||!enemy.mark)return null;
 if(enemy.state==='windup')return {phase:'windup',radius:SNARE_RADIUS,factor:Math.min(1,enemy.t/enemy.windReady)};
 if(enemy.state==='active'&&enemy.t<.24)return {phase:'release',radius:SNARE_RADIUS,factor:enemy.t/.24};
 return null;
}
export function createSnareTell(scene){
 const g=new T.Group();g.name='Snare warning tessellation';scene.add(g);
 g.rotation.x=-Math.PI/2;
 const plate=(geo,color,order)=>{
  const m=new T.MeshBasicMaterial({color,transparent:true,opacity:0,depthWrite:false,side:T.DoubleSide,toneMapped:false});
  const o=new T.Mesh(geo,m);o.renderOrder=order;g.add(o);return o;
 };
 const rim=plate(new T.RingGeometry(.954,1,64),0xff8042,6);
 const fill=plate(new T.CircleGeometry(.95,64),0xc45a31,5);
 const chevrons=[];
 for(let i=0;i<8;i++){
  const geo=new T.BufferGeometry();
  geo.setAttribute('position',new T.Float32BufferAttribute([-.077,.88,0,0,.72,0,.077,.88,0],3));
  const tooth=plate(geo,0xffcc75,7);
  tooth.rotation.z=i*Math.PI*.25;chevrons.push(tooth);
 }
 const discharge=new T.Group();discharge.name='Snare emergence sparks';scene.add(discharge);
 const fin=new T.OctahedronGeometry(.08,0),m=new T.MeshBasicMaterial({color:0xffd49e,toneMapped:false,transparent:true,depthWrite:false});
 const plume=new T.InstancedMesh(fin,m,9);discharge.add(plume);plume.frustumCulled=false;
 const loc=new T.Object3D();
 return enemy=>{
  const state=snarePhase(enemy);
  g.visible=!!state;discharge.visible=state?.phase==='release';if(!state)return null;
  const {x,z}=enemy.mark,{phase,radius,factor}=state;
  g.position.set(x,.035,z);g.scale.setScalar(radius);
  const striking=phase==='release';
  rim.material.opacity=striking?.96*(1-factor):.89;
  fill.material.opacity=striking?.35*(1-factor):.14+.17*factor;
  for(const o of chevrons){
   o.visible=!striking;
   o.scale.set(1,1-.13*factor,1);
   o.material.opacity=.62+.31*factor;
  }
  if(striking){
   discharge.position.set(x,.07,z);
   const r=.22+.58*factor;
   m.opacity=1-factor;
   for(let i=0;i<9;i++){
    const a=i*2*Math.PI/9,scale=1-factor*.58;
    loc.position.set(r*Math.cos(a),.13+.67*Math.sin(Math.PI*factor)*(i%3+1)/3,r*Math.sin(a));
    loc.scale.set(scale,scale*2.2,scale);
    loc.rotation.set(.5+a,.33,a);
    loc.updateMatrix();plume.setMatrixAt(i,loc.matrix);
   }
   plume.instanceMatrix.needsUpdate=true;
  }
  return state;
 };
}
