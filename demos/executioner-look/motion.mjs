import * as T from 'three';

export function setupGuardStudy(gltf,stage,render) {
 const clip=gltf.animations.find(a=>a.name==='Executioner Guard Study');
 if(!clip||gltf.animations.length!==1)throw Error('Wrong guard study motion.');
 const skinned=[];
 gltf.scene.traverse(o=>{if(o.isSkinnedMesh)skinned.push(o);});
 if(skinned.length!==7)throw Error('Expected seven skinned garment meshes.');
 const wrap=skinned.find(o=>o.name.includes('fireproof_cloth'));
 if(!wrap)throw Error('Weighted mantle missing.');
 const joints=wrap.geometry.attributes.skinIndex, weights=wrap.geometry.attributes.skinWeight;
 const shoulder=wrap.skeleton.bones.findIndex(x=>x.name.replace('.','')==='upper_armL');
 if(shoulder<0)throw Error('Left shoulder joint missing.');
 const indices=[];
 for(let i=0;i<joints.count;i++)for(let k=0;k<4;k++){
  if(joints.getComponent(i,k)===shoulder&&weights.getComponent(i,k)>.8){indices.push(i);break;}
 }
 if(!indices.length)throw Error('No weighted mantle probes.');
 const selection=indices.filter((_,i)=>i%Math.max(1,Math.floor(indices.length/12))===0).slice(0,16);
 const mixer=new T.AnimationMixer(gltf.scene);
 const action=mixer.clipAction(clip);action.setLoop(T.LoopOnce,1);action.clampWhenFinished=true;
 const play=document.querySelector('#guard-play'),slider=document.querySelector('#guard-frame'),panel=document.querySelector('#guard-panel');
 panel.hidden=false;
 const vec=new T.Vector3(),baseline=[];
 function position(i){wrap.getVertexPosition(i,vec);return vec.applyMatrix4(wrap.matrixWorld);}
 let serial=0;
 function seek(v) {
  action.reset().play();mixer.setTime(clip.duration*v);gltf.scene.updateMatrixWorld(true);
  if(!baseline.length)for(const i of selection)baseline.push(position(i).clone());
  let max=0;selection.forEach((i,j)=>{max=Math.max(max,position(i).distanceTo(baseline[j]));});
  slider.value=String(Math.round(v*100));
  stage.dataset.motionProgress=v.toFixed(3);stage.dataset.clothTravel=max.toFixed(5);
  render();
 }
 slider.addEventListener('input',()=>{serial++;seek(+slider.value/100);});
 play.addEventListener('click',()=>{
  const tag=++serial,origin=performance.now();
  function step(now) {
   if(tag!==serial)return;
   const v=Math.min(1,(now-origin)/(clip.duration*1000));
   seek(v);
   if(v<1)requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
 });
 stage.dataset.motion='guard-study';stage.dataset.motionSeconds=clip.duration.toFixed(4);
 stage.dataset.skinnedMeshes=String(skinned.length);
 stage.dataset.probeVertices=String(selection.length);seek(0);
}
