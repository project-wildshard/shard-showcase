import * as THREE from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {canvasRenderer} from './canvas_fallback.mjs'
import {ARENA,VIEW_FOV,VIEW_PITCH,MITE_TIMING,SWORD_SWING,cameraPose,clamp,createGame,step} from './combat.mjs'
import {CRATES,DOCK,GANTRY,GANTRY_FALLBACK_OMIT,GANTRY_PLAQUE,STACK} from './yard-layout.mjs'
import {createTouchLook} from './touch-look.mjs'
import {CONCRETE_SIZE,CONCRETE_METERS,concretePixels} from './concrete-surface.mjs'
import {createRearCladding} from './yard-cladding.mjs'
import {YARD_SUN,shadowDelta,shadowFootprint} from './yard-light.mjs'
import {createApron} from './yard-apron.mjs'
import {createViewmodel,poseViewmodel} from './viewmodel.mjs'
const el=q=>document.querySelector(q)
let view=el('#view')
const status=el('#status'), enter=el('#enter'), reticle=el('#reticle')
const touchLook=createTouchLook()
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
const camera=new THREE.PerspectiveCamera(VIEW_FOV,1,.04,55);camera.rotation.order='YXZ';scene.add(camera)
scene.add(new THREE.HemisphereLight(0xc8efff,0x91745e,2.3))
const sun=new THREE.DirectionalLight(0xffd1a0,2.7);sun.position.set(...YARD_SUN);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-14,right:14,top:16,bottom:-16,near:.1,far:45});sun.shadow.bias=-.001;scene.add(sun)
const mat=(color,roughness=.68,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness})
const iron=mat(0x2a3d40,.56,.39),paint=mat(0x9e4a21,.62,.25),steel=mat(0xa0b2ad,.36,.65),sunwood=mat(0xa06938),leather=mat(0x39291d),warm=mat(0xe19a3b),pad=mat(0x42585a)
function box(parent,m,w,h,d,x,y,z){
 const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o
}
const concrete=renderer.isWebGLRenderer?new THREE.DataTexture(concretePixels(),CONCRETE_SIZE,CONCRETE_SIZE):null
if(concrete){
 concrete.colorSpace=THREE.SRGBColorSpace
 concrete.wrapS=concrete.wrapT=THREE.RepeatWrapping
 concrete.generateMipmaps=true;concrete.minFilter=THREE.LinearMipmapLinearFilter;concrete.magFilter=THREE.LinearFilter
 concrete.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());concrete.needsUpdate=true
}
const apronGroups=new Map()
for(const patch of createApron()){
 const key=patch.style+':'+patch.color+':'+patch.y
 let batch=apronGroups.get(key)
 if(!batch){batch={patch,positions:[]};apronGroups.set(key,batch)}
 const [a,...rest]=patch.points
 for(let i=0;i<rest.length-1;i++){
  // Reverse X/Z winding to face upward in Three's Y-up scene.
  for(const [x,z] of [a,rest[i+1],rest[i]])batch.positions.push(x,patch.y,z)
 }
}
for(const {patch,positions} of apronGroups.values()){
 const g=new THREE.BufferGeometry()
 g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3))
 g.computeVertexNormals()
 const isMetal=patch.style==='metal'
 const m=new THREE.Mesh(g,mat(patch.color,isMetal?.48:.79,isMetal?.46:0))
 if(concrete&&patch.style==='slab'){
  const uv=[]
  for(let i=0;i<positions.length;i+=3)uv.push(positions[i]/CONCRETE_METERS,positions[i+2]/CONCRETE_METERS)
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));m.material.map=concrete
 }
 m.receiveShadow=true;m.userData.paintLayer=patch.y
 scene.add(m)
}
// Short wall panels prevent a near end of a long triangle from sorting
// in front of unrelated props in the software renderer.
for(const x of [-9,9])for(let i=0;i<10;i++)box(scene,iron,.27,2.65,2.2,x,1.32,-9.9+i*2.2)
for(let i=0;i<9;i++){box(scene,iron,2,2.65,.26,-8+i*2,1.32,11);box(scene,iron,2,2.65,.24,-8+i*2,1.32,-11.064)}
for(let i=-8;i<=8;i+=2){for(const x of [i])for(const z of [-10.85,10.85])box(scene,paint,.19,3.02,.29,x,1.51,z)}
const cladding=new THREE.BufferGeometry(),cladPos=[],cladColor=[],tone=new THREE.Color()
for(const {points,top,bottom} of createRearCladding()){
 for(const i of [0,1,2,0,2,3]){
  cladPos.push(...points[i]);tone.setHex(i<2?bottom:top);cladColor.push(tone.r,tone.g,tone.b)
 }
}
cladding.setAttribute('position',new THREE.Float32BufferAttribute(cladPos,3))
cladding.setAttribute('color',new THREE.Float32BufferAttribute(cladColor,3))
cladding.computeVertexNormals()
const wallMaterial=mat(0xffffff,.62,.31);wallMaterial.vertexColors=true
const rear=new THREE.Mesh(cladding,wallMaterial);rear.receiveShadow=true;rear.userData.verticalTint=true;scene.add(rear)
const curb=mat(0x646d63,.89),flashing=mat(0x56635c,.63,.38)
for(let x=-8;x<=8;x+=2){
 box(scene,curb,1.975,.22,.25,x,.11,-10.76)
 box(scene,flashing,1.965,.105,.22,x,2.62,-10.79)
}
const loadYard=new GLTFLoader()
function mountGantryPlaque(prop){
 let stencil
 prop.traverse(o=>{if(o.isMesh&&o.material?.name==='Ivory stenciling')stencil=o})
 if(!stencil)throw new Error('Yard 01 gantry stencil missing')
 const {height,front,width,faceHeight,glyphScale}=GANTRY_PLAQUE
 const frame=mat(0x6c7b75,.51,.49),panel=mat(0x27363a,.65,.20),hanger=mat(0x455150,.72,.39)
 for(const y of [-1,1])box(prop,frame,width,.039,.042,0,height+y*(faceHeight-.039)/2,front-.027)
 for(const x of [-1,1])box(prop,frame,.041,faceHeight-.078,.042,x*(width-.041)/2,height,front-.027)
 const face=new THREE.Mesh(new THREE.PlaneGeometry(width-.075,faceHeight-.071,6,4),panel)
 face.position.set(0,height,front-.047);face.receiveShadow=true;prop.add(face)
 box(prop,hanger,width*.94,.115,.226,0,height,front-.142)
 for(const x of [-.755,.755])box(prop,steel,.055,.034,.027,x,height,front+.005)
 stencil.scale.set(glyphScale,glyphScale,1)
 stencil.position.set(.025,height-3.97679687*glyphScale,front+.027-.261)
}
function stageProp(url,placements,omit=[],dress){

 return loadYard.loadAsync(url).then(({scene:prop})=>{
  prop.traverse(o=>{
   if(!o.isMesh)return
   o.castShadow=true;o.receiveShadow=true
   if(!renderer.isWebGLRenderer&&omit.includes(o.material?.name))o.visible=false
  })
  if(dress)dress(prop)
  for(const p of placements){const copy=prop.clone();copy.position.set(...p);scene.add(copy)}
 })
}
const dressing=Promise.all([
 stageProp('./assets/dock.glb',[[DOCK.x,0,DOCK.z]]),
 stageProp('./assets/haul-crate.glb',CRATES),
 stageProp('./assets/gantry.glb',[[GANTRY.x,0,GANTRY.z]],GANTRY_FALLBACK_OMIT,mountGantryPlaque),
]).then(()=>true,e=>{console.error(e);return false})
// Base plate keeps the authored stack aligned to its existing cover volume.
box(scene,iron,STACK.width,.065,STACK.depth,STACK.x,.033,STACK.z)
for(const [x,z,w,d] of ARENA.blocks){
 if(x===STACK.x&&z===STACK.z)continue
 box(scene,sunwood,w,1.47,d,x,.735,z)
 for(const dx of [-.4,.4])box(scene,iron,.102,1.55,d+.055,x+w*dx,.776,z)
}
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
// Layered contact occlusion for the software renderer only. WebGL has
// the actual sun shadow map, so don't darken it a second time.
function footShadow(x,z,radiusX,radiusZ){
 const g=new THREE.Group();scene.add(g);g.position.set(x,.007,z)
 for(const [scale,opacity] of [[1.16,.105],[.87,.15],[.57,.105]]){
  const o=new THREE.Mesh(new THREE.CircleGeometry(1,14),
   new THREE.MeshBasicMaterial({color:0x201f1b,transparent:true,opacity}))
  o.rotation.x=-Math.PI/2;o.scale.set(radiusX*scale,radiusZ*scale,1)
  o.userData.paintLayer=.006+(1.16-scale)*.0001
  g.add(o)
 }
 return g
}
// These two thin layers are a directional extension, not a second light
// pass. Keep their world bearing fixed when the Mite turns. The real WebGL
// shadow map needs neither these approximations nor the contact decals.
function directionalShadow(x,z,height,radius){
 const g=new THREE.Group(),points=shadowFootprint(height,radius),positions=[]
 const [dx,dz]=shadowDelta(height),ang=Math.atan2(dz,dx),c=Math.cos(ang),s=Math.sin(ang)
 for(let i=1;i<points.length-1;i++)
  for(const [u,v] of [points[0],points[i+1],points[i]])positions.push(u*c-v*s,0,u*s+v*c)
 const geom=new THREE.BufferGeometry()
 geom.setAttribute('position',new THREE.Float32BufferAttribute(positions,3))
 for(const [scale,opacity] of [[1.12,.11],[1,.17]]){
  const o=new THREE.Mesh(geom,new THREE.MeshBasicMaterial({color:0x252d35,transparent:true,opacity}))
  o.scale.set(scale,1,scale);o.userData.paintLayer=.0058+(1.12-scale)*.0001
  o.userData.baseOpacity=opacity;g.add(o)
 }
 g.position.set(x,.007,z);scene.add(g);return g
}
let miteShadow,miteCast
if(!renderer.isWebGLRenderer){
 miteShadow=footShadow(0,0,.43,.35)
 miteCast=directionalShadow(0,0,.60,.41)
 footShadow(STACK.x-.065,STACK.z+.18,1.62,1.16)
 footShadow(DOCK.x+.09,DOCK.z+.12,1.42,1.39)
 directionalShadow(DOCK.x,DOCK.z,.63,1.24)
 for(const x of [-2.92,2.92])footShadow(x+.08,GANTRY.z+.15,.75,.68)
}
// The cue is anchored to the locked attack heading, not to the moving camera.
const tell=new THREE.Group();scene.add(tell);tell.visible=false
const tellMat=mat(0x55d9d5,.55);tellMat.emissive.setHex(0x18b9bf)
for(const x of [-.62,.62])for(const z of [.56,1.40,2.24]){
 const stripe=box(tell,tellMat,.048,.007,.61,x,.009,z)
 stripe.castShadow=false;stripe.userData.paintLayer=.009
}
const sparks=new THREE.Group();scene.add(sparks);sparks.visible=false
const sparkMat=mat(0xffa94e,.45);sparkMat.emissive.setHex(0xff8e2c)
for(let i=0;i<8;i++){
 const chip=box(sparks,sparkMat,.016,.016,.13,0,0,0)
 chip.castShadow=false
}
let game=createGame(),yaw=0,pitch=VIEW_PITCH,active=false,model,mix,action,eyeMat,oldPhase='',hurt=0,hit=0,keys=new Set(),swing=false,dodge=false,last=performance.now(),stickId,stickX=0,stickY=0,carry=0
const dodgeButton=el('#dodge')
const stick=el('#stick'),thumb=el('#stick-thumb')
function stopStick(){stickId=undefined;stickX=stickY=0;thumb.style.transform=''}
const clips=new Map()
const opts={idle:['idle',true],sleep:['sleep',true],wake:['wake',false],turn:['turn',true],chase:['run',true],hit:['hit',false],die:['die',false]}
const setClip=(name,loop)=>{
 if(action?.getClip().name===name)return
 const clip=clips.get(name);if(!clip)return
 const next=mix.clipAction(clip).reset();next.setLoop(loop?THREE.LoopRepeat:THREE.LoopOnce,loop?Infinity:1);next.clampWhenFinished=!loop
 if(action)next.crossFadeFrom(action,name==='hit'?.035:.10,false);next.play();action=next
}
function reset(){
 game=createGame();yaw=0;pitch=VIEW_PITCH;oldPhase='';hurt=0;hit=0;swing=false;dodge=false;carry=0;stopStick();tell.visible=sparks.visible=false
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
 const k=e.key.toLowerCase();if(['w','a','s','d','shift',' ','q','r'].includes(k)){e.preventDefault();keys.add(k)}
 if(k==='r'&&!e.repeat)reset();if(k===' ')swing=true;if(k==='q'&&!e.repeat)dodge=true
})
document.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()))
window.addEventListener('blur',()=>{keys.clear();stopStick();touchLook.clear()})
document.addEventListener('mousemove',e=>{
 if(document.pointerLockElement===view){yaw+=e.movementX*.0026;pitch=clamp(pitch-e.movementY*.0023,-1.10,1.10)}
})
view.addEventListener('pointerdown',e=>{
 if(!active)return
 if(e.pointerType==='touch'){if(touchLook.begin(e))view.setPointerCapture(e.pointerId)}
 else if(document.pointerLockElement!==view)view.requestPointerLock?.()?.catch?.(()=>{})
 else swing=true
})
view.addEventListener('pointermove',e=>{
 const delta=touchLook.move(e)
 if(!delta)return
 yaw+=delta[0]*.006;pitch=clamp(pitch-delta[1]*.005,-1.1,1.1)
})
for(const x of ['pointerup','pointercancel','lostpointercapture'])view.addEventListener(x,e=>touchLook.end(e))
function aimStick(e){
 const r=stick.getBoundingClientRect()
 const x=(e.clientX-r.x-r.width/2)/34,y=(e.clientY-r.y-r.height/2)/34,n=Math.max(1,Math.hypot(x,y))
 stickX=x/n;stickY=-y/n
 thumb.style.transform=`translate(${stickX*29}px,${-stickY*29}px)`
}
stick.addEventListener('pointerdown',e=>{
 if(!active||stickId!==undefined)return
 stickId=e.pointerId;stick.setPointerCapture(stickId);aimStick(e)
})
stick.addEventListener('pointermove',e=>{if(e.pointerId===stickId)aimStick(e)})
for(const type of ['pointerup','pointercancel','lostpointercapture'])
 stick.addEventListener(type,e=>{if(e.pointerId===stickId)stopStick()})
