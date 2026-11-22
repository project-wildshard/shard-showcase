import * as THREE from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {canvasRenderer} from './canvas_fallback.mjs'
import {ARENA,SWORD_SWING,clamp,createGame,step} from './combat.mjs'
import {CRATES,DOCK,STACK} from './yard-layout.mjs'
import {createViewmodel,poseViewmodel} from './viewmodel.mjs'
const el=q=>document.querySelector(q)
let view=el('#view')
const status=el('#status'), enter=el('#enter'), reticle=el('#reticle')
const touch=matchMedia('(pointer:coarse)').matches
let renderer
try{renderer=new THREE.WebGLRenderer({canvas:view,antialias:true})}
catch{
 const fresh=view.cloneNode();view.replaceWith(fresh);view=fresh
 renderer=canvasRenderer(view)
}

renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.shadowMap.enabled=true
renderer.shadowMap.type=THREE.PCFShadowMap
const scene=new THREE.Scene();scene.background=new THREE.Color(0x8cb8c3);scene.fog=new THREE.Fog(0x8cb8c3,23,48)
const camera=new THREE.PerspectiveCamera(65,1,.04,55);camera.rotation.order='YXZ';scene.add(camera)
scene.add(new THREE.HemisphereLight(0xc8efff,0x91745e,2.3))
const sun=new THREE.DirectionalLight(0xffd1a0,2.7);sun.position.set(-8,14,8);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-14,right:14,top:16,bottom:-16,near:.1,far:45});sun.shadow.bias=-.001;scene.add(sun)
const mat=(color,roughness=.68,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness})
const cement=mat(0xa59470),iron=mat(0x2a3d40,.56,.39),paint=mat(0x9e4a21,.62,.25),steel=mat(0xa0b2ad,.36,.65),sunwood=mat(0xa06938),leather=mat(0x39291d),warm=mat(0xe19a3b),pad=mat(0x42585a)
function box(parent,m,w,h,d,x,y,z){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o
}
box(scene,cement,18,.22,22,0,-.11,0).userData.paintBackground=true
for(const x of [-9,9])box(scene,iron,.27,2.65,22,x,1.32,0)
for(const z of [-11,11])box(scene,iron,18,2.65,.26,0,1.32,z)
for(let i=-8;i<=8;i+=2){for(const x of [i])for(const z of [-10.85,10.85])box(scene,paint,.19,3.02,.29,x,1.51,z)}
for(let x=-8.75;x<9;x+=.36)box(scene,iron,.10,2.3,.105,x,1.48,-10.82)
box(scene,paint,9,.12,.13,4.4,2.35,-10.67)
box(scene,steel,9,.12,.13,4.4,.29,-10.67)
const loadYard=new GLTFLoader()
function stageProp(url,placements){
 return loadYard.loadAsync(url).then(({scene:prop})=>{
  prop.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}})
  for(const p of placements){const copy=prop.clone();copy.position.set(...p);scene.add(copy)}
 })
}
const dressing=Promise.all([
 stageProp('./assets/dock.glb',[[DOCK.x,0,DOCK.z]]),
 stageProp('./assets/haul-crate.glb',CRATES),
]).then(()=>true,e=>{console.error(e);return false})
// Base plate keeps the authored stack aligned to its existing cover volume.
box(scene,iron,STACK.width,.065,STACK.depth,STACK.x,.033,STACK.z)
for(const [x,z,w,d] of ARENA.blocks){
 if(x===STACK.x&&z===STACK.z)continue
 box(scene,sunwood,w,1.47,d,x,.735,z)
 for(const dx of [-.4,.4])box(scene,iron,.102,1.55,d+.055,x+w*dx,.776,z)
}
for(let z=-8;z<9;z+=1.5)for(const x of [-2.9,2.9])box(scene,warm,.065,.006,.78,x,.004,z)
box(scene,pad,2.75,.018,2.9,DOCK.x,.009,DOCK.z)
for(const z of [DOCK.z-1.35,DOCK.z+1.35]){
 for(let i=0;i<9;i++){
  const stripe=box(scene,i%2?iron:warm,.245,.009,.14,DOCK.x+(i-4)*.272,.021,z)
  stripe.rotation.y=.38
 }
}
const handRig=createViewmodel();camera.add(handRig);poseViewmodel(handRig,0)
// Mechanical pickup, with editable geometry and no binary texture dependency.
const servo=new THREE.Group();scene.add(servo);servo.visible=false
const copper=mat(0xc67a35,.44,.52),servoLens=mat(0x46cdd2,.29,.28)
servoLens.emissive.setHex(0x15bfc7);servoLens.emissiveIntensity=1.7
function servoRing(r,h,y,material){
 const o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,10),material)
 o.position.y=y;o.castShadow=true;servo.add(o)
}
servoRing(.092,.23,0,iron)
for(const y of [-.105,.105])servoRing(.132,.041,y,steel)
for(const y of [-.067,-.034,0,.034,.067])servoRing(.107,.019,y,copper)
servoRing(.068,.018,.135,servoLens)
box(servo,leather,.077,.085,.112,.12,-.016,0)
let game=createGame(),yaw=0,pitch=-.30,active=false,model,mix,action,eyeMat,oldPhase='',hurt=0,hit=0,keys=new Set(),swing=false,last=performance.now(),touchDrag
const clips=new Map()
const opts={idle:['idle',true],sleep:['sleep',true],wake:['wake',false],turn:['turn',true],chase:['run',true],hit:['hit',false],die:['die',false]}
const setClip=(name,loop)=>{
 if(action?.getClip().name===name)return
 const clip=clips.get(name);if(!clip)return
 const next=mix.clipAction(clip).reset();next.setLoop(loop?THREE.LoopRepeat:THREE.LoopOnce,loop?Infinity:1);next.clampWhenFinished=!loop
 if(action)next.crossFadeFrom(action,.10,false);next.play();action=next
}
function reset(){
 game=createGame();yaw=0;pitch=-.30;oldPhase='';hurt=0;hit=0;swing=false
 mix?.stopAllAction();action=undefined;servo.visible=false
}
enter.disabled=true
new GLTFLoader().load('./assets/mite.glb',async g=>{
 if(!await dressing){status.textContent='Could not load the E01 dock court.';enter.textContent='Assets unavailable';return}
 model=g.scene;scene.add(model);mix=new THREE.AnimationMixer(model)
 g.animations.forEach(a=>clips.set(a.name,a))
 model.traverse(o=>{
  if(!o.isMesh)return
  o.castShadow=true;o.receiveShadow=true
  if(o.material.emissive?.g>.65){o.material=o.material.clone();eyeMat=o.material}
 })
 enter.disabled=false;status.textContent='Ready.'
},undefined,e=>{status.textContent='Could not load Crate Mite rig.';enter.textContent='Asset unavailable';console.error(e)})
function begin(){
 if(!model)return
 active=true;el('#start').hidden=true
 if(!touch)view.requestPointerLock?.()?.catch?.(()=>{})
}
enter.onclick=begin
el('#reset').onclick=reset
document.addEventListener('keydown',e=>{
 const k=e.key.toLowerCase();if(['w','a','s','d','shift',' ','r'].includes(k)){e.preventDefault();keys.add(k)}
 if(k==='r')reset();if(k===' ')swing=true
})
document.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()))
window.addEventListener('blur',()=>keys.clear())
document.addEventListener('mousemove',e=>{
 if(document.pointerLockElement===view){yaw+=e.movementX*.0026;pitch=clamp(pitch-e.movementY*.0023,-1.10,1.10)}
})
view.addEventListener('pointerdown',e=>{
 if(!active)return
 if(e.pointerType==='touch'){touchDrag=[e.clientX,e.clientY];view.setPointerCapture(e.pointerId)}
 else if(document.pointerLockElement!==view)view.requestPointerLock?.()?.catch?.(()=>{})
 else swing=true
})
view.addEventListener('pointermove',e=>{
 if(e.pointerType!=='touch'||!touchDrag)return
 yaw+=(e.clientX-touchDrag[0])*.006;pitch=clamp(pitch-(e.clientY-touchDrag[1])*.005,-1.1,1.1);touchDrag=[e.clientX,e.clientY]
})
for(const x of ['pointerup','pointercancel'])view.addEventListener(x,()=>touchDrag=null)
for(const b of document.querySelectorAll('[data-key]')){
 b.onpointerdown=e=>{b.setPointerCapture(e.pointerId);keys.add(b.dataset.key)}
 for(const x of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(x,()=>keys.delete(b.dataset.key))
}
el('#attack').onpointerdown=()=>{swing=true}
function frame(now){
 requestAnimationFrame(frame);const dt=Math.min(.045,(now-last)/1000);last=now
 const w=view.clientWidth,h=view.clientHeight
 if(w&&h&&(view.width!==Math.floor(w*renderer.getPixelRatio())||view.height!==Math.floor(h*renderer.getPixelRatio()))){renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
 if(active&&model){
  const before=game.player.hp,priorMiteHp=game.mite.hp
  step(game,{yaw,pitch,forward:Number(keys.has('w'))-Number(keys.has('s')),strafe:Number(keys.has('d'))-Number(keys.has('a')),sprint:keys.has('shift'),attack:swing||keys.has(" ")},dt);swing=false
  const p=game.player,m=game.mite
  camera.position.set(p.x,1.68,p.z);camera.rotation.set(p.pitch,-p.yaw,0,'YXZ')
  model.position.set(m.x,0,m.z);model.rotation.y=m.yaw
  const d=game.drop
  servo.visible=Boolean(d&&game.time>=d.readyAt)
  if(servo.visible){
   const lift=Math.sin((game.time-d.readyAt)*3.5)*.035
   servo.position.set(d.x,.28+lift,d.z);servo.rotation.set(.34,game.time*1.4,.17)
  }
  if(m.phase!==oldPhase){
   if(m.phase==='windup')setClip(m.special?'attack.overclock':'attack.bite',false)
   else if(m.phase!=='lunge'&&m.phase!=='recover')setClip(...(opts[m.phase]||opts.idle))
   oldPhase=m.phase
  }
  const elapsed=p.swing?p.swingTime:SWORD_SWING.end
  const moving=['w','a','s','d'].some(key=>keys.has(key))
  poseViewmodel(handRig,elapsed,game.time,moving,camera.aspect)
  if(eyeMat)eyeMat.emissiveIntensity=m.phase==='sleep'||m.phase==='die'?0:m.phase==='recover'?.38:m.phase==='windup'?(m.special?3.3:2.8)+.7*Math.sin(m.t*33):1.45
  mix.update(dt)
  if(before!==p.hp)hurt=.72
  hit=priorMiteHp>m.hp?.18:Math.max(0,hit-dt)
  const mark=hit>0?'×':'+'
  if(reticle.textContent!==mark)reticle.textContent=mark
  reticle.classList.toggle('hit',hit>0)
  hurt=Math.max(0,hurt-2.1*dt);el('#vignette').style.opacity=hurt
  el('#life').textContent='HEALTH '+p.hp+' · MITE '+m.hp+' · SERVO '+game.servos;status.textContent=game.notice
 }else if(model){
  camera.position.set(0,1.68,6.7);camera.rotation.x=-.20;model.position.set(game.mite.x,0,game.mite.z)
  setClip('sleep',true);mix.update(dt)
 }
 renderer.render(scene,camera)
}
requestAnimationFrame(frame)
