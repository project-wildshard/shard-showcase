import * as T from 'three';
import {SURGE} from './breakwater-surge.mjs';

export function createSurgeFx(scene){
 const {x,halfWidth,near,far}=SURGE,width=2*halfWidth,run=far-near,mid=(near+far)*.5;
 const group=new T.Group();group.name='Animated Breakwater tide marks';scene.add(group);
 function decal(color,opacity,order){
  const mat=new T.MeshBasicMaterial({color,opacity,transparent:true,depthWrite:false,toneMapped:false});
  const o=new T.Mesh(new T.PlaneGeometry(1,1),mat);
  o.rotation.x=-Math.PI/2;o.renderOrder=order;group.add(o);return o;
 }
 const edges=[decal(0x73ced5,.76,6),decal(0x73ced5,.76,6)];
 const under=decal(0x126675,.19,3),timer=decal(0x479ba8,.3,4);
 const water=decal(0x4bc5cc,.69,9),crest=decal(0xd8f9eb,.95,10);
 const ripples=Array.from({length:5},()=>decal(0xcff3ed,.34,10));
 function fit(o,center,y,z,w,l){o.position.set(center,y,z);o.scale.set(w,Math.max(.001,l),1);}
 fit(under,x,.034,mid,width,run);
 for(let i=0;i<2;i++)fit(edges[i],x+(i?1:-1)*(halfWidth-.023),.040,mid,.046,run);
 return state=>{
  group.visible=!!state;if(!state)return;
  const warning=state.phase==='warn';
  for(const o of [timer,under,...edges])o.visible=warning;
  for(const o of [water,crest,...ripples])o.visible=!warning;
  if(warning){
   const left=run*state.remaining;
   fit(timer,x,.035,far-left*.5,width*.97,left);
  }else{
   const length=state.hi-state.lo;
   fit(water,x,.048,(state.hi+state.lo)*.5,width,length);
   fit(crest,x,.053,state.hi-Math.min(length,.12)*.5,width,Math.min(length,.12));
   for(let j=0;j<ripples.length;j++){
    const n=(j+1)/6,r=ripples[j];
    fit(r,x+Math.sin(n*21+state.lo*1.3)*width*.115,.053,state.lo+length*n,width*(.72-.16*n),.04+.03*n);
    r.material.opacity=.12+.18*n;
   }
  }
 };
}