el('#attack').onpointerdown=()=>{swing=true}
dodgeButton.onpointerdown=()=>{dodge=true}
function frame(now){
 requestAnimationFrame(frame);const dt=Math.min(.10,(now-last)/1000);last=now
 const w=view.clientWidth,h=view.clientHeight
 if(w&&h&&(view.width!==Math.floor(w*renderer.getPixelRatio())||view.height!==Math.floor(h*renderer.getPixelRatio()))){renderer.setSize(w,h,false)}
 if(w&&h&&camera.aspect!==w/h){camera.aspect=w/h;camera.updateProjectionMatrix()}
 if(active&&model){
  const before=game.player.hp,priorMiteHp=game.mite.hp
  const forward=clamp(Number(keys.has('w'))-Number(keys.has('s'))+stickY,-1,1)
  const strafe=clamp(Number(keys.has('d'))-Number(keys.has('a'))+stickX,-1,1)
  carry+=dt
  let advanced=0
  while(carry>=1/60){
   step(game,{yaw,pitch,aspect:camera.aspect,forward,strafe,sprint:keys.has('shift'),attack:swing||keys.has(' '),dodge},1/60)
   carry-=1/60;advanced+=1/60;swing=dodge=false
  }
  const p=game.player,m=game.mite
  const pose=cameraPose(p)
  camera.position.set(p.x,pose.height,p.z);camera.rotation.set(pose.pitch,-p.yaw,pose.roll,'YXZ')
  model.position.set(m.x,0,m.z);model.rotation.y=m.yaw
  if(miteShadow){
   miteShadow.position.set(m.x+.05,.007,m.z+.06)
   miteShadow.scale.setScalar(m.phase==='die'?1.24:m.phase==='lunge'?.91:1)
   miteShadow.rotation.y=m.yaw
   miteCast.position.set(m.x,.007,m.z)
   // Breakup settles on the slabs rather than keeping a tall silhouette.
   miteCast.scale.setScalar(m.phase==='die'?.69:m.phase==='lunge'?.94:1)
   const margin=Math.min(ARENA.width/2-Math.abs(m.x),ARENA.depth/2-Math.abs(m.z))
   const fade=clamp((margin-.48)/.38,0,1)*(m.phase==='die'?.46:1)
   for(const layer of miteCast.children)layer.material.opacity=layer.userData.baseOpacity*fade
  }
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
  const moving=Math.abs(forward)+Math.abs(strafe)>.15
  poseViewmodel(handRig,elapsed,game.time,moving,camera.aspect)
  if(eyeMat)eyeMat.emissiveIntensity=m.phase==='sleep'||m.phase==='die'?0:m.phase==='recover'?.38:m.phase==='windup'?(m.special?3.3:2.8)+.7*Math.sin(m.t*33):1.45
  mix.update(advanced)
  tell.visible=m.phase==='windup'
  if(tell.visible){
   tell.position.set(m.x,0,m.z)
   tell.rotation.y=Math.atan2(m.goalX,m.goalZ)
   tell.scale.z=m.special?1.20:1
   tellMat.emissiveIntensity=.34+.44*Math.pow(Math.min(1,m.t/(m.special?MITE_TIMING.overclock.tell:MITE_TIMING.bite.tell)),2)
  }
  if(before!==p.hp)hurt=.72
  if(priorMiteHp>m.hp){
   hit=.19
   const toward=new THREE.Vector2(p.x-m.x,p.z-m.z).normalize()
   sparks.position.set(m.x+toward.x*.23,.44,m.z+toward.y*.23)
  }else hit=Math.max(0,hit-dt)
  sparks.visible=hit>0
  if(sparks.visible){
   const age=.19-hit
   sparkMat.emissiveIntensity=2.1*(hit/.19)
   sparks.children.forEach((o,i)=>{
    const heading=.47+i*(Math.PI*2/8)
    o.position.set(Math.cos(heading)*age*2.2,age*(1.1+i%3*.6)-2.7*age*age,Math.sin(heading)*age*2.2)
    o.rotation.set(.4+i*.51,heading,heading*.77)
    o.scale.z=.2+.8*hit/.19
   })
   handRig.rotation.x-=Math.sin(Math.PI*hit/.19)*.055
  }
  dodgeButton.classList.toggle('cooldown',p.dodgeCooldown>0)
  const mark=hit>0?'×':'+'
  if(reticle.textContent!==mark)reticle.textContent=mark
  reticle.classList.toggle('hit',hit>0)
  hurt=Math.max(0,hurt-2.1*dt);el('#vignette').style.opacity=hurt
  const label='HP '+p.hp+' · MITE '+m.hp+' · SERVO '+game.servos
  if(el('#life').textContent!==label)el('#life').textContent=label
  if(status.textContent!==game.notice)status.textContent=game.notice
 }else if(model){
  camera.position.set(0,1.68,6.7);camera.rotation.x=-.20;model.position.set(game.mite.x,0,game.mite.z)
  if(miteShadow){miteShadow.position.set(game.mite.x+.05,.007,game.mite.z+.06);miteCast.position.set(game.mite.x,.007,game.mite.z)}
  setClip('sleep',true);mix.update(dt)
 }
 renderer.render(scene,camera)
}
requestAnimationFrame(frame)
