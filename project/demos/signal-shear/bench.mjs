import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const view=document.querySelector('#view'),status=document.querySelector('#state'),controls=document.querySelector('#controls');
const clips=['Signal_Release','Arc_Cut'];
try{
 const gl=new T.WebGLRenderer({antialias:true,alpha:false,powerPreference:'low-power'});
 gl.setPixelRatio(Math.min(devicePixelRatio,1.65));
 gl.toneMapping=T.ACESFilmicToneMapping;
 gl.toneMappingExposure=1.16;
 gl.setClearColor(0x142126);
 const scene=new T.Scene(), camera=new T.PerspectiveCamera(36,1,.02,25);
 const env=new RoomEnvironment(), pmrem=new T.PMREMGenerator(gl);
 scene.environment=pmrem.fromScene(env,.055).texture;
 scene.environmentIntensity=.9; env.dispose();pmrem.dispose();
 const light=(color,power,x,y,z)=>{
  const l=new T.DirectionalLight(color,power); l.position.set(x,y,z);scene.add(l);
 };
 light(0x9bd5ed,2.7,-3,3,4);light(0xffb06b,1.85,4,1,-3);
 const root=new T.Group();root.rotation.x=Math.PI/2;scene.add(root);
 const model=await new GLTFLoader().loadAsync(new URL('signal-shear.glb',location.href).href);
 root.add(model.scene);
 const mixer=new T.AnimationMixer(model.scene);
 const actions=Object.fromEntries(model.animations.map(c=>[c.name,mixer.clipAction(c)]));
 if(!clips.every(c=>actions[c]))throw Error('Missing animation');
 const aim=new T.Vector3(0,.74,0), tip=new T.Vector3();
 const tipSocket=model.scene.getObjectByName('tip_socket');
 if(!tipSocket)throw Error('Missing tip socket');
 let theta=.32,phi=.12,drag=null,active=null;
 function cameraPose(){
  const r=camera.aspect<.74?3.85:3.38;
  tipSocket.getWorldPosition(tip);
  aim.copy(tip.multiplyScalar(.43));
  camera.position.set(aim.x+r*Math.cos(phi)*Math.sin(theta),aim.y+r*Math.sin(phi),aim.z+r*Math.cos(phi)*Math.cos(theta));
  camera.lookAt(aim);camera.rotateZ(-.29);
 }
 function resize(){
  const {clientWidth:w,clientHeight:h}=view;if(!w||!h)return;
  camera.aspect=w/h;camera.updateProjectionMatrix();gl.setSize(w,h,false);cameraPose();
 }
 function reset(){
  mixer.stopAllAction();active=null;theta=.32;phi=.12;cameraPose();
  controls.querySelectorAll('[aria-pressed]').forEach(b=>b.setAttribute('aria-pressed','false'));
  status.textContent='Drag to rotate. Choose a clip to play it once.';
 }
 function play(name){
  mixer.stopAllAction();active=actions[name].reset().setLoop(T.LoopOnce,1);active.clampWhenFinished=false;active.play();
  controls.querySelectorAll('[aria-pressed]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.action===name)));
  status.textContent=name==='Arc_Cut'?'Playing the weapon-only arc cut.':'Playing the hinged-gate release.';
 }
 mixer.addEventListener('finished',()=>{
  active=null;controls.querySelectorAll('[aria-pressed]').forEach(b=>b.setAttribute('aria-pressed','false'));
  status.textContent='Clip complete. Drag to inspect or replay.';
 });
 controls.addEventListener('click',e=>{const a=e.target.closest('button')?.dataset.action;if(a==='reset')reset();else if(actions[a])play(a);});
 const canvas=gl.domElement;
 canvas.setAttribute('aria-label','Rotatable 3D weapon');canvas.tabIndex=0;
 canvas.addEventListener('pointerdown',e=>{drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{
  if(!drag||e.pointerId!==drag.id)return;
  theta-=(e.clientX-drag.x)*.008;phi=Math.max(-.9,Math.min(1.1,phi+(e.clientY-drag.y)*.006));
  drag={id:e.pointerId,x:e.clientX,y:e.clientY};cameraPose();
 });
 canvas.addEventListener('lostpointercapture',()=>{drag=null;});
 canvas.addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){theta+=e.key==='ArrowLeft'?-.13:.13;cameraPose();e.preventDefault();}
 });
 view.append(canvas);view.append(view.querySelector('.view-label'));
 document.querySelector('#poster').hidden=true;controls.hidden=false;resize();reset();
 new ResizeObserver(resize).observe(view);
 let last=0;gl.setAnimationLoop(t=>{if(last&&active){mixer.update(Math.min((t-last)*.001,.06));cameraPose();}last=t;gl.render(scene,camera);});
 document.documentElement.dataset.bench='ready';
}catch(error){
 document.documentElement.dataset.bench='fallback';
 status.textContent='3D unavailable on this device. The finished render and GLB download are still available.';
 console.error(error);
}
