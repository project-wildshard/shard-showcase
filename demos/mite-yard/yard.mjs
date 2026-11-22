import * as THREE from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {canvasRenderer} from './canvas_fallback.mjs'
import {ARENA,clamp,createGame,step} from './combat.mjs'
const el=q=>document.querySelector(q)
let view=el('#view')
const status=el('#status'), enter=el('#enter')
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
const cement=mat(0xa59470),iron=mat(0x2a3d40,.56,.39),paint=mat(0x9e4a21,.62,.25),steel=mat(0xa0b2ad,.36,.65),sunwood=mat(0xa06938),leather=mat(0x39291d),skin=mat(0xa76e50),warm=mat(0xe19a3b),pad=mat(0x42585a)
function box(parent,m,w,h,d,x,y,z){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o
}
box(scene,cement,18,.22,22,0,-.11,0).userData.paintBackground=true
for(const x of [-9,9])box(scene,iron,.27,2.65,22,x,1.32,0)
for(const z of [-11,11])box(scene,iron,18,2.65,.26,0,1.32,z)
for(let i=-8;i<=8;i+=2){for(const x of [i])for(const z of [-10.85,10.85])box(scene,paint,.19,3.02,.29,x,1.51,z)}
for(const [x,z,w,d] of ARENA.blocks){
 box(scene,sunwood,w,1.47,d,x,.735,z)
 for(const dx of [-.4,.4])box(scene,iron,.102,1.55,d+.055,x+w*dx,.776,z)
}
for(let z=-8;z<9;z+=1.5)for(const x of [-2.9,2.9])box(scene,warm,.065,.006,.78,x,.004,z)
box(scene,pad,1.3,.10,.56,1.9,.049,-6.8)
const handRig=new THREE.Group();camera.add(handRig);handRig.position.set(.34,-.33,-.56)
const limb=new THREE.Mesh(new THREE.CapsuleGeometry(.065,.25,3,7),leather);limb.rotation.x=-.83;limb.position.set(.068,-.132,.16);handRig.add(limb)
const palm=new THREE.Mesh(new THREE.CapsuleGeometry(.053,.048,3,7),skin);palm.rotation.z=.34;palm.position.set(0,-.017,.014);handRig.add(palm)
for(let i=0;i<4;i++)box(handRig,leather,.087,.014,.061,0,-.064+i*.024,-.017)
box(handRig,leather,.044,.19,.045,-.025,.012,-.027)
box(handRig,warm,.197,.035,.057,-.022,.124,-.027)
const blade=new THREE.Shape();blade.moveTo(-.053,0);blade.lineTo(-.044,.36);blade.lineTo(0,.49);blade.lineTo(.05,.363);blade.lineTo(.06,0);blade.closePath()
const sword=new THREE.Mesh(new THREE.ExtrudeGeometry(blade,{depth:.022,steps:1,bevelEnabled:true,bevelSegments:1,bevelSize:.006,bevelThickness:.005}),steel)
sword.position.set(-.025,.145,-.043);handRig.add(sword)
let game=createGame(),yaw=0,pitch=-.30,active=false,model,mix,action,eyeMat,oldPhase='',hurt=0,keys=new Set(),swing=false,last=performance.now(),touchDrag
const clips=new Map()
const opts={idle:['idle',true],sleep:['sleep',true],wake:['wake',false],turn:['turn',true],chase:['run',true],hit:['hit',false],die:['die',false]}
const setClip=(name,loop)=>{
 if(action?.getClip().name===name)return
 const clip=clips.get(name);if(!clip)return
 const next=mix.clipAction(clip).reset();next.setLoop(loop?THREE.LoopRepeat:THREE.LoopOnce,loop?Infinity:1);next.clampWhenFinished=!loop
 if(action)next.crossFadeFrom(action,.10,false);next.play();action=next
}
function reset(){
 game=createGame();yaw=0;pitch=-.30;oldPhase='';hurt=0;swing=false
 mix?.stopAllAction();action=undefined
}
enter.disabled=true
new GLTFLoader().load('./assets/mite.glb',g=>{
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
  const before=game.player.hp
  step(game,{yaw,pitch,forward:Number(keys.has('w'))-Number(keys.has('s')),strafe:Number(keys.has('d'))-Number(keys.has('a')),sprint:keys.has('shift'),attack:swing||keys.has(" ")},dt);swing=false
  const p=game.player,m=game.mite
  camera.position.set(p.x,1.68,p.z);camera.rotation.set(p.pitch,-p.yaw,0,'YXZ')
  model.position.set(m.x,0,m.z);model.rotation.y=m.yaw
  if(m.phase!==oldPhase){
   if(m.phase==='windup')setClip(m.special?'attack.overclock':'attack.bite',false)
   else if(m.phase!=='lunge')setClip(...(opts[m.phase]||opts.idle))
   oldPhase=m.phase
  }
  const u=clamp(p.swingTime/.48,0,1),n=p.swing?Math.sin(Math.PI*u):0
  handRig.rotation.set(.10+n*.75,-.19-n*.86,-.30+n*1.32)
  handRig.position.set(.36-n*.40,-.36+Math.sin(game.time*5)*.004, -.63-n*.09)
  if(eyeMat)eyeMat.emissiveIntensity=m.phase==='sleep'||m.phase==='die'?0:m.phase==='windup'?(m.special?3.3:2.8)+.7*Math.sin(m.t*33):1.45
  mix.update(dt)
  if(before!==p.hp)hurt=.72
  hurt=Math.max(0,hurt-2.1*dt);el('#vignette').style.opacity=hurt
  el('#life').textContent='HEALTH '+p.hp+' · MITE '+m.hp;status.textContent=game.notice
 }else if(model){
  camera.position.set(0,1.68,6.7);camera.rotation.x=-.20;model.position.set(game.mite.x,0,game.mite.z)
  setClip('sleep',true);mix.update(dt)
 }
 renderer.render(scene,camera)
}
requestAnimationFrame(frame)
