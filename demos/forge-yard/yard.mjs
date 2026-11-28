import {SIGNATURE_STRIKES,walkerStrike,walkerStrikePhase} from './walker-strike.mjs';
import {beaconThrustWeight,createThrustAlignment} from './thrust-alignment.mjs';
import {DUEL_CAMERA_AXIS,DUEL_CAMERA_FOV,duelDistance} from './duel-camera.mjs';
import {createImpactEffects,surfaceCue} from './impact-effects.mjs';
import {createSurgeFx} from './breakwater-surge-fx.mjs';
import {SURGE} from './breakwater-surge.mjs';
import {createSnareTell} from './snare-tell.mjs';
import {createBreakwaterGantry,GANTRY_Z,GANTRY_HEIGHT_SCALE} from './breakwater-gantry.mjs';
import {createBreakwaterDressing} from './breakwater-dressing.mjs';
import {createFoundryDressing} from './foundry-dressing.mjs';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {ARENA,COVER,WEAPONS,ramOpen,wardenOpen,RAM_OPEN_SECONDS,sweepRadius,create,spawn,press,select,tick,MORTAR_RADIUS,CROSS_HALF_WIDTH,RELAY_RADIUS,STILT_RADIUS,splitMarks,SEED_RADIUS,FLANK_RADIUS,HARROW_WIND,seedMarks,harrowLine} from './arena.mjs';
import {VARIANTS} from './variants.mjs';

const $=n=>document.querySelector('#'+n);
const wrap=$('yard'),notice=$('notice'),human=$('hero'),rival=$('enemy');
const set=(el,text)=>{if(el.textContent!==String(text))el.textContent=text;};
const enemyBase=new URL('../../art/actors/dock-enemies/',location.href);
const specialistBase=new URL('../../art/actors/dock-specialists/',location.href);
const ordnanceBase=new URL('../../art/actors/dock-ordnance/',location.href);
const foundryBase=new URL('../../art/actors/dock-foundry/',location.href);
const terminalBase=new URL('../../art/actors/dock-terminal/',location.href);
const weaponBase=new URL('../../art/weapons/',location.href);
const clipNames={idle:'Idle',move:'Move',turn:'Turn',feint:'Move',windup:'Windup',active:'Attack',recover:'Recover',hit:'Hit',defeat:'Defeat'};
const mat=(c,metal=.45,rough=.46)=>new T.MeshStandardMaterial({color:c,metalness:metal,roughness:rough});
const basic=(c,opacity)=>new T.MeshBasicMaterial({color:c,transparent:true,opacity,depthWrite:false,side:T.DoubleSide});
const mesh=(g,m)=>new T.Mesh(g,m);
function box(parent,sz,pos,m){
 const o=mesh(new T.BoxGeometry(...sz),m);o.position.set(...pos);parent.add(o);return o;
}
function joint(parent,x,y,z){
 const o=new T.Group();o.position.set(x,y,z);parent.add(o);return o;
}
const clamp=(v,a,b)=>Math.max(a,Math.min(v,b));
const face=(x,z)=>Math.atan2(x,z);

