import assert from 'node:assert/strict';
import {readFileSync,realpathSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire,registerHooks} from 'node:module';
import {dirname,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {readDecodedScenes} from '../sword-presentation/rig-reader.mjs';
import {configure} from './reference-adapter.mjs';
import {jackWarning} from './visibility.mjs';

const root=realpathSync(process.argv[2]),dep=createRequire(join(realpathSync(process.argv[3]),'package.json'));
const threeDir=dirname(dirname(dep.resolve('three')));
const uri=pathToFileURL(root+'/').href, adapter=new URL('./reference-adapter.mjs',import.meta.url).href;
const threeURL=pathToFileURL(join(threeDir,'build/three.module.js')).href;
const pins={
  'src/entities/robots/common.ts':'c97ff8bfb5bb69dc294fe483f6b5d6b2b5423bb0',
  'src/entities/robots/pallet.ts':'435541419aaa801b9d81b23742eb4ab60093ac44',
  'src/entities/robots/types.ts':'568bc35a85e59872aedb1da7c51f1dc9a15b04df',
  'src/core/util.ts':'1737fa575a6bb8c6c684ce2cde5b8541402d27f3',
  'src/systems/warn.ts':'c5d0edf8e6a6d3cf77a010d62b7f2a1b5de1af02',
  'src/data/enemies.ts':'345d524891aa9d022a8c51bddc8c802ad05cc251',
  'public/models/pallet.glb':'9603f6c37b94a49904f017c7ee1cd917cab36cf3'
};
for(const [p,sha] of Object.entries(pins)){
  const b=readFileSync(join(root,p));
  assert.equal(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex'),sha,p);
}
registerHooks({resolve(s,c,next){
  if(c.parentURL?.startsWith(uri)){
    if(s==='three')return next(threeURL,c);
    if(s.startsWith('.')&&!s.endsWith('.ts')){
      const dst=new URL(s,c.parentURL).href;
      return next(/\/gfx\/(geo|models|material|textures|vfx\/tells)$/.test(dst)?adapter:dst+'.ts',c);
    }
  }
  return next(s,c);
}});
const THREE=await import(threeURL);
const {clone}=await import(pathToFileURL(dep.resolve('three/addons/utils/SkeletonUtils.js')).href);
const {pallet}=await readDecodedScenes({pallet:join(root,'public/models/pallet.glb')},
  name=>import(pathToFileURL(dep.resolve(name)).href),threeDir);
// Instantiate stores only one rig per trial. Clone skin and bind hierarchy
// before passing in a fixture so each variant begins with the same pose.
const {makePallet}=await import(uri+'src/entities/robots/pallet.ts');
const {WindupArrows}=await import(uri+'src/systems/warn.ts');
const {ENEMIES}=await import(uri+'src/data/enemies.ts');
const charge=ENEMIES.pallet.attacks.find(a=>a.id==='charge');
assert.deepEqual([charge.windup,charge.active,charge.recover,charge.width,charge.length],[.95,.75,1.1,2.2,14]);
const W=402,H=874;globalThis.innerWidth=W;globalThis.innerHeight=H;
const v=(x,y,z)=>new THREE.Vector3(x,y,z), round=n=>+n.toFixed(4);
const dt=1/60;
function box(lo,hi){return new THREE.Box3(v(...lo),v(...hi));}
function dom(){
  const create=()=>({style:{},children:[],appendChild(n){this.children.push(n);}});
  const body=create();
  globalThis.document={body,createElement:create};
  return ()=>body.children.some(r=>r.children.some(n=>n.style.display==='block'));
}
function stats(ok){return {bodyFrames:ok.filter(f=>f.bodyVisible).length,laneFrames:ok.filter(f=>f.laneVisible).length,
  nativeArrowFrames:ok.filter(f=>f.nativeArrow).length,
  supplementalFrames:ok.filter(f=>f.proposed==='hidden-charge').length};}
function run(cfg){
  configure(clone(pallet),THREE);
  const rig=makePallet({variant:'normal',scale:1});
  const cam=new THREE.PerspectiveCamera(64,W/H,.05,100);
  cam.position.set(0,3.08,5.78);
  cam.lookAt(cfg.lookX??0,1.9,cfg.lookZ??0);
  cam.updateMatrixWorld();cam.updateProjectionMatrix();
  const getNative=dom();
  const mob={kind:'pallet',cls:'normal',alive:true,aggro:true,isBoss:false,state:'windup',
    atk:charge,stT:0,rig,pos:v(0,0,-cfg.dist),height:rig.height,radius:rig.radius,lift:0,fly:0,
    center(out){return out.set(this.pos.x,this.pos.y+this.height*.55,this.pos.z)},windupOf(a){return a.windup}};
  const player={pos:v(0,0,0),dead:false};
  const game={player,mobs:{list:[mob]},fx:{cam:cam.position},camera:cam,cameraRig:{cine:null},time:0};
  const native=new WindupArrows(game);
  const visible=p=>{
    const n=p.clone().project(cam);
    if(n.z< -1||n.z>1||Math.abs(n.x)>.93||Math.abs(n.y)>.93)return false;
    const diff=p.clone().sub(cam.position),ray=new THREE.Ray(cam.position,diff.clone().normalize());
    // Ray geometry only: these boxes are not entered into a physics engine.
    return !cfg.boxes.some(b=>{
      const s=ray.intersectBox(b,v(0,0,0));
      return s && s.distanceTo(cam.position)<diff.length()-.02;
    });
  };
  const refs={},trace=[];
  const pose=(action,t,time,speed=0)=>({action,t,time,speed,aimYaw:0,aimPitch:0,
    charge:action==='windup'?t:action==='attack2'?1-t:0,damage:0,status:null,cue:'charge'});
  const update=(action,t,time,speed=0)=>{
    rig.update(dt,pose(action,t,time,speed));
    rig.root.updateMatrixWorld(true);
    const head=rig.sockets.head.getWorldPosition(v(0,0,0)),fork=rig.sockets.muzzle.getWorldPosition(v(0,0,0));
    return {head,fork};
  };
  rig.root.position.copy(mob.pos);
  for(let f=-18;f<0;f++)update('move',0,f*dt,3.6);
  refs.move=update('move',.5,0,3.6).fork.toArray().map(round);
  for(let f=0;f<57;f++){
    const time=f*dt,t=time/charge.windup;
    // First-encounter geometry starts after sight/aggression; lane points
    // toward the hero. An actual charge selector/wall response is not run.
    const {head,fork}=update('windup',t,time);
    mob.pose={t};mob.stT=time;game.time=time;
    native.update();
    const nativeArrow=getNative();
    const bodyVisible=visible(head)||visible(fork);
    const floor=[];
    for(const m of [2,4,6,8,10,12]) for(const x of [-.9,0,.9])floor.push(v(x,.07,m-cfg.dist));
    const laneSamples=floor.filter(visible).length;
    // Three visible sample points is a fixture cutoff, not a measured
    // human readability threshold. Keep the raw sample count for review.
    const laneVisible=laneSamples>=3;
    const proposed=jackWarning({tick:f,currentTick:f,windup:true,threatReachesPlayer:cfg.reaches,
      nativeArrow,bodyVisible,laneVisible,tested:true});
    trace.push({ms:round(time*1000),laneSamples,bodyVisible,laneVisible,nativeArrow,proposed});
    if([0,12,40,56].includes(f))refs['windup'+f]={head:head.toArray().map(round),fork:fork.toArray().map(round),emit:round(rig.mat.emitMul.value)};
  }
  for(const [a,len,speed] of [['attack2',.75,18],['recover',1.1,0],['stagger',.25,0],['death',1.1,0]]){
    for(let f=1;f<=Math.round(len*60);f++){
      game.time+=dt;
      const p=update(a,f/Math.round(len*60),game.time,speed);
      if(f===Math.round(len*30))refs[a]={head:p.head.toArray().map(round),fork:p.fork.toArray().map(round),emit:round(rig.mat.emitMul.value)};
    }
  }
  return {id:cfg.id,dist:cfg.dist,fixtureReaches:cfg.reaches,summary:stats(trace),poses:refs,samples:[0,12,40,56].map(j=>trace[j])};
}
const configs=[
  {id:'12m-open',dist:12,reaches:true,boxes:[]},
  {id:'12m-crate-corner',dist:12,reaches:true,boxes:[box([-2.2,0,-8.2],[.5,2.4,-6.4])]},
  {id:'12m-bordered-no-sight-clear-hazard',dist:12,reaches:true,boxes:[box([-2.5,0,-2],[2.5,3,1.2])]},
  {id:'12m-full-cover-blocked-lane',dist:12,reaches:false,boxes:[box([-2.5,0,-2],[2.5,3,1.2])]},
  {id:'12m-turned-away',dist:12,reaches:true,lookX:12,lookZ:5.78,boxes:[]},
  {id:'7m-open',dist:7,reaches:true,boxes:[]}
];
const cases=configs.map(run);
assert.deepEqual(cases.map(({summary:s})=>s.supplementalFrames),[0,0,57,0,0,0]);
assert.equal(cases[0].summary.bodyFrames,57);
assert.equal(cases[1].summary.bodyFrames,0);
assert.equal(cases[1].summary.laneFrames,57);
assert.equal(cases[2].summary.nativeArrowFrames,0);
assert.equal(cases[4].summary.nativeArrowFrames,57);
assert.ok(cases[0].poses.windup56.emit>cases[0].poses.windup0.emit*2);
const out={source:'3afcd880b397e9703e906a7e66b42e8447e59519',pins,viewport:[W,H],hz:60,
  scope:'Actual Jack rig/socket animation and native edge warning logic; scripted state, fixed portrait camera, geometric ray boxes, no rendered HUD, collision authority or game.',
  cases};
process.stdout.write(JSON.stringify(out,null,2)+'\n');
