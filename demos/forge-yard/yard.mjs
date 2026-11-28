import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {ARENA,COVER,WEAPONS,create,spawn,press,select,tick} from './arena.mjs';

const $=n=>document.querySelector('#'+n);
const wrap=$('yard'),notice=$('notice'),human=$('hero'),rival=$('enemy');
const set=(el,text)=>{if(el.textContent!==String(text))el.textContent=text;};
const enemyBase=new URL('../../art/actors/dock-enemies/',location.href);
const specialistBase=new URL('../../art/actors/dock-specialists/',location.href);
const weaponBase=new URL('../../art/weapons/',location.href);
const clipNames={idle:'Idle',move:'Move',windup:'Windup',active:'Attack',recover:'Recover',hit:'Hit',defeat:'Defeat'};
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
 render.setPixelRatio(Math.min(devicePixelRatio,1.5));render.toneMapping=T.ACESFilmicToneMapping;render.toneMappingExposure=1.3;
 wrap.prepend(render.domElement);
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(46,1,.09,85);
 scene.background=new T.Color(0x324a57);scene.fog=new T.FogExp2(0x324a57,.038);
 const env=new RoomEnvironment(),pmrem=new T.PMREMGenerator(render);
 scene.environment=pmrem.fromScene(env,.06).texture;scene.environmentIntensity=.52;env.dispose();pmrem.dispose();
 scene.add(new T.HemisphereLight(0xa1d8df,0x57453c,2.05));
 const key=new T.DirectionalLight(0xffc494,3.8);key.position.set(-6,11,4);scene.add(key);
 const rim=new T.DirectionalLight(0x7ac3ff,1.45);rim.position.set(8,6,-8);scene.add(rim);

 const stone=mat(0x3c545b,.25,.66),stoneAlt=mat(0x375056,.23,.73),deck=mat(0x202d33,.65,.46);
 const amber=mat(0x98703b),paint=mat(0xa36333),cold=mat(0x255a60),brass=mat(0xa97543,.67,.35),navy=mat(0x24475f),skin=mat(0x9f7758,.1,.57);
 const accent=mat(0xc49153),flex=mat(0x233037,.28,.68);const glint=new T.MeshBasicMaterial({color:0x76dfd2});
 box(scene,[80,.25,80],[0,-.5,0],deck);
 const tilePositions=[[],[]],transform=new T.Matrix4();
 for(let x=-10;x<=10;x+=2)for(let z=-10;z<=10;z+=2)tilePositions[Number((x*17+z*13)%8===0)].push([x,z]);
 const tileMesh=new T.BoxGeometry(1.985,.18,1.985);
 tilePositions.forEach((cells,i)=>{
  const batch=new T.InstancedMesh(tileMesh,i?stoneAlt:stone,cells.length);
  cells.forEach(([x,z],n)=>batch.setMatrixAt(n,transform.makeTranslation(x,-.10,z)));
  batch.computeBoundingSphere();scene.add(batch);
 });
 for(const [x,z,r] of COVER){
  box(scene,[r*1.56,1.47,r*1.56],[x,.716,z],paint);
  for(const h of [.19,1.27]){
   box(scene,[r*1.65,.12,r*1.65],[x,h,z],brass);
  }
  box(scene,[r*.65,.36,.04],[x,.78,z+r*.79],deck);
 }
 for(let i=0;i<7;i++){
  const x=-9+i*3;
  for(const z of [-10.65,10.65]){
   box(scene,[2.78,.70,.35],[x,.32,z],deck);
   box(scene,[2.37,.10,.40],[x,.68,z],amber);
  }
 }
 for(const side of [-1,1]){
  for(let z=-8;z<=8;z+=4){
   box(scene,[.42,1.02,3.62],[side*10.65,.48,z],deck);
   box(scene,[.48,.09,3.12],[side*10.65,1.025,z],amber);
  }
  for(const z of [-9,9]){
   box(scene,[.55,4.08,.55],[side*9.5,2,z],cold);
   box(scene,[.74,.32,.74],[side*9.5,3.97,z],brass);
   box(scene,[.29,.11,.16],[side*9.5,3.91,z+(.38*-Math.sign(z))],glint);
  }
 }
 for(const z of [-8.85,8.85])for(let i=-5;i<=5;i++)box(scene,[.48,.013,.22],[i*.86,.006,z],amber).rotation.y=-.35;
 const gantry=joint(scene,0,0,-12.7);
 for(const x of [-5.2,5.2]){
  box(gantry,[.55,7,.66],[x,3.42,0],cold);
  box(gantry,[1.1,.26,1.35],[x,.10,0],deck);
 }
 box(gantry,[11.1,.68,.56],[0,6.55,0],paint);
 for(let x=-4.9;x<5;x+=.84)box(gantry,[.38,.43,.06],[x,6.53,.31],amber).rotation.z=.53;

 const loader=new GLTFLoader(),alivePlayer=joint(scene,0,0,0);
 function shadow(parent,scale){
  const o=mesh(new T.CircleGeometry(scale,24),basic(0x081116,.39));
  o.rotation.x=-Math.PI/2;o.position.y=.012;parent.add(o);return o;
 }
 const shell=joint(alivePlayer,0,0,0);shadow(alivePlayer,.5);
 box(shell,[.61,.62,.38],[0,1.18,0],navy);
 box(shell,[.49,.11,.43],[0,.88,0],flex);
 box(shell,[.40,.32,.37],[0,1.66,0],accent);
 box(shell,[.32,.096,.023],[0,1.68,.194],glint);
 box(shell,[.51,.11,.41],[0,1.83,0],navy);
 box(shell,[.29,.38,.17],[0,1.29,-.24],deck);
 box(shell,[.095,.23,.04],[0,1.32,-.33],glint);
 const hipL=joint(shell,-.15,.83,0),hipR=joint(shell,.15,.83,0);
 for(const hip of [hipL,hipR]){box(hip,[.19,.61,.21],[0,-.30,0],flex);box(hip,[.23,.19,.34],[0,-.70,.07],navy);}
 const left=joint(shell,-.38,1.40,0),right=joint(shell,.38,1.40,0);
 for(const arm of [left,right]){
  box(arm,[.26,.22,.28],[0,-.055,0],accent);
  box(arm,[.16,.43,.19],[0,-.30,.03],navy);
  box(arm,[.17,.14,.18],[0,-.55,.04],skin);
 }
 const grip=joint(right,.02,-.57,.10);

 const warningPlane=mesh(new T.PlaneGeometry(1,1),basic(0xff552f,.29));
 const warningRing=mesh(new T.RingGeometry(.88,1,64),basic(0xff552f,.74));
 const attackRing=mesh(new T.RingGeometry(.76,1,40,1,-.8,1.6),basic(0x8de3d7,.65));
 for(const o of [warningPlane,warningRing,attackRing]){o.rotation.x=-Math.PI/2;o.visible=false;scene.add(o);}
 const flash=mesh(new T.IcosahedronGeometry(.27,1),basic(0x9dfdf0,.83));scene.add(flash);flash.visible=false;
 let impact=.0,noticeUntil=0;
 function say(text,until=1){set(notice,text);noticeUntil=s.time+until;}
 const manifests=await Promise.all([enemyBase,specialistBase].map(path=>fetch(new URL('manifest.json',path)).then(r=>{if(!r.ok)throw Error('Enemy manifest missing');return r.json();})));
 const data={enemyTypes:manifests.flatMap((d,i)=>d.enemyTypes.map(a=>({...a,source:i?specialistBase:enemyBase})))};
 const artists=await Promise.all(data.enemyTypes.map(a=>loader.loadAsync(new URL(a.model,a.source).href)));
 let s=create(data.enemyTypes),i=0,enemy=null,actor=null,weapon=null,wmix=null,wa=null,sequence=0,who=-1;
 const opts=$('weapon');
 for(const w of WEAPONS){const o=document.createElement('option');o.value=w.id;o.textContent=w.name;opts.append(o);}
 const cache=new Map();
 function weaponURL(id){return new URL(id==='014'?'signal-shear/signal-shear.glb':'forge-roster/'+id+'.glb',weaponBase).href;}
 async function loadWeapon(id){
  const t=++sequence;
  if(!cache.has(id))cache.set(id,loader.loadAsync(weaponURL(id)));
  const g=await cache.get(id);
  if(t!==sequence)return;
  if(weapon)grip.remove(weapon);
  weapon=new T.Group();weapon.rotation.x=Math.PI/2;weapon.rotation.z=-.22;
  weapon.add(g.scene);grip.add(weapon);
  wmix=new T.AnimationMixer(g.scene);wa=g.animations.find(c=>c.name==='Arc_Cut'||c.name.startsWith('Attack_'));
  if(!wa)throw Error('Weapon attack clip missing');
  wrap.dataset.equipped=id;
 }
 function start(n){
  if(actor){actor.mixer.stopAllAction();scene.remove(actor.group);}
  const old=s.weapon;
  s=create(data.enemyTypes);select(s,old);
  i=n;enemy=spawn(s,i,{x:0,z:-2.45});
  const g=artists[i];const group=joint(scene,enemy.x,0,enemy.z);group.add(g.scene);shadow(group,enemy.radius*.95);
  const mixer=new T.AnimationMixer(g.scene);
  actor={group,mixer,clips:Object.fromEntries(g.animations.map(c=>[c.name,c])),mode:null,last:null};
  wrap.dataset.enemy=enemy.id;wrap.dataset.outcome='';
  $('win').hidden=true;set($('enemy-name'),enemy.name);say('Fight: '+enemy.name,1.4);
 }
 function action(bot,name){
  if(name===actor.mode)return;
  actor.mode=name;
  const clip=actor.clips[clipNames[name]??'Idle'];
  if(!clip)return;
  if(actor.last){actor.last.fadeOut(.08);}
  const a=actor.mixer.clipAction(clip).reset().fadeIn(.10);
  if(!['idle','move'].includes(name)){
   a.setLoop(T.LoopOnce,1);a.clampWhenFinished=true;
   const sec={windup:bot.windup,active:bot.attack==='charge'?.56:bot.attack==='pounce'?.39:.29,recover:bot.recover,hit:.24,defeat:1.03}[name];
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
  if(k==='attack'&&wrap.dataset.equipped!==WEAPONS[s.weapon].id)return;
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
 $('next').onclick=$('win-next').onclick=()=>start((i+1)%artists.length);$('reset').onclick=()=>start(i);
 start(0);await loadWeapon('014');
 const look=new T.Vector3(),goal=new T.Vector3();
 let last=0,accum=0,walk=0;
 function resize(){const w=wrap.clientWidth,h=wrap.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();render.setSize(w,h,false);}
 window.addEventListener('resize',resize);resize();
 wrap.dataset.state='ready';
 render.setAnimationLoop(now=>{
  const dt=last?clamp((now-last)*.001,0,.05):0;last=now;accum+=dt;
  const vx=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  const vz=Number(keys.has('KeyS')||keys.has('ArrowDown'))-Number(keys.has('KeyW')||keys.has('ArrowUp'));
  const m=pointer!==-1?input:[vx,vz];const p=s.player;
  if(who!==i){who=i;look.set(p.x,.72,p.z-1.65);camera.position.set(p.x,6.4,p.z+7.5);}
  for(;accum>=1/60;accum-=1/60)tick(s,1/60,m);
  for(const e of s.events.splice(0)){
   if(e.type==='enemy-state'&&e.state==='windup'){
    const cue={windmill:'SWEEP · step back',beam:'BEAM · move sideways',pounce:'POUNCE · dodge',charge:'CHARGE · break the line',
     hook:'HOOK · leave the lane',guard:'SHIELD · circle round',burrow:'SNARE · leave the mark',burst:'BURST · get out of the ring'};
    say(cue[enemy.attack],enemy.windup+.18);
   }
   if(e.type==='shield')say('Shield reduced your hit',.45);
   if(e.type==='enemy-hit'){impact=.26;flash.position.set(enemy.x,enemy.attack==='beam'?1.22:.82,enemy.z);say('Hit',.34);}
   if(e.type==='player-hit')say('You took a hit',.65);
   if(e.type==='defeat'){wrap.dataset.outcome='win';set($('win-title'),enemy.name+' defeated');set($('win-body'),'Try a different rival or change weapons.');$('win').hidden=false;}
  }
  if(p.hp===0){wrap.dataset.outcome='loss';set($('win-title'),'Walker down');set($('win-body'),'Restart or try another rival.');$('win').hidden=false;}
  if(s.time>noticeUntil)set(notice,WEAPONS[s.weapon].name);
  human.value=p.hp;set($('hero-hp'),p.hp);rival.max=enemy.maxHp;rival.value=enemy.life;set($('enemy-hp'),enemy.life);
  wrap.dataset.playerX=p.x.toFixed(3);wrap.dataset.playerZ=p.z.toFixed(3);
  wrap.dataset.enemyX=enemy.x.toFixed(3);wrap.dataset.enemyZ=enemy.z.toFixed(3);
  alivePlayer.position.set(p.x,0,p.z);alivePlayer.rotation.y=face(...p.face);
  walk+=dt*(Math.abs(m[0])+Math.abs(m[1])>.1?11.8:0);
  const stride=(Math.abs(m[0])+Math.abs(m[1])>.1&&!p.slash)?Math.sin(walk)*.52:0;
  hipL.rotation.x=stride;hipR.rotation.x=-stride;left.rotation.x=-stride*.35;
  shell.position.y=p.dodge?-.23:Math.abs(stride)*.075;
  shell.rotation.x=p.dodge?.45:0;
  if(p.slash){const a=clamp(p.slash.time/p.slash.weapon.cycle,0,1);right.rotation.z=.36-Math.sin(a*Math.PI)*1.17;right.rotation.x=-.26-Math.sin(a*Math.PI)*.67;}
  else{right.rotation.x=.13+stride*.35;right.rotation.z=.13;}
  wmix?.update(dt);
  actor.group.position.set(enemy.x,0,enemy.z);actor.group.rotation.y=face(...enemy.face);
  action(enemy,enemy.state);actor.mixer.update(dt);
  const warn=enemy.state==='windup'&&enemy.life>0,radial=['windmill','pounce','burrow','burst'].includes(enemy.attack);
  warningRing.visible=warn&&radial;warningPlane.visible=warn&&!radial;
  if(warningRing.visible){const r=enemy.attack==='pounce'?.85:enemy.reach+.25;const d=enemy.attack==='pounce'?Math.min(enemy.lockLength,enemy.reach):0;warningRing.position.set(enemy.attack==='burrow'?enemy.mark.x:enemy.x+enemy.lock[0]*d,.027,enemy.attack==='burrow'?enemy.mark.z:enemy.z+enemy.lock[1]*d);warningRing.scale.setScalar(enemy.attack==='burrow'?.93:r);}
  if(warningPlane.visible){const d=enemy.reach;warningPlane.position.set(enemy.x+enemy.lock[0]*d/2,.03,enemy.z+enemy.lock[1]*d/2);warningPlane.rotation.z=face(...enemy.lock);warningPlane.scale.set(enemy.attack==='beam'?1.16:1.48,d,1);}
  impact=Math.max(0,impact-dt);flash.visible=impact>0;flash.scale.setScalar(1+(.26-impact)*2);flash.material.opacity=impact/.26*.8;
  attackRing.visible=!!p.slash&&Math.abs(p.slash.time-p.slash.weapon.wind)<.075;
  if(attackRing.visible){attackRing.position.set(p.x,.04,p.z);attackRing.rotation.z=-face(...p.face)+Math.PI/2;attackRing.scale.setScalar(p.slash.weapon.reach*.75);}
  const a=1-Math.exp(-dt*8);
  const z=p.z-1.70;look.lerp(goal.set(p.x,.74,z),a);
  camera.position.lerp(goal.set(p.x+.15,5.2,p.z+6.8),a);
  camera.lookAt(look);render.render(scene,camera);
 });
}catch(e){wrap.dataset.state='error';set(notice,'Forge Yard could not load. WebGL and served assets are required.');console.error(e);}