try{
 const render=new T.WebGLRenderer({antialias:true,powerPreference:'low-power'});
 render.setPixelRatio(Math.min(devicePixelRatio,1.5));render.toneMapping=T.ACESFilmicToneMapping;render.toneMappingExposure=1.16;
 wrap.prepend(render.domElement);
 const coast=new URL(location.href).searchParams.get('arena')==='breakwater';
 const sky=coast?0x496972:0x172b34;
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(DUEL_CAMERA_FOV,1,.09,85);
 scene.background=new T.Color(sky);scene.fog=new T.FogExp2(sky,coast?.028:.036);
 const env=new RoomEnvironment(),pmrem=new T.PMREMGenerator(render);
 scene.environment=pmrem.fromScene(env,.06).texture;scene.environmentIntensity=.40;env.dispose();pmrem.dispose();
 scene.add(new T.HemisphereLight(0xa6dce7,coast?0x3b4b53:0x302822,coast?1.43:1.18));
 const key=new T.DirectionalLight(coast?0xffd9bd:0xffdabd,coast?2.8:2.44);key.position.set(-6,11,4);scene.add(key);
 const rim=new T.DirectionalLight(0x86cafa,1.28);rim.position.set(8,6,-8);scene.add(rim);

 const updateSurge=coast?createSurgeFx(scene):null;
 const gantry=coast?createBreakwaterGantry(scene):null;
 let gantryClock=0;
 const tideNotice=$('tide');
 const dressing=coast?createBreakwaterDressing(scene,COVER):createFoundryDressing(scene,COVER);
 if(coast){
  document.title='Signal Breakwater | Wildshard Combat Prototype';
  $('arena-name').firstChild.data='Signal ';
  $('arena-name').querySelector('span').textContent='Breakwater';
 }
 wrap.dataset.sceneKit=coast?'signal-breakwater':'foundry-evening';
 wrap.dataset.lightPools=String(dressing.lightPools);
 wrap.dataset.practicalLights=String(dressing.practicalLights);
 wrap.dataset.sceneBatches=String(dressing.batches+(gantry?.batches??0));
 wrap.dataset.sceneInstances=String(dressing.instances+(gantry?.instances??0));
 wrap.dataset.sceneCover=String(dressing.coverCount);

 const loader=new GLTFLoader(),alivePlayer=joint(scene,0,0,0);
 function shadow(parent,scale){
  const o=mesh(new T.CircleGeometry(scale,24),basic(0x081116,.39));
  o.rotation.x=-Math.PI/2;o.position.y=.012;parent.add(o);return o;
 }
 shadow(alivePlayer,.49);
 const grip=new T.Group(),gripPoint=new T.Vector3(),aimMarker=new T.Vector3();
 const aimThrust=createThrustAlignment();
 const thrustKits=new Set(['016','021','025']);
 let weaponBasis=null;
 let walker=null,heroHit=0,heroTurn=0,heroYaw=Math.PI;
 const heroClips=['Idle','Stride','Turn','Dodge','Hit','Defeat','Sweep','Chop','Thrust',...Object.values(SIGNATURE_STRIKES)];
 async function loadWalker(){
  const g=await loader.loadAsync(new URL('../../art/actors/forge-walker/walker.glb',location.href).href);
  const hand=g.scene.getObjectByName('grip_R');
  const clips=Object.fromEntries(g.animations.map(a=>[a.name,a]));
  if(!hand||!g.scene.getObjectByName('ground_socket')||heroClips.some(n=>!clips[n]))throw Error('Walker rig or animation missing');
  alivePlayer.add(g.scene);hand.add(grip);
  walker={mixer:new T.AnimationMixer(g.scene),clips,name:null,last:null};
  wrap.dataset.heroRig='Walker';wrap.dataset.weaponSocket=hand.name;
 }
 function heroPose(name,seconds=0,scrub=false){
  if(name===walker.name)return;
  const a=walker.mixer.clipAction(walker.clips[name]).reset();
  if(['Idle','Stride'].includes(name)){a.setLoop(T.LoopRepeat,Infinity);a.clampWhenFinished=false;}
  else{a.setLoop(T.LoopOnce,1);a.clampWhenFinished=true;}
  if(seconds)a.setDuration(seconds);
  a.paused=scrub;
  if(walker.last){walker.last.fadeOut(.063);a.fadeIn(.063);}
  a.play();walker.name=name;walker.last=a;
  wrap.dataset.heroClip=name;
 }
 const warningPlane=mesh(new T.PlaneGeometry(1,1),basic(0xff552f,.29));
 const snareTell=createSnareTell(scene);
 const warningRing=mesh(new T.RingGeometry(.88,1,64),basic(0xff552f,.74));
 // Three reusable decals; the bright outside edge is the same radius as damage.
 const sweepMarks=joint(scene,0,.032,0);
 sweepMarks.rotation.x=-Math.PI/2;sweepMarks.visible=false;
 const sweepDecal=(geometry,color,opacity,order)=>{
  const m=basic(color,opacity);m.toneMapped=false;
  const o=mesh(geometry,m);o.renderOrder=order;sweepMarks.add(o);return o;
 };
 const sweepFill=sweepDecal(new T.CircleGeometry(.988,64),0xa63420,.21,4);
 const sweepEdge=sweepDecal(new T.RingGeometry(.981,1,64),0xff7843,.86,5);
 const sweepClockGeo=new T.RingGeometry(.896,.942,64);
 const sweepClock=sweepDecal(sweepClockGeo,0xffc376,.92,6);
 sweepClock.rotation.z=Math.PI/2;
 const pulseRing=mesh(new T.RingGeometry(.77,1,56),basic(0xffa241,.68));
 const counterRing=mesh(new T.RingGeometry(.92,1,54,1,0,Math.PI*1.66),basic(0x53ffff,.92));
 for(const o of [warningPlane,warningRing,pulseRing,counterRing]){o.rotation.x=-Math.PI/2;o.visible=false;scene.add(o);}
 const fan=(half,color)=>{
  const g=new T.CircleGeometry(1,44,Math.PI*.5-half,half*2),o=mesh(g,basic(color,.32));
  o.rotation.x=-Math.PI/2;o.visible=false;scene.add(o);return o;
 };
 const intakeFan=fan(Math.acos(.89),0xee744e),jetFan=fan(Math.acos(.84),0xee5a36);
 const harrowFan=fan(HARROW_WIND,0xe86a39);
 const harrowTrace=mesh(new T.BoxGeometry(.085,.052,1),basic(0xff8f4b,.92));harrowTrace.visible=false;scene.add(harrowTrace);
 const splitRings=[0,1,2].map(i=>{
  const o=mesh(new T.RingGeometry(.88,1,56),basic(i?0xfcac43:0xf85d39,.77));
  o.rotation.x=-Math.PI/2;o.visible=false;scene.add(o);return o;
 });
 const effects=createImpactEffects(scene),tipPoint=new T.Vector3(),weaponBasePoint=new T.Vector3(),weakPoint=new T.Vector3();
 let fxTip=null,fxGrip=null,previousSlash=null,hitSerial=0,prevFxPhase='';
 const shellShot=mesh(new T.IcosahedronGeometry(.13,1),basic(0xffad68,.99));
 const muzzleTrace=mesh(new T.BoxGeometry(.045,.045,1),basic(0xff996b,.88));
 scene.add(shellShot,muzzleTrace);shellShot.visible=muzzleTrace.visible=false;
 let noticeUntil=0,salvoFlash=0;
 function say(text,until=1){set(notice,text);noticeUntil=s.time+until;}
 const actorBases=[enemyBase,specialistBase,ordnanceBase,foundryBase,terminalBase];
 const manifests=await Promise.all(actorBases.map(path=>fetch(new URL('manifest.json',path)).then(r=>{if(!r.ok)throw Error('Enemy manifest missing');return r.json();})));
 const data={enemyTypes:manifests.flatMap((d,i)=>d.enemyTypes.map(a=>({...a,source:actorBases[i]})))};
 const artists=new Map(),loadingModels=new Map();
 function loadRival(n){
  if(artists.has(n))return Promise.resolve(artists.get(n));
  if(loadingModels.has(n))return loadingModels.get(n);
  const a=data.enemyTypes[n];
  const result=loader.loadAsync(new URL(a.model,a.source).href)
   .then(model=>{artists.set(n,model);return model;})
   .finally(()=>loadingModels.delete(n));
  loadingModels.set(n,result);return result;
 }
 let s=create(data.enemyTypes,{breakwater:coast}),i=0,variant=null,enemy=null,actor=null,weapon=null,wmix=null,wa=null,sequence=0,who=-1;
 const opts=$('weapon');
 for(const w of WEAPONS){const o=document.createElement('option');o.value=w.id;o.textContent=w.name;opts.append(o);}
 const variants=$('variant'),picker=$('rival');
 for(const [n,rival] of data.enemyTypes.entries()){
  const o=document.createElement('option');o.value=String(n);o.textContent=rival.name;picker.append(o);
 }
 for(const v of [{id:'',name:'Base type'},...VARIANTS]){
  const o=document.createElement('option');o.value=v.id;o.textContent=v.id?'Variant: '+v.name:v.name;
  o.title=v.rule??'Original rig and attack';variants.append(o);
 }
 const vCopper=mat(0xaa592b),vViolet=mat(0x685598),vPlating=mat(0x98a5a7,.88,.27),vTeal=new T.MeshBasicMaterial({color:0x67e4d5}),vAmber=new T.MeshBasicMaterial({color:0xffb450});
 function kit(b,parent){
  if(!b.variant)return null;
  const layer=joint(parent,0,0,0),h=b.height,w=b.radius;
  if(b.variant==='rusher'){
   for(const s of [-1,1]){
    box(layer,[.22,.17,.51],[s*w*.80,.57*h,-w*.62],vCopper).rotation.x=.27;
    box(layer,[.17,.12,.06],[s*w*.80,.54*h,-w*.62-.26],vAmber);
   }
  }else if(b.variant==='bulwark'){
   for(const q of [-1,1]){
    box(layer,[.23,.38,.50],[q*w*.76,.58*h,.34],vPlating).rotation.y=q*.32;
    box(layer,[.10,.07,.044],[q*w*.76,.58*h,.58],vAmber);
   }
  }else if(b.variant==='feinter'){
   for(const q of [-1,1]){
    box(layer,[.35,.095,.18],[q*w*.90,.70*h,.04],vViolet).rotation.z=q*.51;
    box(layer,[.085,.07,.039],[q*w*1.12,.78*h,.11],vTeal);
   }
  }else if(b.variant==='echo'){
   for(const q of [-1,1]){
    box(layer,[.075,.36,.08],[q*w*.36,h+.075,-.06],vPlating).rotation.z=q*.18;
    box(layer,[.115,.067,.11],[q*w*.39,h+.255,-.06],vTeal);
   }
  }else{
   const coil=mesh(new T.TorusGeometry(.235,.057,8,20),vCopper);layer.add(coil);
   coil.rotation.x=-Math.PI/2;coil.position.y=.89*h;
   box(layer,[.15,.25,.15],[0,.90*h,0],vAmber);
  }
  return layer;
 }
 const cache=new Map();
 function weaponURL(id){return new URL(id==='014'?'signal-shear/signal-shear.glb':'forge-roster/'+id+'.glb',weaponBase).href;}
 async function loadWeapon(id){
  const t=++sequence;
  if(!cache.has(id))cache.set(id,loader.loadAsync(weaponURL(id)));
  const g=await cache.get(id);
  if(t!==sequence)return;
  if(weapon)grip.remove(weapon);
  weapon=new T.Group();weapon.rotation.x=Math.PI/2;weapon.rotation.z=-.22;weaponBasis=weapon.quaternion.clone();
  weapon.add(g.scene);grip.add(weapon);
  fxTip=g.scene.getObjectByName('tip_socket');fxGrip=g.scene.getObjectByName('grip_socket');
  if(!fxTip||!fxGrip)throw Error('Weapon motion sockets missing');
  wrap.dataset.fxSockets=fxGrip.name+','+fxTip.name;
  wmix=new T.AnimationMixer(g.scene);wa=g.animations.find(c=>c.name==='Arc_Cut'||c.name.startsWith('Attack_'));
  if(!wa)throw Error('Weapon attack clip missing');
  wrap.dataset.equipped=id;
 }
 function start(n){
  if(actor){
   actor.mixer.stopAllAction();
   actor.kiln?.gates.forEach((o,j)=>{o.position.x=actor.kiln.rests[j];});
   if(actor.kit){actor.kit.traverse(o=>o.geometry?.dispose());actor.kit.removeFromParent();}
   scene.remove(actor.group);
  }
  const old=s.weapon;
  s=create(data.enemyTypes,{breakwater:coast});select(s,old);
  heroYaw=face(...s.player.face);heroHit=heroTurn=0;
  effects.clear();previousSlash=null;prevFxPhase='';wrap.dataset.fxPhase='idle';wrap.dataset.fxKind='';
  if(walker){walker.mixer.stopAllAction();walker.name=walker.last=null;heroPose('Idle');}
  i=n;picker.value=String(n);enemy=spawn(s,i,{x:0,z:-2.45},variant);
  const g=artists.get(i);const group=joint(scene,enemy.x,0,enemy.z);group.add(g.scene);shadow(group,enemy.radius*.95);
  const armor=kit(enemy,group);
  if(armor)g.scene.getObjectByName('body')?.attach(armor);
  const mixer=new T.AnimationMixer(g.scene);
  const clips=Object.fromEntries(g.animations.map(c=>[c.name,c]));
  const gates=enemy.attack==='guard'?['door_L','door_R'].map(n=>g.scene.getObjectByName(n)):[];
  const kiln=gates.length&&gates.every(Boolean)?{gates,rests:gates.map(x=>x.position.x),slide:0}:null;
  // The two jaws track actual guard state; remove only the offline-authored jaw tracks.
  if(kiln)for(const [name,clip] of Object.entries(clips))clips[name]=new T.AnimationClip(name,clip.duration,
   clip.tracks.filter(t=>!/^door_[LR]\./.test(t.name)));
  delete wrap.dataset.kilnGap;delete wrap.dataset.kilnGuard;
  // The yard owns heading. Keep the articulated motion but discard the baked root swivel.
  if(clips.Turn)clips.Turn=new T.AnimationClip('Turn',clips.Turn.duration,clips.Turn.tracks.filter(t=>!/^root\.(position|quaternion)$/.test(t.name)));
  actor={group,mixer,weak:g.scene.getObjectByName('weak_socket'),kit:armor,kiln,clips,mode:null,last:null,yaw:face(...enemy.face),turnFor:0,turnCooldown:0};
  wrap.dataset.enemy=enemy.id;wrap.dataset.outcome='';wrap.dataset.variant=enemy.variant??'';wrap.dataset.variantParts=String(armor?.children.length??0);wrap.dataset.variantCue='';wrap.dataset.counterHit='';delete wrap.dataset.thrustAxes;delete wrap.dataset.thrustGap;
  $('win').hidden=true;set($('enemy-name'),enemy.name);say(enemy.rule??('Fight: '+enemy.name),1.4);
 }
 function action(bot,name){
  if(name===actor.mode)return;
  actor.mode=name;
  const clip=actor.clips[name==='active'&&(bot.echoed||['mortar','relay','seed','flank'].includes(bot.attack))?'Special':clipNames[name]]??actor.clips.Idle;
  if(!clip)return;
  if(actor.last){actor.last.fadeOut(.08);}
  const a=actor.mixer.clipAction(clip).reset().fadeIn(.10);
  if(!['idle','move'].includes(name)){
   a.setLoop(T.LoopOnce,1);a.clampWhenFinished=true;
   const sec={turn:.28,windup:bot.windReady,feint:.24,active:bot.activeDuration,recover:bot.recover,hit:.24,defeat:1.03}[name];
   if(sec)a.setDuration(sec);
  }
  a.play();actor.last=a;
  wrap.dataset.pose=clip.name;
 }
 let input=[0,0],pointer=-1;const keys=new Set();
 const updateStick=e=>{
  const b=$('stick').getBoundingClientRect(),x=e.clientX-(b.left+b.width*.5),y=e.clientY-(b.top+b.height*.5);
  const d=Math.hypot(x,y),R=42,k=Math.min(1,R/Math.max(.1,d));
  $('knob').style.transform=`translate(${x*k}px,${y*k}px)`;
  input=d>9?[x/d,y/d]:[0,0];
 };
 $('stick').addEventListener('pointerdown',e=>{pointer=e.pointerId;$('stick').setPointerCapture(pointer);updateStick(e);});
 $('stick').addEventListener('pointermove',e=>{if(e.pointerId===pointer)updateStick(e);});
 for(const op of ['lostpointercapture','pointercancel','pointerup'])$('stick').addEventListener(op,e=>{
  if(e.pointerId===pointer){pointer=-1;input=[0,0];$('knob').style.transform='';}
 });
 const pass=k=>{
  if(rivalLoading||(k==='attack'&&wrap.dataset.equipped!==WEAPONS[s.weapon].id))return;
  if(!press(s,k))return;
  if(k==='attack'&&wmix&&wa){wmix.stopAllAction();const a=wmix.clipAction(wa).reset().setLoop(T.LoopOnce,1);a.clampWhenFinished=false;a.setDuration(WEAPONS[s.weapon].cycle);a.play();}
 };
 $('dodge').addEventListener('pointerdown',e=>{e.preventDefault();pass('dodge');});
 $('attack').addEventListener('pointerdown',e=>{e.preventDefault();pass('attack');});
 for(const k of ['attack','dodge'])$(k).addEventListener('click',e=>{if(!e.detail)pass(k);});
 document.addEventListener('keydown',e=>{
  if(e.target.tagName==='SELECT'||e.target.tagName==='BUTTON')return;
  if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space','ShiftLeft','ShiftRight'].includes(e.code))e.preventDefault();
  keys.add(e.code);if(e.repeat)return;
  if(e.code==='Space')pass('attack');if(e.code.startsWith('Shift'))pass('dodge');
 });
 document.addEventListener('keyup',e=>keys.delete(e.code));window.addEventListener('blur',()=>keys.clear());
 opts.addEventListener('change',()=>{
  const n=WEAPONS.findIndex(w=>w.id===opts.value);select(s,n);
  opts.value=WEAPONS[s.weapon].id;void loadWeapon(opts.value).catch(()=>say('Weapon load failed.',3));
 });
 let rivalLoading=false;
 const nav=[$('next'),$('win-next'),$('reset'),variants,opts,picker];
 async function chooseRival(n){
  if(rivalLoading||n===i||!Number.isInteger(n)||!data.enemyTypes[n])return;
  if(artists.has(n)){start(n);return;}
  rivalLoading=true;wrap.dataset.rivalLoading=String(n+1);
  for(const b of nav)b.disabled=true;
  say('Loading '+data.enemyTypes[n].name+'…',90);
  try{await loadRival(n);start(n);}
  catch(e){picker.value=String(i);say('Rival could not load. Select it or tap Next to retry.',3);}
  finally{rivalLoading=false;delete wrap.dataset.rivalLoading;for(const b of nav)b.disabled=false;}
 }
 variants.addEventListener('change',()=>{variant=variants.value||null;start(i);});
 picker.addEventListener('change',()=>void chooseRival(Number(picker.value)));
 $('next').onclick=$('win-next').onclick=()=>void chooseRival((i+1)%data.enemyTypes.length);
 $('reset').onclick=()=>start(i);
 await Promise.all([loadRival(0),loadWeapon('014'),loadWalker()]);
 start(0);
 const look=new T.Vector3(),goal=new T.Vector3(),point=new T.Vector3(),cameraAxis=new T.Vector3(...DUEL_CAMERA_AXIS);
 let cameraDistance=0;
 let last=0,accum=0;
 function resize(){const w=wrap.clientWidth,h=wrap.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();render.setSize(w,h,false);}
 window.addEventListener('resize',resize);resize();
 wrap.dataset.state='ready';
 render.setAnimationLoop(now=>{
  const dt=last?clamp((now-last)*.001,0,.05):0;last=now;accum+=dt;
  const vx=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const vz=Number(keys.has('KeyS')||keys.has('ArrowDown'))-Number(keys.has('KeyW')||keys.has('ArrowUp'));
  const m=pointer!==-1?input:[vx,vz];const p=s.player;let impactEvent=null,blockedHit=false;
  const cut=who!==i;if(cut)who=i;
  for(;accum>=1/60;accum-=1/60)if(!rivalLoading)tick(s,1/60,m);
  for(const e of s.events.splice(0)){
   if(e.type==='enemy-state'&&e.state==='windup'){
    const cue={windmill:'SWEEP · step back',beam:'BEAM · move sideways',pounce:'POUNCE · dodge',charge:'CHARGE · break the line',
     hook:'HOOK · leave the lane',guard:'CORE OPEN · watch the shove',burrow:'SNARE · leave the mark',burst:'BURST · get out of the ring',salvo:'SALVO · step out of the line',lunge:'LUNGE · dodge sideways',mortar:'MORTAR · leave the landing zone',crosscut:'CROSSCUT · step forward or back',vacuum:'INTAKE · leave the pull lane',stilt:'DOUBLE CUT · leave the marks',relay:'LANTERNS · stay in the gap',recoil:'RECOIL · step out of the jet',shutter:'SHUTTERS OPEN · punish the piston',seed:'SEED LINE · step across the marks',harrow:'SWEEP · leave the fan or dodge through',flank:'SIDE STEP · leave your mark'};
    say(cue[enemy.attack],enemy.windReady+.18);
   }
   if(e.type==='enemy-state'&&e.state==='recover'&&wardenOpen(enemy))say('CORE OPEN · strike before it closes',enemy.recover);
   if(e.type==='enemy-state'&&e.state==='recover'&&ramOpen(enemy))say('ARMOR OPEN · counter now',RAM_OPEN_SECONDS);
   if(e.type==='salvo-shot')salvoFlash=.11;
   if(e.type==='mortar-impact')say('Mortar impact',.34);
   if(e.type==='shield')blockedHit=true;
   const variation={shield:'Shield reduced your hit',rush:'RUSH · take space',feint:'FEINT · watch the next tell',echo:'ECHO · follow-up coming',pulse:'OVERLOAD · step outside',discharge:'Discharge'};
   if(variation[e.type]){
    wrap.dataset.variantCue=e.type;
    say(variation[e.type],e.type==='pulse'?.77:.45);
   }
   if(e.type==='enemy-hit'){
    impactEvent={style:p.slash?.weapon.style??WEAPONS[s.weapon].style,blocked:blockedHit};
    if(e.counter){wrap.dataset.counterHit=String(e.damage);say('COUNTER · '+e.damage+' damage',.66);}
    else if(!blockedHit)say('Hit',.34);
   }
   if(e.type==='player-hit'){heroHit=.26;say(e.style==='surge'?'Tide hit · −'+e.damage:'You took a hit',.65);}
   if(e.type==='defeat'){wrap.dataset.outcome='win';set($('win-title'),enemy.name+' defeated');set($('win-body'),'Try a different rival or change weapons.');$('win').hidden=false;}
  }
  if(p.hp===0){wrap.dataset.outcome='loss';set($('win-title'),'Walker down');set($('win-body'),'Restart or try another rival.');$('win').hidden=false;}
  if(s.time>noticeUntil)set(notice,WEAPONS[s.weapon].name);
  human.value=p.hp;set($('hero-hp'),p.hp);rival.max=enemy.maxHp;rival.value=enemy.life;set($('enemy-hp'),enemy.life);
  if(s.surge){
   const phase=s.surge.section?.phase??'idle';
   updateSurge(s.surge.section);
   wrap.dataset.surgePhase=phase;wrap.dataset.surgeHits=String(s.surge.hits);
   wrap.dataset.surgeFront=s.surge.section?.hi?.toFixed(3)??'';
   wrap.dataset.surgeLeft=s.surge.section?.remaining?.toFixed(3)??'';
   const nearby=Math.abs(p.x-SURGE.x)<SURGE.halfWidth+1.25&&p.z>SURGE.near-1&&p.z<SURGE.far+1;
   tideNotice.hidden=!nearby||phase==='idle'||p.hp===0;
   if(!tideNotice.hidden)set(tideNotice,phase==='warn'?'TIDE INCOMING · leave the blue lane':'TIDE CROSSING');
  }
  wrap.dataset.playerX=p.x.toFixed(3);wrap.dataset.playerZ=p.z.toFixed(3);
  wrap.dataset.enemyX=enemy.x.toFixed(3);wrap.dataset.enemyZ=enemy.z.toFixed(3);
  alivePlayer.position.set(p.x,0,p.z);
  const wish=face(...p.face),yawErr=Math.atan2(Math.sin(wish-heroYaw),Math.cos(wish-heroYaw));
  const moving=Math.hypot(...m)>.10&&!rivalLoading;
  if(Math.abs(yawErr)>.88&&moving&&!p.slash&&!p.dodge&&heroTurn<=0)heroTurn=.25;
  heroYaw+=yawErr*(1-Math.exp(-dt*(p.slash?23:14)));alivePlayer.rotation.y=heroYaw;
  heroHit=Math.max(0,heroHit-dt);heroTurn=Math.max(0,heroTurn-dt);
  const strike=p.slash?.weapon;
  if(p.hp===0)heroPose('Defeat',.95);
  else if(p.dodge)heroPose('Dodge',.245);
  else if(strike){
   heroPose(walkerStrike(strike),0,true);
   const elapsed=impactEvent?p.slash.releaseAt:p.slash.time;
   const phase=walkerStrikePhase(elapsed,p.slash.releaseAt??strike.wind,strike.cycle);
   walker.last.time=walker.last.getClip().duration*phase;
   wrap.dataset.heroStrikePhase=phase.toFixed(5);
   wrap.dataset.heroStrikeTime=elapsed.toFixed(5);
   wrap.dataset.heroStrikeRelease=p.slash.releaseAt?.toFixed(5)??'';
  }
  else if(heroHit)heroPose('Hit',.26);
  else if(heroTurn)heroPose('Turn',.25);
  else if(moving)heroPose('Stride',.61);
  else heroPose('Idle',1.6);
  if(!strike||p.hp===0)delete wrap.dataset.heroStrikePhase;
  walker.mixer.update(dt);
  wmix?.update(dt);
  grip.getWorldPosition(gripPoint);alivePlayer.worldToLocal(gripPoint);
  wrap.dataset.gripLocal=gripPoint.toArray().map(x=>x.toFixed(3)).join(',');
  actor.group.position.set(enemy.x,0,enemy.z);
  const tracking=enemy.state==='idle'||enemy.state==='move';
  const locking=enemy.state==='windup'||enemy.state==='active';
  const enemyYaw=face(...enemy.face),enemyYawError=Math.atan2(Math.sin(enemyYaw-actor.yaw),Math.cos(enemyYaw-actor.yaw));
  actor.turnCooldown=Math.max(0,actor.turnCooldown-dt);
  if(tracking&&Math.abs(enemyYawError)>.34&&!actor.turnCooldown){
   actor.turnFor=.28;actor.turnCooldown=.55;
  }
  actor.turnFor=tracking?Math.max(0,actor.turnFor-dt):0;
  // Never lag the readable, locked attacks behind the simulation.
  if(tracking)actor.yaw+=enemyYawError*(1-Math.exp(-dt*7));
  else if(locking)actor.yaw=face(...enemy.lock);
  actor.group.rotation.y=actor.yaw;
  action(enemy,actor.turnFor?'turn':enemy.state);actor.mixer.update(dt);
  if(actor.kiln){
   const open=wardenOpen(enemy),k=actor.kiln;
   const target=(open||enemy.state==='defeat') ? .30 : 0;
   k.slide+=Math.sign(target-k.slide)*Math.min(Math.abs(target-k.slide),dt*4);
   k.gates.forEach((o,j)=>{o.position.x=k.rests[j]+(j===0?-k.slide:k.slide);});
   wrap.dataset.kilnGap=(2*k.slide).toFixed(3);
   wrap.dataset.kilnGuard=open?'open':enemy.life>0?'closed':'down';
  }
  const bomb=enemy.attack==='mortar',cross=enemy.attack==='crosscut';
  const two=['stilt','relay','seed'].includes(enemy.attack),flank=enemy.attack==='flank',harrow=enemy.attack==='harrow';
  const markerAfter=enemy.life>0&&enemy.state==='active'&&flank&&!enemy.dashHit;
  const warn=enemy.life>0&&(enemy.state==='windup'||(bomb&&enemy.state==='active'&&!enemy.dashHit));
  const radial=['windmill','pounce','burst','mortar','flank'].includes(enemy.attack);
  const fanned=enemy.attack==='vacuum'||enemy.attack==='recoil'||harrow;
  const sweep=enemy.attack==='windmill'&&enemy.life>0;
  const releasing=sweep&&enemy.state==='active'&&enemy.t<.14;
  sweepMarks.visible=sweep&&(warn||releasing);
  wrap.dataset.sweepPhase=sweepMarks.visible?(releasing?'release':'windup'):'';
  if(sweepMarks.visible){
   const r=sweepRadius(enemy);
   sweepMarks.position.set(enemy.x,.032,enemy.z);sweepMarks.scale.setScalar(r);
   const left=releasing?0:clamp(1-enemy.t/enemy.windReady,0,1);
   const fade=releasing?1-enemy.t/.14:1;
   sweepEdge.material.opacity=(releasing?.91:.86)*fade;
   sweepFill.material.opacity=(releasing?.26:.19)*fade;
   sweepClock.visible=!releasing;
   sweepClockGeo.setDrawRange(0,6*Math.ceil(left*64));
   wrap.dataset.sweepRadius=r.toFixed(3);wrap.dataset.sweepRemaining=left.toFixed(3);
  }
  warningRing.visible=(warn&&radial&&!sweep)||markerAfter;warningPlane.visible=warn&&!radial&&!two&&!fanned&&enemy.attack!=='burrow';
  intakeFan.visible=enemy.life>0&&enemy.attack==='vacuum'&&(warn||enemy.state==='active'&&enemy.t<.42);
  jetFan.visible=warn&&enemy.attack==='recoil';
  for(const o of [intakeFan,jetFan])if(o.visible){
   o.position.set(enemy.x,.045,enemy.z);o.rotation.z=face(...enemy.lock)+Math.PI;
   o.scale.setScalar(enemy.reach+(o===intakeFan?.14:.10));
  }
  harrowFan.visible=harrow&&warn;
  if(harrowFan.visible){harrowFan.position.set(enemy.x,.044,enemy.z);harrowFan.rotation.z=face(...enemy.lock)+Math.PI;harrowFan.scale.setScalar(enemy.reach+.12);}
  harrowTrace.visible=harrow&&enemy.life>0&&enemy.state==='active';
  if(harrowTrace.visible){
   const [x,z]=harrowLine(enemy),d=enemy.reach;
   harrowTrace.position.set(enemy.x+x*d*.5,1.30,enemy.z+z*d*.5);harrowTrace.rotation.y=face(x,z);harrowTrace.scale.z=d;
  }
  if(warningRing.visible){
   const r=enemy.attack==='pounce'?.85:enemy.reach+.25,d=enemy.attack==='pounce'?Math.min(enemy.lockLength,enemy.reach):0;
   const marked=bomb||flank;
   warningRing.position.set(marked?enemy.mark.x:enemy.x+enemy.lock[0]*d,.027,marked?enemy.mark.z:enemy.z+enemy.lock[1]*d);
   warningRing.scale.setScalar(bomb?MORTAR_RADIUS:flank?FLANK_RADIUS:r);
  }
  const tell=snareTell(enemy);
  if(tell){
   wrap.dataset.snarePhase=tell.phase;wrap.dataset.snareRadius=tell.radius;
   wrap.dataset.snareX=enemy.mark.x.toFixed(3);wrap.dataset.snareZ=enemy.mark.z.toFixed(3);
  }else delete wrap.dataset.snarePhase;
  if(warningPlane.visible){
   const d=enemy.reach;
   warningPlane.position.set(cross?enemy.mark.x:enemy.x+enemy.lock[0]*d/2,.030,cross?enemy.mark.z:enemy.z+enemy.lock[1]*d/2);
   warningPlane.rotation.z=face(...enemy.lock)+(cross?Math.PI/2:0);
   warningPlane.scale.set(cross?CROSS_HALF_WIDTH*2:enemy.attack==='beam'||enemy.attack==='salvo'?1.22:1.48,cross?3.44:d,1);
  }
  const splitVisible=two&&enemy.life>0&&(enemy.state==='windup'||enemy.state==='active');
  const seeded=enemy.attack==='seed';
  const twins=splitVisible?(seeded?seedMarks(enemy):splitMarks(enemy,enemy.attack==='stilt'?.54:1.23)):null;
  splitRings.forEach((r,j)=>{
   r.visible=splitVisible&&j<twins.length&&(enemy.state==='windup'||enemy.shots<=j);
   if(r.visible){r.position.set(twins[j].x,.035+j*.005,twins[j].z);r.scale.setScalar(seeded?SEED_RADIUS:enemy.attack==='stilt'?STILT_RADIUS:RELAY_RADIUS);}
  });
  shellShot.visible=bomb&&enemy.state==='active'&&!enemy.dashHit&&enemy.life>0;
  if(shellShot.visible){
   const v=clamp(enemy.t/.50,0,1);
   shellShot.position.set(T.MathUtils.lerp(enemy.x,enemy.mark.x,v),T.MathUtils.lerp(1.66,.09,v)+Math.sin(Math.PI*v)*2.52,T.MathUtils.lerp(enemy.z,enemy.mark.z,v));
  }
  salvoFlash=Math.max(0,salvoFlash-dt);
  muzzleTrace.visible=enemy.life>0&&enemy.state==='active'&&enemy.attack==='salvo'&&salvoFlash>0;
  if(muzzleTrace.visible){
   const d=enemy.reach, x=enemy.lock[0],z=enemy.lock[1];
   muzzleTrace.position.set(enemy.x+x*d/2,1.2,enemy.z+z*d/2);muzzleTrace.rotation.y=face(x,z);
   muzzleTrace.scale.z=d;muzzleTrace.material.opacity=salvoFlash/.11*.88;
  }
  pulseRing.visible=enemy.life>0&&enemy.pulse>0;
  if(pulseRing.visible){pulseRing.position.set(enemy.x,.047,enemy.z);pulseRing.scale.setScalar(2.25);pulseRing.material.opacity=.62+Math.sin(enemy.pulse*30)*.18;}
  counterRing.visible=ramOpen(enemy);
  wrap.dataset.counterOpen=counterRing.visible?'1':'0';
  if(counterRing.visible){
   counterRing.position.set(enemy.x,.054,enemy.z);counterRing.scale.setScalar(enemy.r+.39);
   counterRing.material.opacity=.33+.58*Math.max(0,1-enemy.t/RAM_OPEN_SECONDS);
  }
  const weak=(impactEvent||strike?.style==='thrust')?actor.weak?.getWorldPosition(weakPoint):null;
  const cue=impactEvent?surfaceCue(p,enemy,weak?.y):null;
  if(thrustKits.has(wrap.dataset.equipped)&&weapon){
   const dx=enemy.x-p.x,dz=enemy.z-p.z,range=Math.hypot(dx,dz);
   const active=strike?.style==='thrust'&&(enemy.life>0||impactEvent)&&
    (impactEvent||range<strike.reach+enemy.r+.45&&dx*p.face[0]+dz*p.face[1]>.15);
   const at=impactEvent?p.slash?.releaseAt:p.slash?.time;
   const weight=active?beaconThrustWeight(at,p.slash.releaseAt??strike.wind,strike.cycle):0;
   let target=null;
   if(active){
    const seek=strike.id==='021'&&weak?weak:null;
    target=seek??aimMarker.fromArray((cue??surfaceCue(p,enemy,weak?.y)).at);
   }
   const a=aimThrust(weapon,weaponBasis,grip,fxGrip,fxTip,target,weight);
   if(impactEvent&&a){
    wrap.dataset.thrustAxes=[a.before.toFixed(2),a.after.toFixed(2),a.gripSlip.toFixed(5)].join(',');
    wrap.dataset.thrustGap=[a.tipGapBefore.toFixed(3),a.tipGapAfter.toFixed(3),a.tipAxialError.toFixed(3)].join(',');
   }
  }
  if(impactEvent){
   effects.hit(cue.at,cue.outer,impactEvent.style,impactEvent.blocked);
   wrap.dataset.fxImpact=String(++hitSerial);wrap.dataset.fxKind=impactEvent.blocked?'block':impactEvent.style;
   wrap.dataset.fxAnchor=cue.at.map(x=>x.toFixed(3)).join(',');
  }
  if(p.slash&&p.slash!==previousSlash)previousSlash=p.slash;
  const swingWindow=p.slash&&p.slash.time>=Math.max(.075,p.slash.weapon.wind-.105)&&p.slash.time<=p.slash.weapon.wind+.11;
  const trailCount=effects.trailSample(dt,fxGrip?.getWorldPosition(weaponBasePoint),fxTip?.getWorldPosition(tipPoint),swingWindow,previousSlash?.weapon.style);
  const sparkCount=effects.stepParticles(impactEvent?0:dt);
  const phase=sparkCount?'impact':trailCount?'trail':'idle';
  if(prevFxPhase!==phase){wrap.dataset.fxPhase=phase;prevFxPhase=phase;}
  wrap.dataset.fxTrailSegments=String(trailCount);wrap.dataset.fxParticles=String(sparkCount);
  if(sparkCount)wrap.dataset.fxAgeMs=String(Math.round(effects.age()*1000));
  // Frame both rigs without changing the world-relative stick axes.
  const a=cut?1:1-Math.exp(-dt*8),dx=enemy.x-p.x,dz=enemy.z-p.z;
  look.lerp(goal.set(p.x+dx*.46,.91,p.z+dz*.46),a);
  const fit=duelDistance(look,camera.aspect,[{x:p.x,z:p.z,radius:.59,height:2.14},enemy]);
  cameraDistance=cut?fit:Math.max(fit,cameraDistance+(fit-cameraDistance)*(1-Math.exp(-dt*4)));
  camera.position.copy(look).addScaledVector(cameraAxis,cameraDistance);
  wrap.dataset.cameraDistance=cameraDistance.toFixed(3);
  camera.lookAt(look);camera.updateMatrixWorld();
  const viewport=(who,x,h,z)=>{
   point.set(x,h,z).project(camera);
   wrap.dataset[who+'ViewX']=point.x.toFixed(3);wrap.dataset[who+'ViewY']=point.y.toFixed(3);
  };
  viewport('player',p.x,1.02,p.z);viewport('enemy',enemy.x,Math.min(enemy.height*.60,1.10),enemy.z);
  if(gantry){
   const pose=gantry.step(gantryClock+=dt);
   viewport('cargo',pose.x,(4.09-pose.drop)*GANTRY_HEIGHT_SCALE,GANTRY_Z);
   wrap.dataset.gantryX=pose.x.toFixed(3);
   wrap.dataset.gantryDrop=pose.drop.toFixed(3);
   wrap.dataset.gantryTriangles=String(gantry.triangles);
  }
  render.render(scene,camera);
 });
}catch(e){wrap.dataset.state='error';set(notice,'Forge Yard could not load. WebGL and served assets are required.');console.error(e);}
